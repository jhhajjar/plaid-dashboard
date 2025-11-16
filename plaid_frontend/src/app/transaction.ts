export interface Transaction {
    transactionId: string,
    date: number,
    authorized_date: number,
    name: string,
    merchantName: string,
    plaid_categories: string[],
    category: string,
    amount: number,
    includeInCalc: boolean
}