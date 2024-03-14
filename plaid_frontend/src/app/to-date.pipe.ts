import { Pipe, PipeTransform } from '@angular/core';
/*
 * Raise the value exponentially
 * Takes an exponent argument that defaults to 1.
 * Usage:
 *   value | exponentialStrength:exponent
 * Example:
 *   {{ 2 | exponentialStrength:10 }}
 *   formats to: 1024
*/
@Pipe({
    standalone: true,
    name: 'toDate'
})
export class ToDatePipe implements PipeTransform {
    transform(utc: number): string {
        return new Date(utc).toISOString().split('T')[0]
    }
}