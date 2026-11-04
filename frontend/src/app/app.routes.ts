import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

import { Login } from './features/auth/login/login';
import { Dashboard } from './features/dashboard/dashboard';
import { Sales } from './features/sales/sales';
import { Purchases } from './features/purchases/purchases';
import { Inventory } from './features/inventory/inventory';
import { Vendors } from './features/vendors/vendors';
import { Customers } from './features/customers/customers';
import { AiAssistant } from './features/ai-assistant/ai-assistant';

import { MainLayout } from './layout/main-layout/main-layout';

const ALL_ROLES = [
  'Administrator',
  'Sales Executive',
  'Purchase Executive',
  'Management',
];

export const routes: Routes = [
  {
    path: 'login',
    component: Login,
  },
  {
    path: '',
    component: MainLayout,
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        component: Dashboard,
        canActivate: [roleGuard],
        data: { roles: ALL_ROLES },
      },
      {
        path: 'sales',
        component: Sales,
        canActivate: [roleGuard],
        data: {
          roles: ['Administrator', 'Sales Executive', 'Management'],
        },
      },
      {
        path: 'purchases',
        component: Purchases,
        canActivate: [roleGuard],
        data: {
          roles: ['Administrator', 'Purchase Executive', 'Management'],
        },
      },
      {
        path: 'inventory',
        component: Inventory,
        canActivate: [roleGuard],
        data: { roles: ALL_ROLES },
      },
      {
        path: 'vendors',
        component: Vendors,
        canActivate: [roleGuard],
        data: {
          roles: ['Administrator', 'Purchase Executive', 'Management'],
        },
      },
      {
        path: 'customers',
        component: Customers,
        canActivate: [roleGuard],
        data: {
          roles: ['Administrator', 'Sales Executive', 'Management'],
        },
      },
      {
        path: 'ai-assistant',
        component: AiAssistant,
        canActivate: [roleGuard],
        data: { roles: ALL_ROLES },
      },
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full',
      },
    ],
  },
  {
    path: '**',
    redirectTo: 'dashboard',
  },
];