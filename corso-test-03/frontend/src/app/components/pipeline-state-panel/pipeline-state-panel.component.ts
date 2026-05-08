import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PipelineState } from '../../models/pipeline-state.model';

@Component({
  selector: 'app-pipeline-state-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="state-panel">
      <div class="state-header">
        <span class="state-title">Stato Pipeline</span>
        <span class="state-version" *ngIf="state">v{{ state.pipeline_version }}</span>
      </div>

      <div *ngIf="!state" class="state-empty">
        <span>Stato non disponibile</span>
        <span class="hint">Avvia il backend e usa Claude Code per processare i ticket</span>
      </div>

      <div *ngIf="state">
        <!-- Global stats -->
        <div class="global-stats">
          <div class="global-stat">
            <span class="gs-number">{{ state.global.total_processed }}</span>
            <span class="gs-label">Processati</span>
          </div>
          <div class="global-stat">
            <span class="gs-number">{{ state.global.pending_review }}</span>
            <span class="gs-label">Da revisionare</span>
          </div>
        </div>

        <!-- Per-ticket table -->
        <div class="ticket-table">
          <div class="table-row header-row">
            <span>Ticket</span>
            <span>Status</span>
            <span>Step</span>
          </div>
          <div
            *ngFor="let entry of ticketEntries()"
            class="table-row"
            [class.has-errors]="entry.value.errors.length > 0"
          >
            <span class="t-id">{{ entry.key }}</span>
            <span class="badge" [class]="'status-' + entry.value.status" style="font-size:10px">
              {{ entry.value.status }}
            </span>
            <span class="t-steps">
              <span *ngFor="let step of ['classify','draft','approve']"
                class="step-dot"
                [class.done]="entry.value.steps_completed.includes(step)"
                [title]="step"
              ></span>
            </span>
          </div>
        </div>

        <!-- Errors -->
        <div class="errors-section" *ngIf="hasErrors()">
          <span class="errors-title">⚠ Errori</span>
          <div *ngFor="let entry of errorEntries()" class="error-item">
            <span class="error-id">{{ entry.key }}</span>
            <span class="error-msg">{{ entry.value.errors[0] }}</span>
          </div>
        </div>

        <!-- Last updated -->
        <div class="last-updated">
          Aggiornato: {{ state.last_updated | date:'HH:mm:ss' }}
        </div>
      </div>
    </div>

    <!-- Claude Code commands reference -->
    <div class="commands-ref">
      <div class="commands-title">Comandi Claude Code</div>
      <div class="command-item">
        <code>/process-ticket &lt;id&gt;</code>
        <span>Processa un ticket</span>
      </div>
      <div class="command-item">
        <code>/process-all</code>
        <span>Processa tutti</span>
      </div>
      <div class="command-item">
        <code>/show-state</code>
        <span>Mostra stato</span>
      </div>
    </div>
  `,
  styles: [`
    .state-panel {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .state-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .state-title {
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--color-text-muted);
    }

    .state-version { font-size: 11px; color: var(--color-text-muted); }

    .state-empty {
      display: flex;
      flex-direction: column;
      gap: 4px;
      color: var(--color-text-muted);
      font-size: 12px;
    }

    .hint { font-style: italic; font-size: 11px; }

    .global-stats {
      display: flex;
      gap: 1px;
      background: var(--color-border);
      border-radius: 6px;
      overflow: hidden;
    }

    .global-stat {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 8px;
      background: var(--color-surface-2);
      gap: 2px;
    }

    .gs-number { font-size: 20px; font-weight: 700; }
    .gs-label { font-size: 10px; color: var(--color-text-muted); text-transform: uppercase; }

    .ticket-table { display: flex; flex-direction: column; gap: 4px; }

    .table-row {
      display: grid;
      grid-template-columns: 80px 1fr auto;
      align-items: center;
      gap: 8px;
      padding: 4px 0;
      font-size: 11px;
    }

    .header-row {
      color: var(--color-text-muted);
      font-weight: 600;
      text-transform: uppercase;
      border-bottom: 1px solid var(--color-border);
      padding-bottom: 6px;
    }

    .t-id { font-family: monospace; font-weight: 600; }

    .t-steps { display: flex; gap: 3px; }

    .step-dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--color-border);
      &.done { background: var(--status-approved); }
    }

    .has-errors { background: rgba(239,68,68,0.05); border-radius: 4px; }

    .errors-section {
      background: rgba(239,68,68,0.08);
      border: 1px solid rgba(239,68,68,0.2);
      border-radius: 6px;
      padding: 8px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .errors-title { font-size: 11px; font-weight: 600; color: var(--priority-critical); }
    .error-item { display: flex; gap: 6px; }
    .error-id { font-family: monospace; font-size: 11px; font-weight: 600; }
    .error-msg { font-size: 11px; color: var(--color-text-muted); }

    .last-updated { font-size: 10px; color: var(--color-text-muted); text-align: right; }

    .commands-ref {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: 10px;
      padding: 14px;
      margin-top: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .commands-title {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--color-text-muted);
    }

    .command-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }

    .command-item code {
      font-size: 11px;
      background: var(--color-surface-2);
      border: 1px solid var(--color-border);
      padding: 2px 6px;
      border-radius: 4px;
    }

    .command-item span { font-size: 11px; color: var(--color-text-muted); }
  `]
})
export class PipelineStatePanelComponent {
  @Input() state: PipelineState | null = null;

  ticketEntries(): { key: string; value: any }[] {
    if (!this.state) return [];
    return Object.entries(this.state.tickets).map(([key, value]) => ({ key, value }));
  }

  hasErrors(): boolean {
    return this.ticketEntries().some((e) => e.value.errors.length > 0);
  }

  errorEntries(): { key: string; value: any }[] {
    return this.ticketEntries().filter((e) => e.value.errors.length > 0);
  }
}
