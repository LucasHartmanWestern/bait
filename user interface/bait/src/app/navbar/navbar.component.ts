import { Component, OnInit, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {

  _navPage: string = localStorage.getItem('page') || "Main";
  @Output() navPage = new EventEmitter<string>();

  constructor() {}

  ngOnInit(): void {
      this.navigate(localStorage.getItem('page') || 'Main');
      this._navPage = localStorage.getItem('page') || "Main";
  }

  home(): void {
    this.navigate('Main')
  }

  navigate(value: string) {
    localStorage.setItem('page', value);
    this._navPage = value;
    this.navPage.emit(this._navPage);
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('password');
    this.navigate('Login')
  }

  login(): void {
    this.navigate('Login')
  }
}
