import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErpDataService } from '../../core/services/erp-data.service';
import { AuthService } from '../../core/services/auth.service';
import { InventoryItem, PaginatedResponse } from '../../core/models/erp.model';

@Component({
  selector: 'app-inventory',
  imports: [CommonModule],
  templateUrl: './inventory.html',
  styleUrl: './inventory.scss',
})
export class Inventory implements OnInit {
  private readonly erpService = inject(ErpDataService);
  private readonly authService = inject(AuthService);

  readonly loading = signal(true);
  readonly errorMessage = signal('');
  readonly data = signal<PaginatedResponse<InventoryItem> | null>(null);
  readonly page = signal(0);
  readonly lowStockOnly = signal(false);

  readonly pageSize = 20;

  get canViewPurchasePrice(): boolean {
    return ['Administrator', 'Purchase Executive', 'Management'].includes(
      this.authService.currentUser?.role ?? '',
    );
  }

  ngOnInit(): void {
    this.loadInventory();
  }

  loadInventory(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    this.erpService
      .listInventory(
        this.pageSize,
        this.page() * this.pageSize,
        this.lowStockOnly(),
      )
      .subscribe({
        next: (response) => {
          this.data.set(response);
          this.loading.set(false);
        },
        error: () => {
          this.errorMessage.set(
            'Unable to load inventory. Please try again.',
          );
          this.loading.set(false);
        },
      });
  }

  toggleLowStock(): void {
    this.lowStockOnly.update((value) => !value);
    this.page.set(0);
    this.loadInventory();
  }

  nextPage(): void {
    const total = this.data()?.total ?? 0;

    if ((this.page() + 1) * this.pageSize < total) {
      this.page.update((value) => value + 1);
      this.loadInventory();
    }
  }

  previousPage(): void {
    if (this.page() > 0) {
      this.page.update((value) => value - 1);
      this.loadInventory();
    }
  }

  get totalPages(): number {
    return Math.ceil((this.data()?.total ?? 0) / this.pageSize);
  }
}