import { Component, Input, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-incomebyday',
  templateUrl: './incomebyday.component.html',
  styleUrls: ['./incomebyday.component.css']
})
export class IncomebydayComponent {
  @Input() dataObject: any = {}
  income: number = 0
  numDays: number = 1
  display: string = ""

  ngOnChanges(changes: SimpleChanges): void {
    this.income = this.dataObject['income']
    this.numDays = this.dataObject['numberOfDays']
    this.display = (this.income / this.numDays).toFixed(2)
  }
}
