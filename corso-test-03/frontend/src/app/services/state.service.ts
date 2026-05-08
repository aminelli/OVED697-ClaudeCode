import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PipelineState } from '../models/pipeline-state.model';

@Injectable({ providedIn: 'root' })
export class StateService {
  private readonly base = '/api/state';

  constructor(private http: HttpClient) {}

  getState(): Observable<PipelineState> {
    return this.http.get<PipelineState>(this.base);
  }
}
