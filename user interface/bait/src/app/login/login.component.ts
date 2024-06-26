import { Component, EventEmitter, Output } from '@angular/core';
import { Router } from '@angular/router';
import { UserService } from "../services/user.service";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {

  @Output() navPage = new EventEmitter<string>();

  constructor(private router: Router, private userService: UserService) {
  }

  ngOnInit(): void {
    let user = localStorage.getItem('username');
    let pass = localStorage.getItem('password');

    if (user && pass) this.login(null, user, pass, true);
  }

  errorMsg: string | null = null;
  errorMsgReg: string | null = null;

  register(username: string, password: string): void {
    this.userService.register(username, password).subscribe(res => {
      this.login(null, username, password, true);
    }, error => {
      console.log(error);
      this.errorMsgReg = error.msg;
      setTimeout(() => this.errorMsgReg = null, 10000);
    });
  }

  login(event: any, username: string, password: string, remember: boolean): void {
    event?.preventDefault();

    if (username && password) {

      this.userService.login(username, password).subscribe(res => {

        this.navPage.emit('User');
        localStorage.setItem('page', 'User');

        localStorage.setItem('token', res['access_token']);

        if (remember) {
          localStorage.setItem('username', username);
          localStorage.setItem('password', password)
        }

        location.reload();
      }, error => {
        console.log(error);
        this.errorMsg = error.error;
        setTimeout(() => this.errorMsg = null, 10000);
      });
    } else {
      this.errorMsg = "Username or Password missing";
      setTimeout(() => this.errorMsg = null, 10000);
    }
  }

}
