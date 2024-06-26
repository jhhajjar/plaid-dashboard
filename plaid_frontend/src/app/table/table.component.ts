import { Component, EventEmitter, Input, Output, SimpleChanges } from '@angular/core';
import { Transaction } from '../transaction';

@Component({
  selector: 'app-table',
  templateUrl: './table.component.html',
  styleUrls: ['./table.component.css']
})
export class TableComponent {
  // json string of the transactions df
  @Input() data: Transaction[] = []
  @Output() transactionsChange: EventEmitter<Transaction[]> = new EventEmitter<Transaction[]>()

  jsonData: Transaction[] = []
  jsonDataBackup: Transaction[] = []
  displayedColumns = ['date', 'name', 'category', 'amount', 'included']
  filterOptions: string[] = ["All"]
  selectedValue: string = "All"

  ngOnChanges(changes: SimpleChanges): void {
    this.jsonData = this.data
    this.jsonDataBackup = this.jsonData
    this.getCategories()
  }

  applyTableFilter() {
    if (this.selectedValue == "All") {
      this.jsonData = this.jsonDataBackup
    } else {
      this.jsonData = this.jsonDataBackup.filter(tr => tr.category == this.selectedValue)
    }
  }

  changeValue() {
    this.transactionsChange.emit(this.jsonData)
  }

  getCategories() {
    this.filterOptions = ["All", ...new Set(this.jsonData.map(tr => tr.category))]
  }
}
