import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Transaction } from './transaction';
import { MainResponse } from './mainResponse';
import { environment } from 'src/environments/environment';

@Injectable({
    providedIn: 'root'
})
export class ApiService {

    constructor(
        private httpClient: HttpClient
    ) { }

    backendURL = environment.BACKEND_URL

    getMainResponse(start: string, end: string = ""): Observable<MainResponse> {
        let url = end != "" ? `${this.backendURL}/transactions?start=${start}&end=${end}` : `${this.backendURL}/transactions?start=${start}`
        let mainResponse = this.httpClient.get<MainResponse>(url)
        return mainResponse
    }

    postTransaction(newJob: Transaction): Observable<Transaction> {
        return this.httpClient.post<Transaction>(`${this.backendURL}/updateJob`, newJob)
    }
}
