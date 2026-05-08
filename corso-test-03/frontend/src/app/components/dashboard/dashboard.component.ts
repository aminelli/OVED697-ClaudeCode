import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { interval, Subscription, switchMap, startWith } from 'rxjs';
import { TicketsService } from '../../services/tickets.service';
import { StateService } from '../../services/state.service';
import { Ticket, Priority, TicketStatus } from '../../models/ticket.model';
import { PipelineState } from '../../models/pipeline-state.model';
import { PipelineStatePanelComponent } from '../pipeline-state-panel/pipeline-state-panel.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, PipelineStatePanelComponent],
  template: `
    <div class="dashboard">
      <!-- Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Triage Dashboard</h1>
          <p class="page-subtitle">Revisiona e approva le bozze generate dagli agenti Claude</p>
        </div>
        <button class="btn-secondary" (click)="refresh()" [disabled]="loading">
          {{ loading ? 'Aggiornamento...' : '↻ Aggiorna' }}
        </button>
      </div>

      <!-- Stats bar -->
      <div class="stats-bar" *ngIf="!loading">
        <div class="stat-item">
          <span class="stat-number">{{ countByStatus('unprocessed') }}</span>
          <span class="stat-label">Non processati</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ countByStatus('draft-ready') }}</span>
          <span class="stat-label">In attesa revisione</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ countByStatus('approved') }}</span>
          <span class="stat-label">Approvati</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{{ tickets.length }}</span>
          <span class="stat-label">Totale ticket</span>
        </div>
      </div>

      <div class="dashboard-body">
        <!-- Ticket list -->
        <section class="ticket-list-section">
          <h2 class="section-title">Ticket</h2>

          <div *ngIf="loading" class="loading-state">
            <div class="spinner"></div>
            <span>Caricamento ticket...</span>
          </div>

          <div *ngIf="error" class="error-state">
            <span>⚠ {{ error }}</span>
            <button class="btn-secondary" (click)="refresh()">Riprova</button>
          </div>

          <div *ngIf="!loading && !error" class="ticket-grid">
            <a
              *ngFor="let ticket of tickets"
              [routerLink]="['/ticket', ticket.id]"
              class="ticket-card"
              [class]="'ticket-card status-border-' + ticket.status"
            >
              <div class="ticket-card-header">
                <span class="ticket-id">{{ ticket.id }}</span>
                <span class="badge" [class]="'status-' + ticket.status">
                  {{ ticket.status | titlecase }}
                </span>
              </div>

              <p class="ticket-preview">{{ ticket.content | slice:0:120 }}...</p>

              <div class="ticket-card-meta" *ngIf="ticket.classification">
                <span class="badge" [class]="'priority-' + ticket.classification['artifact:priority']">
                  {{ ticket.classification['artifact:priority'] }}
                </span>
                <span class="meta-category">{{ ticket.classification['artifact:category'] }}</span>
                <span class="meta-sentiment">{{ sentimentIcon(ticket.classification['artifact:sentiment']) }}</span>
              </div>

              <div class="ticket-card-meta" *ngIf="!ticket.classification">
                <span class="meta-muted">Non ancora classificato — usa /process-ticket in Claude Code</span>
              </div>

              <div class="ticket-card-footer" *ngIf="ticket.classification">
                <span class="summary">{{ ticket.classification['artifact:summary'] }}</span>
              </div>
            </a>

            <div *ngIf="tickets.length === 0" class="empty-state">
              <p>Nessun ticket trovato in <code>tickets/</code></p>
            </div>
          </div>
        </section>

        <!-- Pipeline state panel -->
        <aside class="sidebar">
          <app-pipeline-state-panel [state]="pipelineState" />
        </aside>
      </div>
    </div>
  `,
  styles: [`
    .dashboard { display: flex; flex-direction: column; gap: 24px; }

    .page-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
    }

    .page-title {
      margin: 0 0 4px;
      font-size: 24px;
      font-weight: 700;
    }

    .page-subtitle {
      margin: 0;
      color: var(--color-text-muted);
      font-size: 13px;
    }

    .stats-bar {
      display: flex;
      gap: 1px;
      background: var(--color-border);
      border-radius: 10px;
      overflow: hidden;
      border: 1px solid var(--color-border);
    }

    .stat-item {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px;
      background: var(--color-surface);
      gap: 4px;
    }

    .stat-number {
      font-size: 28px;
      font-weight: 700;
      color: var(--color-text);
    }

    .stat-label {
      font-size: 11px;
      color: var(--color-text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .dashboard-body {
      display: grid;
      grid-template-columns: 1fr 320px;
      gap: 24px;
      align-items: start;
    }

    .section-title {
      margin: 0 0 16px;
      font-size: 16px;
      font-weight: 600;
      color: var(--color-text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .ticket-grid {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .ticket-card {
      display: flex;
      flex-direction: column;
      gap: 10px;
      padding: 16px;
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: 10px;
      text-decoration: none;
      color: var(--color-text);
      transition: all 0.15s;
      border-left: 3px solid transparent;

      &:hover {
        border-color: var(--color-accent);
        background: var(--color-surface-2);
      }
    }

    .status-border-draft-ready { border-left-color: var(--status-draft-ready) !important; }
    .status-border-approved    { border-left-color: var(--status-approved) !important; }
    .status-border-rejected    { border-left-color: var(--status-rejected) !important; }

    .ticket-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .ticket-id {
      font-family: monospace;
      font-size: 12px;
      color: var(--color-text-muted);
      font-weight: 600;
    }

    .ticket-preview {
      margin: 0;
      font-size: 13px;
      color: var(--color-text-muted);
      line-height: 1.5;
    }

    .ticket-card-meta {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .meta-category {
      font-size: 12px;
      color: var(--color-text-muted);
      font-weight: 500;
    }

    .meta-sentiment { font-size: 16px; }

    .meta-muted {
      font-size: 11px;
      color: var(--color-text-muted);
      font-style: italic;
    }

    .ticket-card-footer { border-top: 1px solid var(--color-border); padding-top: 8px; }

    .summary {
      font-size: 12px;
      color: var(--color-text);
      font-style: italic;
    }

    .loading-state, .error-state, .empty-state {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 40px;
      justify-content: center;
      color: var(--color-text-muted);
    }

    .spinner {
      width: 20px; height: 20px;
      border: 2px solid var(--color-border);
      border-top-color: var(--color-accent);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .sidebar { position: sticky; top: 80px; }

    @media (max-width: 900px) {
      .dashboard-body { grid-template-columns: 1fr; }
      .sidebar { position: static; }
    }
  `]
})
export class DashboardComponent implements OnInit, OnDestroy {
  tickets: Ticket[] = [];
  pipelineState: PipelineState | null = null;
  loading = true;
  error: string | null = null;

