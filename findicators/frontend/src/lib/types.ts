export interface PriceData {
  asset: string;
  price: number;
  source: string;
  change_24h: number | null;
  volume_24h: number | null;
}

export interface PriceResponse {
  timestamp: string;
  assets: Record<string, PriceData>;
}

export interface PriceHistoryPoint {
  time: string;
  price: number;
  volume: number | null;
}

export interface PriceHistoryResponse {
  asset: string;
  data: PriceHistoryPoint[];
}

export interface SignalData {
  value: number;
  action: string;
  breakdown: Record<string, number> | null;
}

export interface SignalResponse {
  timestamp: string;
  signals: Record<string, SignalData>;
}

export interface SuggestionData {
  summary: string;
  actions: string[];
}

export interface RegimeResponse {
  timestamp: string;
  regime: string;
  risk_score: number;
  factor_scores: Record<string, number>;
  description: string;
  suggestion: SuggestionData;
}

export interface AllocationResponse {
  timestamp: string;
  regime: string;
  weights: Record<string, number>;
}
