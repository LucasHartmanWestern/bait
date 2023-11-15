import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AccountComponent } from "./account/account.component";
import { LoginComponent } from "./login/login.component";
import { SplashPageComponent } from "./splash-page/splash-page.component";

const routes: Routes = [{
  path: 'user', component: AccountComponent
}, {
  path: 'login', component: LoginComponent
}, {
  path: '', component: SplashPageComponent
}];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
