import { Component, inject } from '@angular/core';
import {
  Router,
  RouterLink,
  RouterLinkActive,
  RouterOutlet,
} from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

interface NavigationItem {
  label: string;
  path: string;
  roles: string[];
}

@Component({
  selector: 'app-main-layout',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './main-layout.html',
  styleUrl: './main-layout.scss'
})
export class MainLayout {
  private readonly router = inject(Router);
  readonly authService = inject(AuthService);

  private readonly navigationItems: NavigationItem[] = [
    {
      label: 'Dashboard',
      path: '/dashboard',
      roles: ['Administrator', 'Sales Executive', 'Purchase Executive', 'Management']
    },
    {
      label: 'Sales',
      path: '/sales',
      roles: ['Administrator', 'Sales Executive', 'Management']
    },
    {
      label: 'Purchases',
      path: '/purchases',
      roles: ['Administrator', 'Purchase Executive', 'Management']
    },
    {
      label: 'Inventory',
      path: '/inventory',
      roles: ['Administrator', 'Sales Executive', 'Purchase Executive', 'Management']
    },
    {
      label: 'Vendors',
      path: '/vendors',
      roles: ['Administrator', 'Purchase Executive', 'Management']
    },
    {
      label: 'Customers',
      path: '/customers',
      roles: ['Administrator', 'Sales Executive', 'Management']
    },
    {
      label: 'AI Assistant',
      path: '/ai-assistant',
      roles: ['Administrator', 'Sales Executive', 'Purchase Executive', 'Management']
    }
  ];

  get visibleNavigation(): NavigationItem[] {
    const role = this.authService.currentUser?.role;

    if (!role) {
      return [];
    }

    return this.navigationItems.filter((item) => item.roles.includes(role));
  }

  logout(): void {
    this.authService.logout();
    void this.router.navigate(['/login']);
  }
}
