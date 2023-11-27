import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { UserService } from "../services/user.service";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {

  constructor(private router: Router, private userService: UserService) {
  }

  ngOnInit(): void {
    let user = localStorage.getItem('username');
    let pass = localStorage.getItem('password');

    if (user && pass) this.login(null, user, pass, true);
  }

  errorMsg: string | null = null;

  register(username: string, password: string): void {
    this.userService.register(username, password).subscribe(res => {
      this.login(null, username, password, true);
    });
  }

  login(event: any, username: string, password: string, remember: boolean): void {
    event?.preventDefault();

    if (username && password) {

      this.userService.login(username, password).subscribe(res => {

        localStorage.setItem('token', res['access_token']);

        if (remember) {
          localStorage.setItem('username', username);
          localStorage.setItem('password', password)
        }

        this.router.navigate(['user']);
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
