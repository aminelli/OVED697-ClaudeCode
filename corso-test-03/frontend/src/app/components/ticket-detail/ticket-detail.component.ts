import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { switchMap } from 'rxjs';
import { TicketsService } from '../../services/tickets.service';
import { Ticket } from '../../models/ticket.model';

@Component({
  selector: 'app-ticket-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule],
  template: `
    <div class="detail-page" *ngIf="ticket; else loadingTpl">
      <!-- Back nav -->
      <a routerLink="/" class="back-link">← Dashboard</a>

      <div class="detail-layout">
        <!-- Left: ticket info + classification -->
        <div class="left-panel">
          <div class="panel">
            <div class="panel-header">
              <h2 class="panel-title">{{ ticket.id }}</h2>
              <span class="badge" [class]="'status-' + ticket.status">
                {{ ticket.status }}
              </span>
            </div>

            <!-- Classification badges -->
            <div class="classification-strip" *ngIf="ticket.classification">
              <span class="badge" [class]="'priority-' + ticket.classification['artifact:priority']">
                {{ ticket.classification['artifact:priority'] }}
              </span>
              <span class="cat-badge">{{ ticket.classification['artifact:category'] }}</span>
              <span class="sentiment-label">
                {{ sentimentIcon(ticket.classification['artifact:sentiment']) }}
                {{ ticket.classification['artifact:sentiment'] }}
              </span>
            </div>

            <!-- Tags -->
            <div class="tags-row" *ngIf="ticket.classification?.['artifact:tags']?.length">
              <span class="tag" *ngFor="let tag of ticket.classification!['artifact:tags']">
                {{ tag }}
              </span>
            </div>

            <!-- Summary -->
            <div class="summary-box" *ngIf="ticket.classification?.['artifact:summary']">
              <span class="summary-label">Sommario</span>
              <p class="summary-text">{{ ticket.classification!['artifact:summary'] }}</p>
            </div>

            <!-- Original ticket -->
            <div class="original-ticket">
              <span class="section-label">Messaggio originale</span>
              <pre class="ticket-body">{{ ticket.content }}</pre>
            </div>
          </div>

          <!-- Placeholder helper -->
          <div class="panel hint-panel" *ngIf="ticket.status === 'draft-ready'">
            <h3 class="hint-title">💡 Come revisionare</h3>
            <ol class="hint-list">
              <li>Leggi la bozza a destra</li>
              <li>Sostituisci tutti i <code>[PLACEHOLDER: ...]</code> con le informazioni reali</li>
              <li>Correggi o integra il testo se necessario</li>
              <li>Clicca <strong>Approva</strong> per segnare il ticket come gestito</li>
            </ol>
          </div>
        </div>

        <!-- Right: draft editor -->
        <div class="right-panel" *ngIf="ticket.draft; else noDraftTpl">
          <div class="panel">
            <div class="panel-header">
              <h3 class="panel-title">Bozza risposta</h3>
              <div class="draft-meta">
                <span class="meta-item">Tono: {{ ticket.draft!['artifact:tone'] }}</span>
                <span class="meta-item placeholder-count"
                  [class.has-placeholders]="remainingPlaceholders > 0">
                  {{ remainingPlaceholders }} placeholder
                </span>
              </div>
            </div>

            <div class="subject-row">
              <span class="field-label">Oggetto</span>
              <div class="subject-value">{{ ticket.draft!['artifact:subject'] }}</div>
            </div>

            <div class="editor-area">
              <div class="editor-header">
                <span class="field-label">Corpo della risposta</span>
                <span class="char-count">{{ draftBody.length }} caratteri</span>
              </div>
              <textarea
                [(ngModel)]="draftBody"
                (ngModelChange)="onDraftChange()"
                rows="20"
                [disabled]="ticket.status === 'approved'"
                placeholder="La bozza apparirà qui dopo che Claude ha processato il ticket..."
              ></textarea>
            </div>

            <!-- Actions -->
            <div class="action-bar" *ngIf="ticket.status !== 'approved'">
              <button
                class="btn-secondary"
                (click)="saveDraft()"
                [disabled]="saving || !draftDirty"
              >
                {{ saving ? 'Salvataggio...' : '💾 Salva bozza' }}
              </button>
              <button
                class="btn-danger"
                (click)="rejectDraft()"
                [disabled]="saving"
              >
                ✕ Rifiuta
              </button>
              <button
                class="btn-success"
                (click)="approveDraft()"
                [disabled]="saving || remainingPlaceholders > 0"
                [title]="remainingPlaceholders > 0 ? 'Completa tutti i placeholder prima di approvare' : ''"
              >
                ✓ Approva risposta
              </button>
            </div>

            <div class="approved-banner" *ngIf="ticket.status === 'approved'">
              ✓ Risposta approvata e pronta per l'invio
            </div>

            <div class="feedback" *ngIf="feedback">
              {{ feedback }}
            </div>
          </div>
        </div>

        <ng-template #noDraftTpl>
          <div class="right-panel">
            <div class="panel empty-draft-panel">
              <div class="empty-state">
                <p class="empty-title">Nessuna bozza disponibile</p>
                <p class="empty-sub">
                  Esegui in Claude Code:
                </p>
                <code class="command-snippet">/process-ticket {{ ticket.id }}</code>
                <p class="empty-sub">
                  L'agente classificherà il ticket e genererà una bozza di risposta.
                </p>
              </div>
            </div>
          </div>
        </ng-template>
      </div>
    </div>

    <ng-template #loadingTpl>
      <div class="loading-full">
        <div class="spinner"></div>
        <span>Caricamento ticket...</span>
      </div>
    </ng-template>
  `,
  styles: [`
    .detail-page { display: flex; flex-direction: column; gap: 16px; }

    .back-link {
      font-size: 13px;
      color: var(--color-text-muted);
      &:hover { color: var(--color-text); }
    }

    .detail-layout {
      display: grid;
      grid-template-columns: 380px 1fr;
      gap: 20px;
      align-items: start;
    }

    .panel {
      background: var(--color-surface);
      border: 1px solid var(--color-border);
      border-radius: 10px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .panel-title { margin: 0; font-size: 16px; font-weight: 700; }

    .classification-strip { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }

    .cat-badge {
      background: var(--color-surface-2);
      border: 1px solid var(--color-border);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: 500;
    }

    .sentiment-label { font-size: 12px; color: var(--color-text-muted); }

    .tags-row { display: flex; gap: 6px; flex-wrap: wrap; }

    .tag {
      background: var(--color-surface-2);
      border: 1px solid var(--color-border);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      color: var(--color-text-muted);
    }

    .summary-box {
      background: var(--color-surface-2);
      border-radius: 6px;
      padding: 10px 12px;
    }

    .summary-label, .field-label, .section-label {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--color-text-muted);
      font-weight: 600;
      display: block;
      margin-bottom: 4px;
    }

    .summary-text { margin: 0; font-size: 13px; font-style: italic; }

    .original-ticket {}
    .ticket-body {
      margin: 0;
      font-family: inherit;
      font-size: 13px;
      line-height: 1.6;
      white-space: pre-wrap;
      color: var(--color-text-muted);
      background: var(--color-surface-2);
      border-radius: 6px;
      padding: 12px;
      border: 1px solid var(--color-border);
    }

    .hint-panel { margin-top: 4px; }
    .hint-title { margin: 0 0 8px; font-size: 14px; }
    .hint-list { margin: 0; padding-left: 20px; display: flex; flex-direction: column; gap: 6px; }
    .hint-list li { font-size: 13px; color: var(--color-text-muted); }

    .draft-meta { display: flex; gap: 12px; align-items: center; }
    .meta-item { font-size: 12px; color: var(--color-text-muted); }
    .placeholder-count.has-placeholders { color: var(--priority-medium); font-weight: 600; }

    .subject-row {}
    .subject-value {
      background: var(--color-surface-2);
      border: 1px solid var(--color-border);
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 13px;
    }

    .editor-area { display: flex; flex-direction: column; gap: 8px; }
    .editor-header { display: flex; justify-content: space-between; align-items: center; }
    .char-count { font-size: 11px; color: var(--color-text-muted); }

    .action-bar {
      display: flex;
      gap: 8px;
      justify-content: flex-end;
      padding-top: 8px;
      border-top: 1px solid var(--color-border);
    }

    .approved-banner {
      text-align: center;
      padding: 12px;
      background: rgba(16,185,129,0.1);
      border: 1px solid rgba(16,185,129,0.3);
      border-radius: 6px;
      color: var(--status-approved);
      font-weight: 600;
    }

    .feedback {
      font-size: 12px;
      text-align: center;
      color: var(--color-text-muted);
    }

    .empty-draft-panel { min-height: 300px; justify-content: center; }
    .empty-state { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 8px; }
    .empty-title { font-size: 16px; font-weight: 600; margin: 0; }
    .empty-sub { color: var(--color-text-muted); font-size: 13px; margin: 0; }
    .command-snippet {
      background: var(--color-surface-2);
      border: 1px solid var(--color-border);
      padding: 8px 16px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 14px;
    }

    .loading-full {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      height: 300px;
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

    @media (max-width: 900px) {
      .detail-layout { grid-template-columns: 1fr; }
    }
  `]
})
export class TicketDetailComponent implements OnInit {
  ticket: Ticket | null = null;
  draftBody = '';
  draftDirty = false;
  saving = false;
  feedback = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private ticketsService: TicketsService
  ) {}

  ngOnInit(): void {
    this.route.params
      .pipe(switchMap((p) => this.ticketsService.getById(p['id'])))
      .subscribe((t) => {
        this.ticket = t;
        this.draftBody = t.draft?.body ?? '';
        this.draftDirty = false;
      });
  }

  get remainingPlaceholders(): number {
    return (this.draftBody.match(/\[PLACEHOLDER:/g) || []).length;
  }

  onDraftChange(): void {
    this.draftDirty = true;
  }

  saveDraft(): void {
    if (!this.ticket) return;
    this.saving = true;
    this.ticketsService.updateDraft(this.ticket.id, this.draftBody).subscribe({
      next: () => {
        this.saving = false;
        this.draftDirty = false;
        this.feedback = '✓ Bozza salvata';
        setTimeout(() => (this.feedback = ''), 2000);
      },
      error: () => {
        this.saving = false;
        this.feedback = '✗ Errore salvataggio';
      },
    });
  }

  approveDraft(): void {
    if (!this.ticket) return;
    this.saving = true;
    this.ticketsService.approveDraft(this.ticket.id, this.draftBody).subscribe({
      next: () => {
        this.saving = false;
        this.ticket!.status = 'approved';
        this.feedback = '✓ Risposta approvata!';
      },
      error: () => {
        this.saving = false;
        this.feedback = '✗ Errore';
      },
    });
  }

  rejectDraft(): void {
    if (!this.ticket) return;
    const reason = prompt('Motivo del rifiuto (opzionale):') ?? '';
    this.saving = true;
    this.ticketsService.rejectDraft(this.ticket.id, reason).subscribe({
      next: () => {
        this.saving = false;
        this.ticket!.status = 'rejected';
        this.feedback = 'Bozza rifiutata.';
      },
      error: () => {
        this.saving = false;
      },
    });
  }

  sentimentIcon(sentiment: string): string {
    const m: Record<string, string> = { frustrated: '😤', neutral: '😐', satisfied: '😊' };
    return m[sentiment] ?? '';
  }
}
