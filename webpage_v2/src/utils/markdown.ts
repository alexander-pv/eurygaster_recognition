import type { Language } from '../types';
import { SUPPORTED_LANGUAGES } from '../config';

const markdownCache = new Map<string, string>();
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

/** Allow only safe markdown filenames (no path traversal, no protocol) */
const SAFE_FILENAME = /^[a-zA-Z0-9_.-]+\.md$/;

const sleep = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

export const loadMarkdown = async (lang: Language, filename: string, retries: number = MAX_RETRIES): Promise<string> => {
  // Security: prevent path traversal and invalid inputs
  if (!SUPPORTED_LANGUAGES.includes(lang)) {
    throw new Error('Invalid language for markdown');
  }
  if (!SAFE_FILENAME.test(filename)) {
    throw new Error('Invalid markdown filename');
  }

  const cacheKey = `${lang}/${filename}`;

  // Check cache first
  const cached = markdownCache.get(cacheKey);
  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(`/markdown/${lang}/${filename}`);
    if (!response.ok) {
      throw new Error(`Failed to load markdown: ${response.status} ${response.statusText}`);
    }
    const text = await response.text();
    
    // Validate that we got actual content
    if (!text || text.trim().length === 0) {
      throw new Error('Markdown file is empty');
    }
    
    markdownCache.set(cacheKey, text);
    return text;
  } catch (error) {
    // Retry on network errors
    if (retries > 0 && error instanceof Error && 
        (error.message.includes('Failed to fetch') || 
         error.message.includes('NetworkError') ||
         error.message.includes('timeout'))) {
      console.warn(`Retrying markdown load for ${cacheKey}, ${retries} attempts remaining`);
      await sleep(RETRY_DELAY * (MAX_RETRIES - retries + 1)); // Exponential backoff
      return loadMarkdown(lang, filename, retries - 1);
    }
    
    console.error(`Error loading markdown ${cacheKey}:`, error);
    // Return a user-friendly error message instead of empty string
    throw new Error(`Failed to load content. Please refresh the page or contact support if the problem persists.`);
  }
};

