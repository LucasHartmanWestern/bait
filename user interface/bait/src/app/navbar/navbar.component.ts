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

  navigate(value: string) {
    localStorage.setItem('page', value);
    this._navPage = value;
    this.navPage.emit(this._navPage);
  }

  logout(): void {
    localStorage.setItem('page', 'Login');
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('password');
    this.navigate('Login')
  }

  login(): void {
    localStorage.setItem('page', 'Login');
    this.navigate('Login')
  }
}
