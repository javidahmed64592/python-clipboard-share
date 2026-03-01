// TypeScript types matching FastAPI Pydantic models

// Base response types
export interface BaseResponse {
  message: string;
  timestamp: string;
}

// Authentication types
export interface AuthContextType {
  apiKey: string | null;
  isAuthenticated: boolean;
  login: (apiKey: string) => Promise<void>;
  logout: () => void;
}

// Clipboard item types
export interface ClipboardHistoryEntry {
  id: string;
  title: string;
  content: string;
}

export interface ClipboardHistoryArchive {
  entries: ClipboardHistoryEntry[];
}

// Response types
export interface HealthResponse extends BaseResponse {}

export interface LoginResponse extends BaseResponse {}

export interface GetHistoryResponse extends BaseResponse {
  history: ClipboardHistoryEntry[];
}

export interface AddEntryResponse extends BaseResponse {
  id: string;
}

export interface DeleteEntryResponse extends BaseResponse {
  id: string;
}

export interface ModifyEntryResponse extends BaseResponse {
  id: string;
}

// Request types
export interface AddEntryRequest {
  title: string;
  content: string;
}

export interface DeleteEntryRequest {
  id: string;
}

export interface ModifyEntryRequest {
  id: string;
  title?: string;
  content?: string;
}
