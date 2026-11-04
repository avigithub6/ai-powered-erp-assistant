import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { forkJoin, of } from 'rxjs';

import { AuthService } from './auth.service';
import {
  DashboardSummary,
  SalesTrend,
  TopProduct,
  TopVendor,
  PaginatedResponse,
  DashboardInventoryItem
} from '../models/dashboard.model';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);
  private readonly apiUrl = '/api/v1/dashboard';

  getDashboardData() {
    const role = this.authService.currentUser?.role;

    const canViewSales = [
      'Administrator',
      'Sales Executive',
      'Management'
    ].includes(role ?? '');

    const canViewPurchases = [
      'Administrator',
      'Purchase Executive',
      'Management'
    ].includes(role ?? '');

    return forkJoin({
      summary: this.http.get<DashboardSummary>(
        `${this.apiUrl}/summary`
      ),
      salesTrend: canViewSales
        ? this.http.get<SalesTrend[]>(`${this.apiUrl}/sales-trend`)
        : of([] as SalesTrend[]),
      topProducts: canViewSales
        ? this.http.get<TopProduct[]>(`${this.apiUrl}/top-products?limit=5`)
        : of([] as TopProduct[]),
      topVendors: canViewPurchases
        ? this.http.get<TopVendor[]>(`${this.apiUrl}/top-vendors?limit=5`)
        : of([] as TopVendor[]),
      inventory: this.http.get<PaginatedResponse<DashboardInventoryItem>>(
        `${this.apiUrl}/inventory?limit=5&offset=0`
      ),
      lowStock: this.http.get<PaginatedResponse<DashboardInventoryItem>>(
        `${this.apiUrl}/low-stock?limit=5&offset=0`
      )
    });
  }
}
