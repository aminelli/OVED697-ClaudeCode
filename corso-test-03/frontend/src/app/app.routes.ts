import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./components/dashboard/dashboard.component').then((m) => m.DashboardComponent),
  },
  {
    path: 'ticket/:id',
    loadComponent: () =>
      import('./components/ticket-detail/ticket-detail.component').then(
        (m) => m.TicketDetailComponent
      ),
  },
  { path: '**', redirectTo: '' },
];
