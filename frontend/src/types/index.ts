export type Language = 'en' | 'hi' | 'ta';

export type Intent = 
  | 'registration' 
  | 'candidate_info' 
  | 'process_education' 
  | 'general' 
  | 'greeting';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  intent?: Intent;
  sources?: SourceCitation[];
  piiDetected?: boolean;
  cached?: boolean;
}

export interface SourceCitation {
  title: string;
  url: string;
  snippet?: string;
}

export interface PIIDetectionInfo {
  detected: boolean;
  types: string[];
  message?: string;
}

export interface ChatRequest {
  message: string;
  language: Language;
  conversation_history: {
    role: string;
    content: string;
  }[];
}

export interface ChatResponse {
  message: string;
  intent: Intent;
  language: Language;
  sources: SourceCitation[];
  pii_info: PIIDetectionInfo;
  cached: boolean;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  services: Record<string, string>;
}

export interface LanguageInfo {
  code: Language;
  name: string;
  native_name: string;
}

export interface LanguagesResponse {
  languages: LanguageInfo[];
  default: string;
}

export interface AccessibilitySettings {
  fontSize: number;       // 100-200 percentage
  highContrast: boolean;
  reducedMotion: boolean;
}

export interface AppState {
  language: Language;
  accessibility: AccessibilitySettings;
  messages: ChatMessage[];
  isLoading: boolean;
}
