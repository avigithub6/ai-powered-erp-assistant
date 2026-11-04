import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AiService } from '../../core/services/ai.service';
import { AIQueryResponse } from '../../core/models/ai.model';

@Component({
  selector: 'app-ai-assistant',
  imports: [CommonModule],
  templateUrl: './ai-assistant.html',
  styleUrl: './ai-assistant.scss'
})
export class AiAssistant {
  private readonly aiService = inject(AiService);

  readonly question = signal('');
  readonly loading = signal(false);
  readonly errorMessage = signal('');
  readonly response = signal<AIQueryResponse | null>(null);

  submitQuestion(): void {
    const question = this.question().trim();

    if (!question || this.loading()) {
      return;
    }

    this.loading.set(true);
    this.errorMessage.set('');
    this.response.set(null);

    this.aiService.query(question).subscribe({
      next: (result) => {
        this.response.set(result);
        this.loading.set(false);
      },
      error: () => {
        this.errorMessage.set(
          'Unable to process your question. Please try again.'
        );
        this.loading.set(false);
      }
    });
  }

  askSuggestion(question: string): void {
    this.question.set(question);
    this.submitQuestion();
  }

  clearResponse(): void {
    this.question.set('');
    this.response.set(null);
    this.errorMessage.set('');
  }
}