import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'bait';

  page: string | undefined = 'Main';

  onNavPageChange(newPage: string) {
    this.page = newPage;
  }
}
