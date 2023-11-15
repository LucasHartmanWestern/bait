import { Component } from '@angular/core';

@Component({
  selector: 'app-account',
  templateUrl: './account.component.html',
  styleUrls: ['./account.component.scss']
})
export class AccountComponent {

  constructor() {
    document.addEventListener('DOMContentLoaded', function() {
      const carousel = document.querySelector('.carousel');
      const cards = document.querySelectorAll('.card');
      let scrollAmount = 0;

      const cardWidth = cards[0].clientWidth;
      const gap = 24; // Assuming a gap of 24px; adjust as per your design

      document.querySelector('.carousel-control.right')?.addEventListener('click', () => {
        if (carousel) carousel.scrollLeft += cardWidth + gap;
      });

      document.querySelector('.carousel-control.left')?.addEventListener('click', () => {
        if (carousel) carousel.scrollLeft -= cardWidth + gap;
      });
    });
  }


}
