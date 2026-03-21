import React, { useEffect, useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { loadMarkdown } from '../utils/markdown';
import ReactMarkdown from 'react-markdown';

export const HowToUsePage: React.FC = () => {
  const { language } = useLanguage();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadContent = async () => {
      setLoading(true);
      try {
        const text = await loadMarkdown(language, 'how_to_use.md');
        setContent(text);
      } catch (error) {
        console.error('Error loading how to use page:', error);
        setContent(error instanceof Error ? error.message : 'Failed to load content. Please try refreshing the page.');
      } finally {
        setLoading(false);
      }
    };

    loadContent();
  }, [language]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-8 prose prose-lg max-w-none">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};

