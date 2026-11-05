export interface AIQueryRequest {
  question: string;
}

export interface AIIntentEntities {
  vendor_name?: string | null;
  product_name?: string | null;
  customer_name?: string | null;
  sku?: string | null;
}

export interface AIIntentFilters {
  category?: string | null;
  location?: string | null;
  status?: string | null;
}

export interface AIIntentDateRange {
  start_date?: string | null;
  end_date?: string | null;
}

export interface AIQueryResponse {
  answer: string;
  tool_used: string | null;
  source: string;
  data: unknown;

  // Optional structured intent information
  intent?: string | null;
  entities?: AIIntentEntities | null;
  filters?: AIIntentFilters | null;
  date_range?: AIIntentDateRange | null;
  needs_clarification?: boolean | null;
  clarification_question?: string | null;
}

export interface AIChatMessage {
  role: 'user' | 'assistant';
  content: string;
  toolUsed?: string | null;
  source?: string;
  data?: unknown;
}