import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  AIQueryRequest,
  AIQueryResponse
} from '../models/ai.model';

@Injectable({
  providedIn: 'root'
})
export class AiService {
  private readonly http = inject(HttpClient);

  query(question: string): Observable<AIQueryResponse> {
    const payload: AIQueryRequest = { question };

    return this.http.post<AIQueryResponse>(
      '/api/v1/ai/query',
      payload
    );
  }
}