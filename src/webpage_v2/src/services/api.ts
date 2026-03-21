import axios, { AxiosError, CancelTokenSource } from 'axios';
import type { Metadata, Entry, ScoreData, ClassificationResponse, IconsResponse, ScoresResponse } from '../types';

// Per-endpoint timeout configuration (in milliseconds)
const ENDPOINT_TIMEOUTS: Record<string, number> = {
  '/metadata': 10000, // 10 seconds for metadata
  '/classify_image': 60000, // 60 seconds for image classification
  '/classify_eurygaster': 60000, // 60 seconds for eurygaster classification
  '/get_score': 15000, // 15 seconds for scores
  '/get_icons': 20000, // 20 seconds for icons
  '/add_score': 15000, // 15 seconds for adding score
};

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second base delay

const isRetryableError = (error: AxiosError): boolean => {
  // Retry on network errors or 5xx server errors
  if (!error.response) {
    return true; // Network error
  }
  const status = error.response.status;
  return status >= 500 || status === 429; // Server error or rate limit
};

const sleep = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

const retryRequest = async <T>(
  requestFn: () => Promise<T>,
  retries: number = MAX_RETRIES
): Promise<T> => {
  try {
    return await requestFn();
  } catch (error) {
    if (retries > 0 && error instanceof AxiosError && isRetryableError(error)) {
      // Exponential backoff
      const delay = RETRY_DELAY * (MAX_RETRIES - retries + 1);
      await sleep(delay);
      return retryRequest(requestFn, retries - 1);
    }
    throw error;
  }
};

const createApiClient = (baseURL: string, defaultTimeout: number = 30000) => {
  const client = axios.create({
    baseURL,
    headers: {
      'Accept': 'application/json',
    },
    timeout: defaultTimeout,
  });

  // Add response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      // Don't throw if request was cancelled
      if (axios.isCancel(error)) {
        throw error;
      }
      
      if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout. Please try again.');
      }
      if (error.response) {
        // Server responded with error status
        throw new Error(`Server error: ${error.response.status} ${error.response.statusText}`);
      } else if (error.request) {
        // Request was made but no response received
        throw new Error('Network error. Please check your connection.');
      }
      throw error;
    }
  );

  return client;
};

export class InferenceService {
  private client;
  private cancelTokens: Map<string, CancelTokenSource> = new Map();

  constructor(baseURL: string) {
    this.client = createApiClient(baseURL);
  }

  // Cancel a specific request by key
  cancelRequest(key: string): void {
    const cancelToken = this.cancelTokens.get(key);
    if (cancelToken) {
      cancelToken.cancel('Request cancelled');
      this.cancelTokens.delete(key);
    }
  }

  // Cancel all pending requests
  cancelAllRequests(): void {
    this.cancelTokens.forEach((cancelToken) => {
      cancelToken.cancel('All requests cancelled');
    });
    this.cancelTokens.clear();
  }

  private getTimeout(endpoint: string): number {
    return ENDPOINT_TIMEOUTS[endpoint] || 30000;
  }

  async getMetadata(cancelKey?: string): Promise<Metadata> {
    const cancelTokenSource = axios.CancelToken.source();
    if (cancelKey) {
      // Cancel previous request with same key if exists
      this.cancelRequest(cancelKey);
      this.cancelTokens.set(cancelKey, cancelTokenSource);
    }

    try {
      const response = await retryRequest(() =>
        this.client.get('/metadata', {
          timeout: this.getTimeout('/metadata'),
          cancelToken: cancelTokenSource.token,
        })
      );
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      return response.data;
    } catch (error) {
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (axios.isCancel(error)) {
        throw new Error('Request was cancelled');
      }
      if (error instanceof Error) {
        throw new Error(`Failed to fetch metadata: ${error.message}`);
      }
      throw new Error('Failed to fetch metadata: Unknown error');
    }
  }

  async classifyImage(
    file: File,
    account: string,
    cancelKey?: string,
    accountName?: string
  ): Promise<number[]> {
    const cancelTokenSource = axios.CancelToken.source();
    if (cancelKey) {
      this.cancelRequest(cancelKey);
      this.cancelTokens.set(cancelKey, cancelTokenSource);
    }

    const headers: Record<string, string> = {
      'Content-Type': file.type || 'image/jpeg',
      Name: file.name,
      Account: account,
    };
    if (accountName != null && accountName !== '') {
      headers['X-Account-Name'] = accountName;
    }

    try {
      const response = await retryRequest(() =>
        this.client.post<ClassificationResponse>(
          '/classify_image',
          file,
          {
            headers,
            timeout: this.getTimeout('/classify_image'),
            cancelToken: cancelTokenSource.token,
          }
        )
      );
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (!response.data) {
        throw new Error('Invalid response format from server: no data');
      }
      if (!Array.isArray(response.data) || response.data.length === 0) {
        throw new Error('Invalid response format from server: expected non-empty array');
      }
      const firstElement = response.data[0];
      if (!Array.isArray(firstElement)) {
        throw new Error('Invalid response format: expected array of numbers');
      }
      return firstElement;
    } catch (error) {
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (axios.isCancel(error)) {
        throw new Error('Request was cancelled');
      }
      if (error instanceof Error) {
        throw new Error(`Image classification failed: ${error.message}`);
      }
      throw new Error('Image classification failed: Unknown error');
    }
  }

