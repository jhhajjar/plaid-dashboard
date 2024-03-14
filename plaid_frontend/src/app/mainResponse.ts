import { Transaction } from "./transaction";

export interface MainResponse {
    transactions: string,
    numberOfDays: number,
    categories: string,
    compareCategories: string
}