import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-spendingbyday',
  templateUrl: './spendingbyday.component.html',
  styleUrls: ['./spendingbyday.component.css']
})
export class SpendingbydayComponent implements OnChanges {
  @Input() dataObject: any = {}
  spending: number = 0
  numDays: number = 1
  display: string = ""

  ngOnChanges(changes: SimpleChanges): void {
    this.spending = this.dataObject['spending']
    this.numDays = this.dataObject['numberOfDays']
    this.display = (this.spending / this.numDays).toFixed(2)
  }
}
