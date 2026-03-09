import axios from 'axios';
import type { CreateJobResponse, JobDetailResponse, LanguagesResponse } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

export async function fetchLanguages(): Promise<LanguagesResponse> {
  const response = await client.get<LanguagesResponse>('/languages');
  return response.data;
}

export async function createTranslationJob(payload: {
  sourceLanguage: string;
  targetLanguage: string;
  videoFile: File;
  speakerFile?: File;
}): Promise<CreateJobResponse> {
  const formData = new FormData();
  formData.append('source_language', payload.sourceLanguage);
  formData.append('target_language', payload.targetLanguage);
  formData.append('video', payload.videoFile);
  if (payload.speakerFile) {
    formData.append('speaker_wav', payload.speakerFile);
  }

  const response = await client.post<CreateJobResponse>('/jobs', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

export async function fetchJob(jobId: string): Promise<JobDetailResponse> {
  const response = await client.get<JobDetailResponse>(`/jobs/${jobId}`);
  return response.data;
}

export function resolveAssetUrl(url: string): string {
  if (url.startsWith('http')) {
    return url;
  }
  const base = API_BASE_URL.replace(/\/api\/v1\/?$/, '');
  return `${base}${url}`;
}
