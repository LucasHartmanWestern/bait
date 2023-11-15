import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AccountComponent } from "./account/account.component";
import { LoginComponent } from "./login/login.component";
import { SplashPageComponent } from "./splash-page/splash-page.component";

const routes: Routes = [{
  path: 'user', component: AccountComponent, data: { title: 'User'}
}, {
  path: 'login', component: LoginComponent, data: { title: 'Login'}
}, {
  path: '', component: SplashPageComponent, data: { title: 'Home'}
}];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
