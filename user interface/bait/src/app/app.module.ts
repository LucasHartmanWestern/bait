import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AccountComponent } from './account/account.component';
import { SplashPageComponent } from './splash-page/splash-page.component';
import { LoginComponent } from './login/login.component';
import { NavbarComponent } from './navbar/navbar.component';
import { PluginComponent } from './plugin/plugin.component';

@NgModule({
  declarations: [
    AppComponent,
    AccountComponent,
    SplashPageComponent,
    LoginComponent,
    NavbarComponent,
    PluginComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
