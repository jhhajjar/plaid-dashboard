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
    let grouped = this.data.reduce((acc: { [key: string]: number }, val) => {
      if (val.category === "Income") {
        return acc
      }
      if (!acc[val.category]) {
        acc[val.category] = 0
      }
      acc[val.category] += val.amount
      return acc
    }, {})
    let result = Object.keys(grouped).map((category) => ({
      category,
      amount: grouped[category]
    }))
    result = result.sort((a, b) => a.category.localeCompare(b.category))
    this.makePieChart(result)
  }

  makePieChart(data: { category: string, amount: number }[]) {
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
      labels: data.map(item => item.category),
      datasets: [
        {
          data: data.map(item => item.amount),
        },
      ],
    };
  }

}
