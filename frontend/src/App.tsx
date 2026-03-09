import { useEffect, useMemo, useState } from 'react';
import { createTranslationJob, fetchJob, fetchLanguages, resolveAssetUrl } from './api';
import type { JobDetailResponse, LanguageOption } from './types';

function App() {
  const [languages, setLanguages] = useState<LanguageOption[]>([]);
  const [sourceLanguage, setSourceLanguage] = useState('en');
  const [targetLanguage, setTargetLanguage] = useState('hi');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [speakerFile, setSpeakerFile] = useState<File | null>(null);
  const [job, setJob] = useState<JobDetailResponse | null>(null);
  const [jobId, setJobId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    async function loadLanguages() {
      try {
        const data = await fetchLanguages();
        setLanguages(data.source_languages);
      } catch {
        setError('Could not load language options. Ensure backend is running.');
      }
    }

    loadLanguages();
  }, []);

  useEffect(() => {
    if (!jobId) {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const latest = await fetchJob(jobId);
        setJob(latest);
        if (latest.status === 'completed' || latest.status === 'failed') {
          clearInterval(interval);
        }
      } catch {
        setError('Polling failed. Please retry.');
        clearInterval(interval);
      }
    }, 1800);

    return () => clearInterval(interval);
  }, [jobId]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!videoFile) {
      setError('Upload a source video first.');
      return;
    }

    setError('');
    setLoading(true);
    setJob(null);

    try {
      const created = await createTranslationJob({
        sourceLanguage,
        targetLanguage,
        videoFile,
        speakerFile: speakerFile ?? undefined,
      });

      setJobId(created.job_id);
      const current = await fetchJob(created.job_id);
      setJob(current);
    } catch {
      setError('Job creation failed. Check backend logs for details.');
    } finally {
      setLoading(false);
    }
  }

  const progressPct = useMemo(() => {
    if (!job) return 0;
    return Math.round((job.progress ?? 0) * 100);
  }, [job]);

  return (
    <main className="shell">
      <section className="hero-card">
        <h1>Multilingual Deepfake Translator</h1>
        <p className="subtitle">
          Upload any talking-head video, translate speech with NLLB-200, and generate a synced output clip with Wav2Lip.
        </p>
      </section>

      <section className="panel">
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Source Language
            <select value={sourceLanguage} onChange={(e) => setSourceLanguage(e.target.value)}>
              {languages.map((lang) => (
                <option key={`src-${lang.code}`} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Target Language
            <select value={targetLanguage} onChange={(e) => setTargetLanguage(e.target.value)}>
              {languages.map((lang) => (
                <option key={`tgt-${lang.code}`} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </label>

          <label className="upload-row">
            Source Video
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setVideoFile(e.target.files?.[0] ?? null)}
              required
            />
          </label>

          <label className="upload-row">
            Speaker Reference Audio (Optional)
            <input
              type="file"
              accept="audio/wav,audio/*"
              onChange={(e) => setSpeakerFile(e.target.files?.[0] ?? null)}
            />
          </label>

          <button disabled={loading} type="submit">
            {loading ? 'Submitting...' : 'Translate Video'}
          </button>
        </form>

        {error && <p className="error">{error}</p>}
      </section>

      <section className="panel">
        <h2>Pipeline Status</h2>
        {!job && <p className="muted">No job yet. Submit a video to begin.</p>}

        {job && (
          <div className="status">
            <p>
              <strong>Job:</strong> <code>{job.job_id}</code>
            </p>
            <p>
              <strong>Status:</strong> {job.status}
            </p>
            <div className="progress-track">
              <div className="progress-bar" style={{ width: `${progressPct}%` }} />
            </div>
            <p>{progressPct}% complete</p>

            {job.transcript && (
              <p>
                <strong>Transcript:</strong> {job.transcript}
              </p>
            )}

            {job.translated_text && (
              <p>
                <strong>Translated:</strong> {job.translated_text}
              </p>
            )}

            {job.error && (
              <p className="error">
                <strong>Error:</strong> {job.error}
              </p>
            )}

            {job.output_url && (
              <div className="result">
                <video controls src={resolveAssetUrl(job.output_url)} />
                <a href={resolveAssetUrl(job.output_url)} target="_blank" rel="noreferrer">
                  Download translated video
                </a>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}

export default App;
