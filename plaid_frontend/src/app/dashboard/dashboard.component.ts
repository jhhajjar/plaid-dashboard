import { Component, OnInit } from '@angular/core';
import { Transaction } from '../transaction';
import { ApiService } from '../api.service';
import { Category } from '../category';
import { MONTHS, YEARS, Option } from '../constants';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  allTransactions: Transaction[] = []
  transactions: Transaction[] = []
  numberOfDays: number = 1
  compareCategories: Category[] = []
  incomeDataObject: any = {}
  spendingDataObject: any = {}
  netDataObject: any = {}

  years: Option[] = []
  months: Option[] = MONTHS

  startMonth: number = 0
  startYear: number = 0
  endMonth: number = 0
  endYear: number = 0

  constructor(public apiClient: ApiService) { }

  ngOnInit(): void {
    // set default start and end dates to today
    let today = new Date()
    this.endMonth = today.getMonth() + 1 // indexed at 0
    this.endYear = today.getFullYear()
    this.startMonth = today.getMonth() + 1 // javascript thinks january is 0
    this.startYear = today.getFullYear()

    // fill out options (2021 to current year)
    this.years = YEARS(today.getFullYear())
    this.callAPIForMainResponse()
  }

  setEndDate() {
    if (this.startYear > this.endYear) {
      this.endYear = this.startYear
    } else if (this.startYear == this.endYear && this.startMonth > this.endMonth) {
      this.endMonth = this.startMonth
    }
  }

  setStartDate() {
    console.log(this.startYear == this.endYear)
    console.log(this.startMonth, this.endMonth, this.startMonth > this.endMonth)
    if (this.startYear > this.endYear) {
      this.startYear = this.endYear
    } else if (this.startYear == this.endYear && this.startMonth > this.endMonth) {
      this.startMonth = this.endMonth
    }
  }

  updateVariables(updatedTransactions: Transaction[]) {
    updatedTransactions = updatedTransactions.filter(tr => tr['includeInCalc'] == true)
    this.transactions = updatedTransactions
    this.calculateSums()
  }

  callAPIForMainResponse() {
    this.apiClient.getMainResponse(`${this.startYear}-${this.startMonth}`, `${this.endYear}-${this.endMonth}`).subscribe(
      response => {
        this.allTransactions = response.transactions
        this.transactions = this.allTransactions

        this.calculateSums()
      }
    )
  }

  calculateSums() {
    let income = this.transactions.filter(function (tr) { return tr.category == "Income" }).reduce((acc, curr) => acc + curr.amount, 0)
    let spending = this.transactions.filter(function (tr) { return tr.amount < 0 }).reduce((acc, curr) => acc + curr.amount, 0)
    let net = this.transactions.reduce((acc, curr) => acc + curr.amount, 0)

    this.incomeDataObject = { "income": income, "numberOfDays": this.numberOfDays }
    this.spendingDataObject = { "spending": spending, "numberOfDays": this.numberOfDays }
    this.netDataObject = { "net": net, "numberOfDays": this.numberOfDays }
  }

  applyFilters() {
    this.callAPIForMainResponse()
  }
}
