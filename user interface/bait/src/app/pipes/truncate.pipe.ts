import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'truncate'
})
export class TruncatePipe implements PipeTransform {
  transform(value: string, limit: number = 20, completeWords: boolean = false, ellipsis: string = '...'): string {
    if (value.length <= limit) {
      return value;
    }

    const subString = value.substr(0, limit);
    return (completeWords ? subString.substr(0, subString.lastIndexOf(' ')) : subString) + ellipsis;
  }
}
