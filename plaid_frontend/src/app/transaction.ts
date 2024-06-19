export interface Transaction {
    transactionID: string,
    date: number,
    authorized_date: number,
    name: string,
    merchant_name: string,
    plaid_categories: string[],
    category: string,
    amount: number,
    include_in_calc: boolean
}