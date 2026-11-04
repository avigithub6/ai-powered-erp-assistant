import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErpDataService } from '../../core/services/erp-data.service';
import {
  PaginatedResponse,
  PurchaseOrder,
} from '../../core/models/erp.model';

@Component({
  selector: 'app-purchases',
  imports: [CommonModule],
  templateUrl: './purchases.html',
  styleUrl: './purchases.scss',
})
export class Purchases implements OnInit {
  private readonly erpService = inject(ErpDataService);

  readonly loading = signal(true);
  readonly errorMessage = signal('');
  readonly data = signal<PaginatedResponse<PurchaseOrder> | null>(null);
  readonly page = signal(0);

  readonly pageSize = 20;

  ngOnInit(): void {
    this.loadPurchases();
  }

  loadPurchases(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    this.erpService
      .listPurchases(this.pageSize, this.page() * this.pageSize)
      .subscribe({
        next: (response) => {
          this.data.set(response);
          this.loading.set(false);
        },
        error: () => {
          this.errorMessage.set(
            'Unable to load purchase orders. Please try again.',
          );
          this.loading.set(false);
        },
      });
  }

  nextPage(): void {
    const total = this.data()?.total ?? 0;

    if ((this.page() + 1) * this.pageSize < total) {
      this.page.update((value) => value + 1);
      this.loadPurchases();
    }
  }

  previousPage(): void {
    if (this.page() > 0) {
      this.page.update((value) => value - 1);
      this.loadPurchases();
    }
  }

  get totalPages(): number {
    return Math.ceil((this.data()?.total ?? 0) / this.pageSize);
  }
}