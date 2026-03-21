export type Language = 'en' | 'ru';

export interface User {
  email: string;
  name: string;
  authenticated: boolean;
}

export interface Metadata {
  binary_model: {
    class_map: Record<string, string>;
  };
  multiclass_model: {
    class_map: Record<string, string>;
  };
}

export interface ClassificationResult {
  details: Record<string, number>;
  recognized: boolean;
  class_name?: string;
  confidence?: number;
}

export interface Entry {
  DateTime: string;
  Score: number;
  Recognized: string;
}

export interface ScoreData {
  score: number;
  class_name: string;
  icon_b64: string;
}

export interface AppConfig {
  inferenceServer: string;
  entriesServer: string;
  binaryThreshold: number;
  authUrl?: string;
  authRealm?: string;
  authClientId?: string;
}

// API Response Types
export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}

export interface ClassificationResponse {
  [index: number]: number[];
}

export interface IconsResponse {
  [index: number]: string[];
}

export type ScoresResponse = Entry[];

