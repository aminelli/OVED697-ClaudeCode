import { Component } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink],
  template: `
    <div class="app-shell">
      <header class="topbar">
        <a routerLink="/" class="logo">
          <span class="logo-icon">⚡</span>
          Customer Triage
          <span class="logo-tag">corso-test-03</span>
        </a>
        <nav class="topbar-nav">
          <a routerLink="/" class="nav-link">Dashboard</a>
        </nav>
      </header>
      <main class="main-content">
        <router-outlet />
      </main>
    </div>
  `,
  styles: [`
    .app-shell {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      height: 56px;
      background: var(--color-surface);
      border-bottom: 1px solid var(--color-border);
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 700;
      font-size: 16px;
      color: var(--color-text);
      text-decoration: none;
    }

    .logo-icon { font-size: 20px; }

    .logo-tag {
      font-size: 10px;
      font-weight: 500;
      padding: 2px 6px;
      border-radius: 4px;
      background: var(--color-surface-2);
      color: var(--color-text-muted);
      border: 1px solid var(--color-border);
    }

    .topbar-nav { display: flex; gap: 4px; }

    .nav-link {
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      color: var(--color-text-muted);
      transition: all 0.15s;
      &:hover {
        color: var(--color-text);
        background: var(--color-surface-2);
      }
    }

    .main-content {
      flex: 1;
      padding: 24px;
      max-width: 1400px;
      width: 100%;
      margin: 0 auto;
    }
  `]
})
export class AppComponent {}
