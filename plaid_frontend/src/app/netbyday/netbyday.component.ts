import { Component, Input, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-netbyday',
  templateUrl: './netbyday.component.html',
  styleUrls: ['./netbyday.component.css']
})
export class NetbydayComponent {
  @Input() dataObject: any = {}
  net: number = 0
  numDays: number = 1
  display: string = ""

  ngOnChanges(changes: SimpleChanges): void {
    this.net = this.dataObject['net']
    this.numDays = this.dataObject['numberOfDays']
    this.display = (this.net / this.numDays).toFixed(2)
  }
}