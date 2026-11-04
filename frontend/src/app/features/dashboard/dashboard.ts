import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DashboardService } from '../../core/services/dashboard.service';
import { DashboardData } from '../../core/models/dashboard.model';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit {
  private readonly dashboardService = inject(DashboardService);

  readonly loading = signal(true);
  readonly errorMessage = signal('');
  readonly data = signal<DashboardData | null>(null);

  ngOnInit(): void {
    this.loadDashboard();
  }

  getSalesBarWidth(value: number): number {
    const items = this.data()?.salesTrend ?? [];
    const maximum = Math.max(
      ...items.map(item => Number(item.total_sales)),
      0
    );

    if (maximum <= 0) {
      return 0;
    }

    return Math.max((Number(value) / maximum) * 100, 2);
  }

  getProductBarWidth(value: number): number {
    const items = this.data()?.topProducts ?? [];
    const maximum = Math.max(
      ...items.map(item => Number(item.total_quantity_sold)),
      0
    );

    if (maximum <= 0) {
      return 0;
    }

    return Math.max((Number(value) / maximum) * 100, 2);
  }

  getVendorBarWidth(value: number): number {
    const items = this.data()?.topVendors ?? [];
    const maximum = Math.max(
      ...items.map(item => Number(item.total_purchase_value)),
      0
    );

    if (maximum <= 0) {
      return 0;
    }

    return Math.max((Number(value) / maximum) * 100, 2);
  }

  loadDashboard(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    this.dashboardService.getDashboardData().subscribe({
      next: (response) => {
        this.data.set(response);
        this.loading.set(false);
      },
      error: () => {
        this.errorMessage.set(
          'Unable to load dashboard data. Please try again.'
        );
        this.loading.set(false);
      }
    });
  }
}