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
  transactions: Transaction[] = []
  numberOfDays: number = 1
  categories: Category[] = []
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
    today.setMonth(today.getMonth() - 3)
    this.endMonth = (today.getMonth() + 1).toString() // indexed at 0
    this.endYear = today.getFullYear().toString()

    // today.setMonth(today.getMonth() - 1)
    this.startMonth = (today.getMonth() + 1).toString() // javascript thinks january is 0
    this.startYear = today.getFullYear().toString()
    this.callAPIForMainResponse()
  }

  callAPIForMainResponse() {
    this.apiClient.getMainResponse(`${this.startYear}-${this.startMonth}`, `${this.endYear}-${this.endMonth}`).subscribe(
      response => {
        this.transactions = JSON.parse(response.transactions)
        this.numberOfDays = response.numberOfDays
        this.categories = JSON.parse(response.categories)
        this.compareCategories = JSON.parse(response.compareCategories)

        this.transactions.sort((a, b) => a.authorized_date - b.authorized_date)
        // console.log(this.transactions.length)
        // this.transactions = this.transactions.filter(tr => (!tr.name.toLowerCase().includes("td bank payment")) && (!tr.name.toLowerCase().includes("recurring automatic payment")))
        // console.log(this.transactions.length)
        // TODO: categories is being populated from the backend, so we cannot really affect it with the filters. need to figure oout how to change that

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
