import { Component, OnInit } from '@angular/core';
import { Transaction } from '../transaction';
import { ApiService } from '../api.service';
import { Category } from '../category';

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

  startMonth: string = ""
  startYear: string = ""
  endMonth: string = ""
  endYear: string = ""

  constructor(public apiClient: ApiService) { }

  ngOnInit(): void {
    let today = new Date()
    // today.setMonth(today.getMonth() - 1)
    this.endMonth = (today.getMonth() + 1).toString() // indexed at 0
    this.endYear = today.getFullYear().toString()

    this.startMonth = (today.getMonth() + 1).toString() // javascript thinks january is 0
    this.startYear = today.getFullYear().toString()
    this.callAPIForMainResponse()
  }

  updateVariables(updatedTransactions: Transaction[]) {
    updatedTransactions = updatedTransactions.filter(tr => tr['include_in_calc'] == true)
    this.transactions = updatedTransactions
    this.calculateSums()
  }

  callAPIForMainResponse() {
    this.apiClient.getMainResponse(`${this.startYear}-${this.startMonth}`, `${this.endYear}-${this.endMonth}`).subscribe(
      response => {
        this.allTransactions = JSON.parse(response.transactions)
        this.transactions = this.allTransactions
        this.numberOfDays = response.numberOfDays
        this.compareCategories = JSON.parse(response.compareCategories)

        this.transactions.sort((a, b) => a.authorized_date - b.authorized_date)

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
