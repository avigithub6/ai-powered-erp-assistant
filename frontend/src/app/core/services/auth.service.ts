import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, catchError, map, of, switchMap, tap, throwError } from 'rxjs';

import { CurrentUser, LoginRequest, TokenResponse } from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly apiUrl = '/api/v1/auth';
  private readonly tokenKey = 'erp_access_token';

  private readonly userSubject = new BehaviorSubject<CurrentUser | null>(null);
  readonly user$ = this.userSubject.asObservable();

  constructor(private readonly http: HttpClient) {}

  get currentUser(): CurrentUser | null {
    return this.userSubject.value;
  }

  getToken(): string | null {
    return sessionStorage.getItem(this.tokenKey);
  }

  login(credentials: LoginRequest): Observable<CurrentUser> {
    return this.http.post<TokenResponse>(`${this.apiUrl}/login`, credentials).pipe(
      tap((response) => {
        sessionStorage.setItem(this.tokenKey, response.access_token);
      }),
      switchMap(() => this.loadCurrentUser()),
      catchError((error) => {
        this.clearSession();
        return throwError(() => error);
      })
    );
  }

  loadCurrentUser(): Observable<CurrentUser> {
    return this.http.get<CurrentUser>(`${this.apiUrl}/me`).pipe(
      tap((user) => this.userSubject.next(user))
    );
  }

  ensureAuthenticated(): Observable<boolean> {
    if (!this.getToken()) {
      return of(false);
    }

    if (this.currentUser) {
      return of(true);
    }

    return this.loadCurrentUser().pipe(
      map(() => true),
      catchError(() => {
        this.clearSession();
        return of(false);
      })
    );
  }

  logout(): void {
    this.clearSession();
  }

  private clearSession(): void {
    sessionStorage.removeItem(this.tokenKey);
    this.userSubject.next(null);
  }
}
