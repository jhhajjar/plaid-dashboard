import { Component, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import { Transaction } from '../transaction';
import { Chart, ChartConfiguration, ChartType } from 'chart.js';
import { BaseChartDirective } from 'ng2-charts';

@Component({
  selector: 'app-networth',
  templateUrl: './networth.component.html',
  styleUrls: ['./networth.component.css']
})
export class NetworthComponent implements OnChanges {
  // json string of the transactions df
  @Input() data: Transaction[] = []
  // chart configs
  chartData: ChartConfiguration['data'] = { datasets: [], labels: [] }
  chartLabels: string[] = []
  chartOptions: ChartConfiguration['options'] = {}
  chartType: ChartType = 'line';

  amounts: number[] = []
  dates: Date[] = []

  @ViewChild(BaseChartDirective) chart?: BaseChartDirective;

  ngOnChanges(changes: SimpleChanges): void {
    this.dates = this.data.map(item => new Date(item.authorized_date)) // utc seconds -> Date
    this.amounts = this.data.map(item => item.amount)

    this.makeLineChart()
  }

  makeLineChart() {
    let init = 0
    let cumulative = this.amounts.map(value => init += value)
    this.chartData = {
      datasets: [
        {
          data: cumulative,
          pointRadius: 0,
          label: "Amount"
        }
      ],
      labels: this.dates.map(d => d.toISOString().split('T')[0])
    }
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
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
    };
  }
}
