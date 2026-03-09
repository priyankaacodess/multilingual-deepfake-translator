export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface LanguageOption {
  code: string;
  name: string;
}

export interface LanguagesResponse {
  source_languages: LanguageOption[];
  target_languages: LanguageOption[];
}

export interface CreateJobResponse {
  job_id: string;
  status: JobStatus;
}

export interface JobDetailResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  source_language: string;
  target_language: string;
  created_at: string;
  updated_at: string;
  error?: string | null;
  transcript?: string | null;
  translated_text?: string | null;
  output_url?: string | null;
}