  async classifyEurygaster(
    file: File,
    account: string,
    cancelKey?: string,
    accountName?: string
  ): Promise<number[]> {
    const cancelTokenSource = axios.CancelToken.source();
    if (cancelKey) {
      this.cancelRequest(cancelKey);
      this.cancelTokens.set(cancelKey, cancelTokenSource);
    }

    const formData = new FormData();
    formData.append('image', file, file.name);
    formData.append('account', (accountName != null && accountName !== '' ? accountName : account) || '');
    formData.append('name', file.name || 'image.jpg');

    try {
      const response = await retryRequest(() =>
        this.client.post<ClassificationResponse>(
          '/classify_eurygaster',
          formData,
          {
            timeout: this.getTimeout('/classify_eurygaster'),
            cancelToken: cancelTokenSource.token,
          }
        )
      );
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (!response.data) {
        throw new Error('Invalid response format from server: no data');
      }
      if (!Array.isArray(response.data) || response.data.length === 0) {
        throw new Error('Invalid response format from server: expected non-empty array');
      }
      const firstElement = response.data[0];
      if (!Array.isArray(firstElement)) {
        throw new Error('Invalid response format: expected array of numbers');
      }
      return firstElement;
    } catch (error) {
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (axios.isCancel(error)) {
        throw new Error('Request was cancelled');
      }
      if (error instanceof Error) {
        throw new Error(`Eurygaster classification failed: ${error.message}`);
      }
      throw new Error('Eurygaster classification failed: Unknown error');
    }
  }
}

export class EntriesService {
  private client;
  private cancelTokens: Map<string, CancelTokenSource> = new Map();

  constructor(baseURL: string) {
    this.client = createApiClient(baseURL);
  }

  cancelRequest(key: string): void {
    const cancelToken = this.cancelTokens.get(key);
    if (cancelToken) {
      cancelToken.cancel('Request cancelled');
      this.cancelTokens.delete(key);
    }
  }

  cancelAllRequests(): void {
    this.cancelTokens.forEach((cancelToken) => {
      cancelToken.cancel('All requests cancelled');
    });
    this.cancelTokens.clear();
  }

  private getTimeout(endpoint: string): number {
    return ENDPOINT_TIMEOUTS[endpoint] || 30000;
  }

  async getRecentScores(n: number = 5, cancelKey?: string): Promise<Entry[]> {
    const cancelTokenSource = axios.CancelToken.source();
    if (cancelKey) {
      this.cancelRequest(cancelKey);
      this.cancelTokens.set(cancelKey, cancelTokenSource);
    }

    try {
      const response = await retryRequest(() =>
        this.client.get<ScoresResponse>(`/get_score/?n=${n}`, {
          timeout: this.getTimeout('/get_score'),
          cancelToken: cancelTokenSource.token,
        })
      );
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (!response.data) {
        throw new Error('Invalid response format: no data received');
      }
      if (!Array.isArray(response.data)) {
        throw new Error('Invalid response format: expected array');
      }
      // Entries server returns array of tuples [time, score, class_name]; normalize to Entry[]
      return response.data.map((row: unknown): Entry => {
        if (Array.isArray(row) && row.length >= 3) {
          return {
            DateTime: String(row[0] ?? ''),
            Score: Number(row[1]) ?? 0,
            Recognized: String(row[2] ?? ''),
          };
        }
        if (row && typeof row === 'object' && 'DateTime' in row && 'Score' in row && 'Recognized' in row) {
          const o = row as Record<string, unknown>;
          return {
            DateTime: String(o.DateTime ?? o.date_time ?? ''),
            Score: Number(o.Score ?? o.score ?? 0),
            Recognized: String(o.Recognized ?? o.class_name ?? ''),
          };
        }
        return { DateTime: '', Score: 0, Recognized: '' };
      });
    } catch (error) {
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (axios.isCancel(error)) {
        throw new Error('Request was cancelled');
      }
      if (error instanceof Error) {
        throw new Error(`Failed to fetch recent scores: ${error.message}`);
      }
      throw new Error('Failed to fetch recent scores: Unknown error');
    }
  }

  async getRecentIcons(n: number = 10, cancelKey?: string): Promise<string[]> {
    const cancelTokenSource = axios.CancelToken.source();
    if (cancelKey) {
      this.cancelRequest(cancelKey);
      this.cancelTokens.set(cancelKey, cancelTokenSource);
    }

    try {
      const response = await retryRequest(() =>
        this.client.get<IconsResponse>(`/get_icons/?n=${n}`, {
          timeout: this.getTimeout('/get_icons'),
          cancelToken: cancelTokenSource.token,
        })
      );
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (!response.data) {
        throw new Error('Invalid response format: no data received');
      }
      if (!Array.isArray(response.data)) {
        throw new Error('Invalid response format: expected array');
      }
      const b64Strings = response.data.flat();
      return b64Strings.map((b64: string) => {
        if (typeof b64 !== 'string') {
          throw new Error('Invalid response format: expected base64 strings');
        }
        return `data:image/png;base64,${b64}`;
      });
    } catch (error) {
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (axios.isCancel(error)) {
        throw new Error('Request was cancelled');
      }
      if (error instanceof Error) {
        throw new Error(`Failed to fetch recent icons: ${error.message}`);
      }
      throw new Error('Failed to fetch recent icons: Unknown error');
    }
  }

  async addScore(data: ScoreData, cancelKey?: string): Promise<void> {
    const cancelTokenSource = axios.CancelToken.source();
    if (cancelKey) {
      this.cancelRequest(cancelKey);
      this.cancelTokens.set(cancelKey, cancelTokenSource);
    }

    try {
      await retryRequest(() =>
        this.client.post('/add_score/', data, {
          timeout: this.getTimeout('/add_score'),
          cancelToken: cancelTokenSource.token,
        })
      );
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
    } catch (error) {
      if (cancelKey) {
        this.cancelTokens.delete(cancelKey);
      }
      if (axios.isCancel(error)) {
        throw new Error('Request was cancelled');
      }
      if (error instanceof Error) {
        throw new Error(`Failed to add score: ${error.message}`);
      }
      throw new Error('Failed to add score: Unknown error');
    }
  }
}

