export interface Transaction {
    transactionId: string,
    date: number,
    merchantName: string,
    category: string,
    amount: number,
    includeInCalc: boolean
}