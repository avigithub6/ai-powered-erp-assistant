import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ErpDataService } from '../../core/services/erp-data.service';
import { Customer, PaginatedResponse } from '../../core/models/erp.model';

@Component({
  selector: 'app-customers',
  imports: [CommonModule],
  templateUrl: './customers.html',
  styleUrl: './customers.scss',
})
export class Customers implements OnInit {
  private readonly erpService = inject(ErpDataService);

  readonly loading = signal(true);
  readonly errorMessage = signal('');
  readonly data = signal<PaginatedResponse<Customer> | null>(null);
  readonly page = signal(0);

  readonly pageSize = 20;

  ngOnInit(): void {
    this.loadCustomers();
  }

  loadCustomers(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    this.erpService
      .listCustomers(this.pageSize, this.page() * this.pageSize)
      .subscribe({
        next: (response) => {
          this.data.set(response);
          this.loading.set(false);
        },
        error: () => {
          this.errorMessage.set(
            'Unable to load customers. Please try again.',
          );
          this.loading.set(false);
        },
      });
  }

  nextPage(): void {
    const total = this.data()?.total ?? 0;

    if ((this.page() + 1) * this.pageSize < total) {
      this.page.update((value) => value + 1);
      this.loadCustomers();
    }
  }

  previousPage(): void {
    if (this.page() > 0) {
      this.page.update((value) => value - 1);
      this.loadCustomers();
    }
  }

  get totalPages(): number {
    return Math.ceil((this.data()?.total ?? 0) / this.pageSize);
  }
}