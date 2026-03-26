/**
 * API client for MatExtractAI backend
 * Handles all communication with the backend API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

export interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
}

export interface JobDetailsResponse extends JobStatusResponse {
  created_at: string;
  updated_at: string;
  result?: Record<string, unknown>;
  error?: string;
}

/**
 * Upload a PDF file for processing
 * @param file The PDF file to upload
 * @returns Job status with job_id
 */
export async function uploadPDF(file: File): Promise<JobStatusResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Upload failed with status ${response.status}`);
  }

  return response.json();
}

/**
 * Get the status of a processing job
 * @param jobId The job ID to check
 * @returns Current job status and details
 */
export async function getJobStatus(jobId: string): Promise<JobDetailsResponse> {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/jobs/${jobId}/status`);

  if (!response.ok) {
    throw new Error(`Failed to get job status: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get the results of a completed job
 * @param jobId The job ID to get results for
 * @returns Job results and extracted data
 */
export async function getJobResults(jobId: string): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/results/${jobId}`);

  if (!response.ok) {
    throw new Error(`Failed to get job results: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Check API health/connectivity
 * @returns Health status
 */
export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error('API health check failed');
  }

  return response.json();
}
