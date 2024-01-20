import pandas as pd
import numpy as np
import calendar
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta


class TransactionSet:
    def __init__(self, start, end=None) -> None:
        self.full_df = pd.read_csv('./all_transactions.csv')
        self.full_df['date'] = pd.to_datetime(self.full_df['date'])
        self.full_df['authorized_date'] = pd.to_datetime(
            self.full_df['authorized_date'])

        self.start = self._format_date(start)
        if end is not None:
            self.end = self._format_date(end)
        else:
            today = dt.today()
            self.end = self._format_date(f'{today.year}-{today.month:02}')

        self.df = self._apply_temporal_filter(start, end)
        self.number_of_days = (dt(self.end.year, self.end.month, calendar.monthrange(
            self.end.year, self.end.month)[1]) - dt(self.start.year, self.start.month, 1)).days

    def _format_date(self, date_str):
        return dt.strptime(date_str, '%Y-%m')

    def _apply_temporal_filter(self, start, end=None) -> pd.DataFrame:
        """
        Puts a filter on the transactions dataframe. If end is not provided, end is current month

        Args:
        start:  datetime.date
        end:    datetime.date, default None
        """
        temporal_filter_df = self.full_df.copy()
        temporal_filter_df = temporal_filter_df[temporal_filter_df['authorized_date'] >= start]
        if end is not None:
            # get last day of this month
            _, last_day = calendar.monthrange(end.year, end.month)
            end = dt(end.year, end.month, last_day)
        else:
            end = dt.today().strftime('%Y-%m-%d')

        temporal_filter_df = temporal_filter_df[temporal_filter_df['authorized_date'] <= end]

        temporal_filter_df.sort_values(by=['authorized_date'], inplace=True)
        return temporal_filter_df

    def get_historical_networth(self) -> pd.DataFrame:
        """
        Gets the networth line chart over time. Takes a cumulative sum of all transactions.
        """

        ntwH = self.df.copy()
        ntwH['amount'] = ntwH['amount'].cumsum()
        return ntwH

    def get_most_expensive_transactions(self, n=5) -> pd.DataFrame:
        """
        Gets the most expensive transactions.

        Args:
        n:  int, default=5
        """
        return self.df.sort_values(by='amount', ascending=True).head(n)

    def group_by_categories(self):
        """
        Group by categories of transactions.
        """
        return self.df.groupby(by='category')['amount'].sum()

    def compare_categories(self):
        """
        Get the difference between what you spent on last time delta to this one
        """
        # get the difference in number of months
        month_difference = ((self.end.month + 1) - self.start.month) % 12

        # subtract that difference from the start
        comp_start_date = self.start - relativedelta(months=month_difference)
        comp_end_date = self.end - relativedelta(months=month_difference)

        comp_df = self._apply_temporal_filter(comp_start_date, comp_end_date)
        comp_categories = comp_df.groupby(by='category')['amount'].sum()
        return np.round((self.group_by_categories() - comp_categories) / comp_categories * 100, 2)

    def money_by_day(self):
        """
        Get the average amount of money that you net by day
        """
        return self.df['amount'].sum() / self.number_of_days

    def money_earned_by_day(self):
        """
        Returns the average amount of money that you earn by day
        """
        return self.df[self.df['amount'] > 0]['amount'].sum() / self.number_of_days

    def money_spent_by_day(self):
        """
        Returns the average amount of money that you spend by day
        """
        return self.df[self.df['amount'] < 0]['amount'].sum() / self.number_of_days
