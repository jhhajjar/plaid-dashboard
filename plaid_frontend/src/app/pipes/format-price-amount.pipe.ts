import { Pipe, PipeTransform } from "@angular/core";

@Pipe({
    standalone: true,
    name: 'formatPriceAmount'
})
export class FormatPriceAmount implements PipeTransform {
    transform(value: number) {
        const transformedValue = value < 0 ? -value : value
        const prefix = value < 0 ? '-' : ''
        return `${prefix}$${transformedValue.toLocaleString('en', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`
    }
}