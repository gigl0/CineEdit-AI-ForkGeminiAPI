import React, { useState, useCallback, useEffect } from 'react';
import { Header } from './components/Header';
import { FileUpload } from './components/FileUpload';
import { ProcessingIndicator } from './components/ProcessingIndicator';
import { ResultsView } from './components/ResultsView';
import { ErrorDisplay } from './components/ErrorDisplay';
import { AnalysisView } from './components/AnalysisView';
import { EpisodeEditorView } from './components/EpisodeEditorView';
import type { AnalysisResult, NarrativeSection, PipelineResult } from './types'; // NOTA: ./types non ../types

type AppState = 'idle' | 'analyzing' | 'ready_to_edit' | 'editing_clip' | 'clip_ready' | 'error';

const App: React.FC = () => {
  console.log("App Rendering..."); // DEBUG

  const [appState, setAppState] = useState<AppState>('idle');
  const [processingMessage, setProcessingMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [originalVideoUrl, setOriginalVideoUrl] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [finalClipUrl, setFinalClipUrl] = useState<string | null>(null);
  const [finalResultData, setFinalResultData] = useState<PipelineResult | null>(null);

  const handleFileSelect = useCallback((file: File) => {
    console.log("File selezionato:", file.name); // DEBUG
    if (originalVideoUrl) URL.revokeObjectURL(originalVideoUrl);
    setVideoFile(file);
    setOriginalVideoUrl(URL.createObjectURL(file));
    setAppState('idle');
    setError(null);
  }, [originalVideoUrl]);

  const uploadAndAnalyze = async () => {
    console.log("Click su Analizza"); // DEBUG
    if (!videoFile) return;
    setAppState('analyzing');
    
    const formData = new FormData();
    formData.append('file', videoFile);

    try {
      // NOTA: Assicurati che il backend sia acceso su localhost:8000
      const response = await fetch('http://localhost:8000/episodes/upload_and_analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Errore connessione Backend');
      const data = await response.json();
      console.log("Upload OK, JobID:", data.job_id); // DEBUG
      setJobId(data.job_id);
    } catch (err: any) {
      console.error("Errore Upload:", err);
      setError(err.message || "Errore Backend");
      setAppState('error');
    }
  };

  const handleAnalysisComplete = (result: AnalysisResult) => {
    console.log("Analisi completata:", result); // DEBUG
    setAnalysisResult(result);
    setAppState('ready_to_edit');
  };
  
  const handleEditSection = async (section: NarrativeSection) => {
    console.log("Editing sezione:", section.title); // DEBUG
    setAppState('editing_clip');
    setProcessingMessage(`Creo clip: ${section.title}...`);
    
    // Simulazione attesa
    setTimeout(() => {
        const mockUrl = "http://localhost:8000/output/demo.mp4"; 
        setFinalClipUrl(mockUrl);
        setFinalResultData({
            ok: true,
            video_path: "demo",
            transcript: "demo text",
            output_video: mockUrl,
            plan: { mood: "Epic", music: "Rock", caption: section.title, fx: [], color: "Warm" }
        });
        setAppState('clip_ready');
    }, 2000);
  };

  const handleReset = () => {
    setAppState('idle');
    setVideoFile(null);
    setOriginalVideoUrl(null);
    setJobId(null);
    setAnalysisResult(null);
    setFinalClipUrl(null);
    setError(null);
  };

  // RENDERING CONDIZIONALE SEMPLIFICATO
  return (
    <div className="min-h-screen bg-slate-900 text-white p-4 flex flex-col items-center">
      <Header />
      
      <main className="w-full max-w-6xl mt-8 border border-slate-800 p-4 rounded bg-slate-800/50">
        
        {/* DEBUG STATE VISUALIZER (Rimuovere in produzione) */}
        <div className="text-xs text-slate-500 mb-4 text-center">
            Stato: {appState} | File: {videoFile ? 'Sì' : 'No'}
        </div>

        {appState === 'error' && (
            <ErrorDisplay message={error || "Errore"} onReset={handleReset} />
        )}

        {appState === 'analyzing' && jobId && (
            <AnalysisView jobId={jobId} onAnalysisComplete={handleAnalysisComplete} onError={(e) => setError(e)} />
        )}
        
        {appState === 'ready_to_edit' && analysisResult && originalVideoUrl && (
            <EpisodeEditorView 
                originalVideoUrl={originalVideoUrl} 
                analysisResult={analysisResult} 
                onEditSection={handleEditSection} 
                onReset={handleReset} 
            />
        )}

        {appState === 'editing_clip' && (
            <ProcessingIndicator message={processingMessage} />
        )}

        {appState === 'clip_ready' && finalResultData && originalVideoUrl && finalClipUrl && (
            <ResultsView 
                result={finalResultData} 
                originalVideoUrl={originalVideoUrl} 
                editedVideoUrl={finalClipUrl} 
                onReset={handleReset} 
            />
        )}

        {/* DEFAULT VIEW: UPLOAD */}
        {appState === 'idle' && (
            <FileUpload onFileSelect={handleFileSelect}>
                {videoFile && (
                    <div className="mt-6 text-center">
                        <p className="mb-4 text-green-400">Video caricato: {videoFile.name}</p>
                        <button 
                            onClick={uploadAndAnalyze}
                            className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 px-6 rounded"
                        >
                            AVVIA ANALISI
                        </button>
                    </div>
                )}
            </FileUpload>
        )}

      </main>
    </div>
  );
};

export default App;