import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from "@angular/common/http";
import { catchError, map, Observable, throwError } from "rxjs";
import { Constants } from "../constants/constants";

@Injectable({
  providedIn: 'root'
})
export class MessageService {

  httpHeaders = new HttpHeaders({
    'Authorization': 'Bearer ' + localStorage.getItem('token') || 'N/A'
  });

  constructor(private http: HttpClient) { }

  sendMessage(messages: any, queryImage: string | ArrayBuffer | null): Observable<any> {
    let body: any = { messages: messages.filter((message: any) => {
        return (message?.sendAPI != false);
      }) }
    if (queryImage) body['queryImage'] = queryImage;

    return this.http.post<any>(`${Constants.apiPaths.sendMessage}`, body, {headers: this.httpHeaders}).pipe(
      map((data: FormData) => data),
      catchError(this.handleError)
    );
  }

  // Handle errors
  private handleError(err: HttpErrorResponse) {
    let errorMessage = '';
    if (err.error instanceof ErrorEvent) {

      errorMessage = `An error occurred: ${err.error.message}`;
    } else {

      errorMessage = `Server returned code: ${err.status}, error message is: ${err.message}`;
    }
    return throwError(err.error);
  }
}
