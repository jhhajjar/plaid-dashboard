import pandas as pd
import numpy as np
import calendar
import os
import boto3
from dateutil.relativedelta import relativedelta
from flask_cors import CORS
from aws_utils import read_file_s3
from datetime import datetime as dt
from dotenv import load_dotenv
from flask import Flask, jsonify, request

app = Flask(__name__)
CORS(app)
full_df = read_file_s3('demo_ledger.csv')


def _apply_temporal_filter(start, end=None):
    """
    Puts a filter on the transactions dataframe. If end is not provided, end is current month

    Args:
    start:  datetime.date
    end:    datetime.date, default None
    """
    temporal_filter_df = full_df.copy()
    temporal_filter_df = temporal_filter_df[temporal_filter_df['authorized_date'] >= pd.to_datetime(
        start)]
    if end is not None:
        # get last day of this month
        _, last_day = calendar.monthrange(end.year, end.month)
        end = dt(end.year, end.month, last_day)
    else:
        end = dt.today().strftime('%Y-%m-%d')

    temporal_filter_df = temporal_filter_df[temporal_filter_df['authorized_date'] <= pd.to_datetime(
        end)]

    temporal_filter_df.sort_values(by=['authorized_date'], inplace=True)
    return temporal_filter_df


def _format_date(date_str):
    return dt.strptime(date_str, '%Y-%m').date()


def compare_categories(df, start, end=None) -> pd.DataFrame:
    """
    Get the difference between what you spent on last time delta to this one
    """
    # get the difference in number of months
    month_difference = ((end.month + 1) - start.month) % 12

    # subtract that difference from the start
    comp_start_date = start - relativedelta(months=month_difference)
    comp_end_date = end - relativedelta(months=month_difference)

    comp_df = _apply_temporal_filter(comp_start_date, comp_end_date)
    comp_categories = comp_df.groupby(by='category')['amount'].sum()
    percs = (df.groupby(by='category')['amount'].sum() - comp_categories) / \
        comp_categories * 100
    return percs


def remove_CD(df) -> pd.DataFrame:
    name_condition = (df['name'] == 'DEBIT') | (
        df['name'] == 'WITHDRAWAL') | (df['name'] == 'DEPOSIT')
    amount_condition = abs(df['amount']) > 1000
    return df[~(name_condition & amount_condition)]


def remove_CC(df) -> pd.DataFrame:
    name_condition = (df['name'].str.lower().str.contains('td bank payment')) | (
        df['name'] == 'Recurring Automatic Payment')
    return df[~name_condition]


def apply_filter(df) -> pd.DataFrame:
    """
    Applies a filter to remove some rows from the transactions df
    """
    df = remove_CD(df)
    df = remove_CC(df)
    return df


@app.route('/getData', methods=['GET'])
def get_df():
    start = request.args.get('start')
    end = request.args.get('end')

    full_df['date'] = pd.to_datetime(full_df['date'])
    full_df['authorized_date'] = pd.to_datetime(
        full_df['authorized_date'])

    today = -1
    start = _format_date(start)
    if end is not None:
        end = _format_date(end)
    else:
        today = dt.today()
        end = _format_date(f'{today.year}-{today.month:02}')

    # transactions
    df = _apply_temporal_filter(start, end)
    # number of days
    if today != -1:
        number_of_days = (dt(today.year, today.month, today.day) -
                          dt(start.year, start.month, start.day)).days
    else:
        last_day_of_month = calendar.monthrange(end.year, end.month)[1]
        number_of_days = (
            dt(end.year, end.month, last_day_of_month) - dt(start.year, start.month, 1)).days

    # apply filter
    df = apply_filter(df)

    # categories
    categories = df.groupby(by='category')['amount'].sum().sort_values()
    categories = categories.drop('Income')

    json_response = {
        'transactions': df.to_json(orient='records'),
        'numberOfDays': number_of_days,
        'categories': categories.reset_index().to_json(orient='records'),
        'compareCategories': compare_categories(df, start, end).reset_index().to_json(orient='records')
    }

    return json_response


app.run()
