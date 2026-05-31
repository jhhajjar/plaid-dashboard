export interface Option {
  id: number;
  name: string;
}

export const MONTHS: Option[] = [
  { id: 1, name: 'January' },
  { id: 2, name: 'February' },
  { id: 3, name: 'March' },
  { id: 4, name: 'April' },
  { id: 5, name: 'May' },
  { id: 6, name: 'June' },
  { id: 7, name: 'July' },
  { id: 8, name: 'August' },
  { id: 9, name: 'September' },
  { id: 10, name: 'October' },
  { id: 11, name: 'November' },
  { id: 12, name: 'December' },
];

export const YEARS: (finalYear: number) => Option[] = (finalYear: number): Option[] => {
  const startYear = 2021;
  const years: Option[] = [];

  // Loop from the start year up to and including the final year
  for (let year = startYear; year <= finalYear; year++) {
    years.push({
      id: year,
      name: year.toString(),
    });
  }

  return years;
};