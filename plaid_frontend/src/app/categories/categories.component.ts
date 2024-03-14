import { Component, Input, SimpleChanges, ViewChild } from '@angular/core';
import { Transaction } from '../transaction';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartData, ChartType } from 'chart.js';
import { Category } from '../category';
import { isNgTemplate } from '@angular/compiler';

@Component({
  selector: 'app-categories',
  templateUrl: './categories.component.html',
  styleUrls: ['./categories.component.css']
})
export class CategoriesComponent {
  @Input() data: Category[] = []

  chartOptions: any = {}
  chartData: any = {}
  chartType: ChartType = 'bar';

  ngOnChanges(changes: SimpleChanges): void {
    this.makePieChart()
  }

  makePieChart() {
    this.chartOptions = {
      scales: {
        y: {
          ticks: {
            color: '#ffffff'
          }
        },
        x: {
          ticks: {
            color: '#ffffff'
          }
        }
      },
    }
    this.chartData = {
      labels: this.data.map(item => item.category),
      datasets: [
        {
          data: this.data.map(item => item.amount),
        },
      ],
    };
  }

}
