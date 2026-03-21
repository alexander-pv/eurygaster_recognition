import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { InferenceService, EntriesService } from '../services/api';
import { DEFAULT_CONFIG } from '../config';
import { getTranslation } from '../translations';
import { imageToBase64Icon } from '../utils/imageUtils';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Upload, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import type { Metadata, ClassificationResult } from '../types';

export const IdentifyPage: React.FC = () => {
  const { user } = useAuth();
  const { language } = useLanguage();
  const t = getTranslation(language);
  
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [metadataLoading, setMetadataLoading] = useState(true);
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [metadata, setMetadata] = useState<Metadata | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isClassifying, setIsClassifying] = useState(false);

  // Memoize service instances to avoid recreating on every render
  const inferenceService = useMemo(
    () => new InferenceService(DEFAULT_CONFIG.inferenceServer),
    []
  );
  const entriesService = useMemo(
    () => new EntriesService(DEFAULT_CONFIG.entriesServer),
    []
  );

  useEffect(() => {
    let cancelled = false;
    const loadMetadata = async () => {
      setMetadataLoading(true);
      try {
        const meta = await inferenceService.getMetadata('metadata-load');
        if (!cancelled) {
          setMetadata(meta);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          if (err instanceof Error && err.message.includes('cancelled')) {
            return; // Don't show error for cancelled requests
          }
          console.error('Failed to load metadata:', err);
          setError('Failed to connect to inference server');
        }
      } finally {
        if (!cancelled) {
          setMetadataLoading(false);
        }
      }
    };
    loadMetadata();
    
    return () => {
      cancelled = true;
      inferenceService.cancelRequest('metadata-load');
    };
  }, [inferenceService]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      if (!['image/jpeg', 'image/jpg'].includes(selectedFile.type)) {
        setError('Please upload a JPEG or JPG image');
        return;
      }
      
      // Validate file size (50MB = 50 * 1024 * 1024 bytes)
      const maxSize = 50 * 1024 * 1024; // 50MB in bytes
      if (selectedFile.size > maxSize) {
        setError(`File size exceeds the maximum limit of 50MB. Your file is ${(selectedFile.size / (1024 * 1024)).toFixed(2)}MB`);
        return;
      }
      
      setFile(selectedFile);
      setResult(null);
      setError(null);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleClassify = async () => {
    if (!file || !metadata || !user.authenticated || isClassifying) return;

    setLoading(true);
    setIsClassifying(true);
    setError(null);

    // Cancel any previous classification requests
    inferenceService.cancelRequest('classify-image');
    inferenceService.cancelRequest('classify-eurygaster');

    try {
      // Binary classification
      const binaryProbs = await inferenceService.classifyImage(
        file,
        user.email,
        'classify-image',
        user.name
      );
      const binaryMax = Math.max(...binaryProbs);
      const binaryClassId = binaryProbs.indexOf(binaryMax);
      
      const binaryMap: Record<number, string> = {};
      Object.entries(metadata.binary_model.class_map).forEach(([k, v]) => {
        binaryMap[parseInt(k)] = v;
      });

      const binaryLabel = binaryMap[binaryClassId];

      if (binaryLabel === 'Eurygaster' && binaryMax > DEFAULT_CONFIG.binaryThreshold) {
        // Multiclass classification
        const multiclassProbs = await inferenceService.classifyEurygaster(
          file,
          user.email,
          'classify-eurygaster',
          user.name
        );
        const multiclassMax = Math.max(...multiclassProbs);
        const multiclassClassId = multiclassProbs.indexOf(multiclassMax);

        const multiclassMap: Record<number, string> = {};
        Object.entries(metadata.multiclass_model.class_map).forEach(([k, v]) => {
          multiclassMap[parseInt(k)] = v;
        });

        const classLabel = multiclassMap[multiclassClassId];

        const details: Record<string, number> = {};
        multiclassProbs.forEach((conf, idx) => {
          details[multiclassMap[idx]] = parseFloat(conf.toFixed(3));
        });

        setResult({
          details,
          recognized: true,
          class_name: classLabel,
          confidence: multiclassMax,
        });

        // Save entry (non-blocking - don't fail classification if this fails)
        try {
          const iconB64 = await imageToBase64Icon(file);
          await entriesService.addScore({
            score: multiclassMax,
            class_name: classLabel,
            icon_b64: iconB64,
          });
        } catch (saveError) {
          console.warn('Failed to save entry:', saveError);
          // Don't show error to user as classification was successful
        }
      } else {
        const details: Record<string, number> = {};
        binaryProbs.forEach((conf: number, idx: number) => {
          details[binaryMap[idx]] = parseFloat(conf.toFixed(3));
        });

        setResult({
          details,
          recognized: false,
        });
      }
    } catch (err) {
      if (err instanceof Error && err.message.includes('cancelled')) {
        return; // Don't show error for cancelled requests
      }
      console.error('Classification error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to classify image. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
      setIsClassifying(false);
    }
  };

  const chartData = result
    ? Object.entries(result.details)
        .map(([name, value]) => ({ name, value: value * 100 }))
        .sort((a, b) => b.value - a.value)
    : [];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">{t.nav.IDENTIFY}</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t.hints.ASK_IMAGE}
            </label>
            <div className="flex items-center justify-center w-full">
              <label 
                className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-primary-500"
                aria-label={t.hints.ASK_IMAGE}
              >
                {preview ? (
                  <img 
                    src={preview} 
                    alt="Image preview" 
                    className="max-h-full max-w-full object-contain rounded-lg"
                    role="img"
                    aria-label="Uploaded image preview"
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center pt-5 pb-6" role="presentation">
                    <Upload className="w-10 h-10 mb-3 text-gray-400" aria-hidden="true" />
                    <p className="mb-2 text-sm text-gray-500">
                      <span className="font-semibold">{t.hints.CLICK_TO_UPLOAD || 'Click to upload'}</span> {t.hints.OR_DRAG_DROP || 'or drag and drop'}
                    </p>
                    <p className="text-xs text-gray-500">{t.hints.FILE_FORMAT || 'JPEG or JPG (MAX. 50MB)'}</p>
                  </div>
                )}
                <input
                  type="file"
                  className="hidden"
                  accept="image/jpeg,image/jpg"
                  onChange={handleFileChange}
                  disabled={loading || isClassifying}
                  aria-label={t.hints.ASK_IMAGE}
                  aria-describedby="file-upload-description"
                />
                <span id="file-upload-description" className="sr-only">
                  {t.hints.FILE_FORMAT || 'JPEG or JPG (MAX. 50MB)'}
                </span>
              </label>
            </div>
          </div>

          {metadataLoading && (
            <div className="flex items-center justify-center p-4">
              <Loader2 className="animate-spin text-primary-600" size={24} />
              <span className="ml-2 text-gray-600">{t.hints.LOADING_METADATA || 'Loading metadata...'}</span>
            </div>
          )}

          {file && !metadataLoading && (
            <button
              onClick={handleClassify}
              disabled={loading || !metadata || isClassifying}
              className="w-full px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
              aria-label={t.hints.CLASSIFY_IMAGE || 'Classify Image'}
              aria-busy={isClassifying}
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  {t.hints.CLASSIFYING || 'Classifying...'}
                </>
              ) : (
                t.hints.CLASSIFY_IMAGE || 'Classify Image'
              )}
            </button>
          )}

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
              <XCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {result.recognized && result.class_name && result.confidence ? (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2 text-green-700">
                  <CheckCircle2 size={20} />
                  <span>
                    {t.hints.RECOGNIZED_AS
                      .replace('%s', result.class_name)
                      .replace(/%\.3f/g, result.confidence.toFixed(3))}
                  </span>
                </div>
              ) : (
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-center gap-2 text-yellow-700">
                  <XCircle size={20} />
                  <span>{t.hints.WAS_FILTERED}</span>
                </div>
              )}

              <div className="mt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">{t.hints.DETAILS || 'Details:'}</h3>
                <div className="bg-gray-50 p-4 rounded-lg mb-4">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                    {JSON.stringify(result.details, null, 2)}
                  </pre>
                </div>

                {chartData.length > 0 && (
                  <div className="mt-6">
                    <h4 className="text-md font-semibold text-gray-700 mb-3">
                      {result.recognized ? t.hints.CLASSIFIER_DESCR : t.hints.FILTER_DESCR}
                    </h4>
                    <ResponsiveContainer width="100%" height={400}>
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="name"
                          angle={-45}
                          textAnchor="end"
                          height={100}
                          interval={0}
                        />
                        <YAxis label={{ value: t.hints.CONFIDENCE_PERCENT || 'Confidence (%)', angle: -90, position: 'insideLeft' }} />
                        <Tooltip />
                        <Bar dataKey="value" fill="#0ea5e9" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

