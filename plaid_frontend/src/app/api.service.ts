import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Transaction } from './transaction';
import { MainResponse } from './mainResponse';

@Injectable({
    providedIn: 'root'
})
export class ApiService {

    constructor(
        private httpClient: HttpClient
    ) { }

    backendURL = "http://plaid-dashboard-production.up.railway.app"

    getMainResponse(start: string, end: string = ""): Observable<MainResponse> {
        let url = end != "" ? `${this.backendURL}/getData?start=${start}&end=${end}` : `${this.backendURL}/getData?start=${start}`
        let mainResponse = this.httpClient.get<MainResponse>(url)
        return mainResponse
    }

    postTransaction(newJob: Transaction): Observable<Transaction> {
        return this.httpClient.post<Transaction>(`${this.backendURL}/updateJob`, newJob)
    }
}