  private sub = new Subscription();

  constructor(
    private ticketsService: TicketsService,
    private stateService: StateService
  ) {}

  ngOnInit(): void {
    // Auto-refresh ogni 10 secondi
    this.sub.add(
      interval(10000)
        .pipe(startWith(0), switchMap(() => this.ticketsService.getAll()))
        .subscribe({
          next: (tickets) => {
            this.tickets = tickets;
            this.loading = false;
            this.error = null;
          },
          error: (err) => {
            this.loading = false;
            this.error = 'Backend non raggiungibile. Avvia il server con: cd backend && npm start';
          },
        })
    );

    this.sub.add(
      interval(10000)
        .pipe(startWith(0), switchMap(() => this.stateService.getState()))
        .subscribe({ next: (s) => (this.pipelineState = s) })
    );
  }

  ngOnDestroy(): void {
    this.sub.unsubscribe();
  }

  refresh(): void {
    this.loading = true;
    this.ticketsService.getAll().subscribe({
      next: (t) => { this.tickets = t; this.loading = false; },
      error: () => { this.loading = false; },
    });
    this.stateService.getState().subscribe({ next: (s) => (this.pipelineState = s) });
  }

  countByStatus(status: TicketStatus): number {
    return this.tickets.filter((t) => t.status === status).length;
  }

  sentimentIcon(sentiment: string): string {
    const map: Record<string, string> = { frustrated: '😤', neutral: '😐', satisfied: '😊' };
    return map[sentiment] ?? '?';
  }
}
