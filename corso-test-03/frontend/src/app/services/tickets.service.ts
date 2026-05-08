import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Ticket } from '../models/ticket.model';

@Injectable({ providedIn: 'root' })
export class TicketsService {
  private readonly base = '/api/tickets';

  constructor(private http: HttpClient) {}

  getAll(): Observable<Ticket[]> {
    return this.http.get<Ticket[]>(this.base);
  }

  getById(id: string): Observable<Ticket> {
    return this.http.get<Ticket>(`${this.base}/${id}`);
  }

  approveDraft(id: string, body: string): Observable<{ success: boolean }> {
    return this.http.post<{ success: boolean }>(`${this.base}/${id}/approve`, { body });
  }

  rejectDraft(id: string, reason: string): Observable<{ success: boolean }> {
    return this.http.post<{ success: boolean }>(`${this.base}/${id}/reject`, { reason });
  }

  updateDraft(id: string, body: string): Observable<{ success: boolean }> {
    return this.http.put<{ success: boolean }>(`${this.base}/${id}/draft`, { body });
  }
}
