import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  Customer,
  InventoryItem,
  PaginatedResponse,
  PurchaseOrder,
  PurchaseOrderDetail,
  SalesOrder,
  SalesOrderDetail,
  Vendor,
} from '../models/erp.model';

@Injectable({
  providedIn: 'root',
})
export class ErpDataService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = '/api/v1';

  private paginationParams(limit: number, offset: number): HttpParams {
    return new HttpParams()
      .set('limit', limit)
      .set('offset', offset);
  }

  listSales(
    limit = 20,
    offset = 0,
    startDate?: string,
    endDate?: string,
  ): Observable<PaginatedResponse<SalesOrder>> {
    let params = this.paginationParams(limit, offset);

    if (startDate) params = params.set('start_date', startDate);
    if (endDate) params = params.set('end_date', endDate);

    return this.http.get<PaginatedResponse<SalesOrder>>(
      `${this.apiUrl}/sales`,
      { params },
    );
  }

  getSales(orderId: number): Observable<SalesOrderDetail> {
    return this.http.get<SalesOrderDetail>(
      `${this.apiUrl}/sales/${orderId}`,
    );
  }

  listPurchases(
    limit = 20,
    offset = 0,
    startDate?: string,
    endDate?: string,
  ): Observable<PaginatedResponse<PurchaseOrder>> {
    let params = this.paginationParams(limit, offset);

    if (startDate) params = params.set('start_date', startDate);
    if (endDate) params = params.set('end_date', endDate);

    return this.http.get<PaginatedResponse<PurchaseOrder>>(
      `${this.apiUrl}/purchases`,
      { params },
    );
  }

  getPurchase(orderId: number): Observable<PurchaseOrderDetail> {
    return this.http.get<PurchaseOrderDetail>(
      `${this.apiUrl}/purchases/${orderId}`,
    );
  }

  listInventory(
    limit = 20,
    offset = 0,
    lowStockOnly = false,
  ): Observable<PaginatedResponse<InventoryItem>> {
    const params = this.paginationParams(limit, offset)
      .set('low_stock_only', lowStockOnly);

    return this.http.get<PaginatedResponse<InventoryItem>>(
      `${this.apiUrl}/inventory`,
      { params },
    );
  }

  getInventoryItem(itemId: number): Observable<InventoryItem> {
    return this.http.get<InventoryItem>(
      `${this.apiUrl}/inventory/${itemId}`,
    );
  }

  listVendors(
    limit = 20,
    offset = 0,
  ): Observable<PaginatedResponse<Vendor>> {
    const params = this.paginationParams(limit, offset);

    return this.http.get<PaginatedResponse<Vendor>>(
      `${this.apiUrl}/vendors`,
      { params },
    );
  }

  getVendor(vendorId: number): Observable<Vendor> {
    return this.http.get<Vendor>(
      `${this.apiUrl}/vendors/${vendorId}`,
    );
  }

  listCustomers(
    limit = 20,
    offset = 0,
  ): Observable<PaginatedResponse<Customer>> {
    const params = this.paginationParams(limit, offset);

    return this.http.get<PaginatedResponse<Customer>>(
      `${this.apiUrl}/customers`,
      { params },
    );
  }

  getCustomer(customerId: number): Observable<Customer> {
    return this.http.get<Customer>(
      `${this.apiUrl}/customers/${customerId}`,
    );
  }
}