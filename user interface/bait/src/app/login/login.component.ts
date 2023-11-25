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

  login(event: any): void {
    event.preventDefault();

    console.log(event);

    this.userService.login("username1", "password1").subscribe(res => {
      console.log(res);
    }, error => {
      console.log(error);
    });

    //this.router.navigate(['user']);
  }

  register(): void {

  }

}
