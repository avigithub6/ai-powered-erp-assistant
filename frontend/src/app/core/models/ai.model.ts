export interface AIQueryRequest {
  question: string;
}

export interface AIQueryResponse {
  answer: string;
  tool_used: string | null;
  source: string;
  data: unknown;
}

export interface AIChatMessage {
  role: 'user' | 'assistant';
  content: string;
  toolUsed?: string | null;
  source?: string;
  data?: unknown;
}