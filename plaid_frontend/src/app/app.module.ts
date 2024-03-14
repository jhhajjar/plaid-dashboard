import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { AppComponent } from './app.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ToolbarComponent } from './toolbar/toolbar.component';
import { ApiService } from './api.service';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { NetworthComponent } from './networth/networth.component';
import { NgChartsModule } from 'ng2-charts';
import { MatCardModule } from '@angular/material/card';
import { TableComponent } from './table/table.component';
import { MatTableModule } from '@angular/material/table';
import { ToDatePipe } from './to-date.pipe';
import { CategoriesComponent } from './categories/categories.component';
import { IncomebydayComponent } from './incomebyday/incomebyday.component';
import { SpendingbydayComponent } from './spendingbyday/spendingbyday.component';
import { NetbydayComponent } from './netbyday/netbyday.component';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    ToolbarComponent,
    NetworthComponent,
    TableComponent,
    CategoriesComponent,
    IncomebydayComponent,
    SpendingbydayComponent,
    NetbydayComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    NgxChartsModule,
    HttpClientModule,
    FormsModule,
    MatButtonModule,
    MatSelectModule,
    MatInputModule,
    MatFormFieldModule,
    MatDatepickerModule,
    ReactiveFormsModule,
    NgChartsModule,
    MatCardModule,
    MatTableModule,
    ToDatePipe
  ],
  providers: [
    ApiService,
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
