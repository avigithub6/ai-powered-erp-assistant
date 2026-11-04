import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const roleGuard: CanActivateFn = (route) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const allowedRoles = route.data['roles'] as string[] | undefined;
  const currentRole = authService.currentUser?.role;

  if (allowedRoles?.includes(currentRole ?? '')) {
    return true;
  }

  return router.createUrlTree(['/dashboard']);
};