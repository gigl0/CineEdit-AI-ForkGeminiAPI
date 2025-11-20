import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { FileUpload } from './components/FileUpload';
import { ProcessingIndicator } from './components/ProcessingIndicator';
import { ResultsView } from './components/ResultsView';
import { ErrorDisplay } from './components/ErrorDisplay';
import { AnalysisView } from './components/AnalysisView';
import { EpisodeEditorView } from './components/EpisodeEditorView';
import type { AnalysisResult, NarrativeSection, PipelineResult } from './types';

type AppState = 'idle' | 'analyzing' | 'ready_to_edit' | 'editing_clip' | 'clip_ready' | 'error';

const App: React.FC = () => {
  console.log("App Rendering..."); 

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
    console.log("File selezionato:", file.name);
    if (originalVideoUrl) URL.revokeObjectURL(originalVideoUrl);
    setVideoFile(file);
    setOriginalVideoUrl(URL.createObjectURL(file));
    setAppState('idle');
    setError(null);
  }, [originalVideoUrl]);

  const uploadAndAnalyze = async () => {
    console.log("Click su Analizza");
    if (!videoFile) return;
    setAppState('analyzing');
    
    const formData = new FormData();
    formData.append('file', videoFile);

    try {
      const response = await fetch('http://localhost:8000/episodes/upload_and_analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Errore connessione Backend');
      const data = await response.json();
      console.log("Upload OK, JobID:", data.job_id);
      setJobId(data.job_id);
    } catch (err: any) {
      console.error("Errore Upload:", err);
      setError(err.message || "Errore Backend");
      setAppState('error');
    }
  };

  const handleAnalysisComplete = (result: AnalysisResult) => {
    console.log("Analisi completata:", result);
    setAnalysisResult(result);
    setAppState('ready_to_edit');
  };
  
  const handleEditSection = async (section: NarrativeSection) => {
    console.log("Avvio creazione clip reale per:", section.title);
    
    setAppState('editing_clip');
    setProcessingMessage(`Generazione Reel: "${section.title}"... (Taglio, Crop 9:16, Sottotitoli)`);
    
    try {
      const response = await fetch('http://localhost:8000/episodes/create_clip', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_job_id: jobId,
          start_sec: section.start_sec,
          end_sec: section.end_sec,
          title: section.title,
          style: "cinematic",         
          music: "ambient"
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: "Errore sconosciuto" }));
        throw new Error(errData.detail || "Errore durante la creazione della clip");
      }

      const result = await response.json();
      console.log("Clip creata:", result);

      const realVideoUrl = `http://localhost:8000${result.output_video}`;
      
      setFinalClipUrl(realVideoUrl); 
      
      setFinalResultData({
          ok: true,
          video_path: videoFile?.name || "video.mp4",
          transcript: section.summary, 
          output_video: result.output_video,
          plan: {
            mood: section.keywords.join(", "),
            music: "Ambient Mix",
            caption: section.title,
            fx: ["9:16 Vertical Crop", "Blur Background", "Auto-Subtitles"],
            color: "Standard"
          }
      });

      setAppState('clip_ready');

    } catch (e: any) {
      console.error("Errore creazione clip:", e);
      setError(e.message || "Impossibile creare la clip. Controlla i log del backend.");
      setAppState('error');
    }
  };

  // --- NUOVA FUNZIONE ---
  const handleBackToScenes = () => {
    console.log("Torno alla selezione scene...");
    // Non resettiamo analysisResult o originalVideoUrl!
    // Resettiamo solo il risultato finale della clip
    setFinalClipUrl(null);
    setFinalResultData(null);
    
    // Torniamo allo stato precedente
    setAppState('ready_to_edit');
  };
  // ----------------------

  const handleReset = () => {
    console.log("Reset totale...");
    setAppState('idle');
    setVideoFile(null);
    if (originalVideoUrl) URL.revokeObjectURL(originalVideoUrl);
    setOriginalVideoUrl(null);
    setJobId(null);
    setAnalysisResult(null);
    setFinalClipUrl(null);
    setFinalResultData(null);
    setError(null);
  };

  // RENDERING
  return (
    <div className="min-h-screen bg-slate-900 text-white p-4 flex flex-col items-center">
      <Header />
      
      <main className="w-full max-w-6xl mt-8 border border-slate-800 p-4 rounded bg-slate-800/50">
        
        {/* ... Error e Processing rimangono uguali ... */}
        {appState === 'error' && <ErrorDisplay message={error || "Errore"} onReset={handleReset} />}
        
        {/* ... AnalysisView rimane uguale ... */}
        {appState === 'analyzing' && jobId && (
            <AnalysisView jobId={jobId} onAnalysisComplete={handleAnalysisComplete} onError={(e) => setError(e)} />
        )}
        
        {/* ... EpisodeEditorView rimane uguale ... */}
        {appState === 'ready_to_edit' && analysisResult && originalVideoUrl && (
            <EpisodeEditorView 
                originalVideoUrl={originalVideoUrl} 
                analysisResult={analysisResult} 
                onEditSection={handleEditSection} 
                onReset={handleReset} 
            />
        )}

        {/* ... ProcessingIndicator rimane uguale ... */}
        {appState === 'editing_clip' && <ProcessingIndicator message={processingMessage} />}

        {/* MODIFICATO: ResultsView ora riceve handleBackToScenes */}
        {appState === 'clip_ready' && finalResultData && originalVideoUrl && finalClipUrl && (
            <ResultsView 
                result={finalResultData} 
                originalVideoUrl={originalVideoUrl} 
                editedVideoUrl={finalClipUrl} 
                onReset={handleReset} 
                onBackToScenes={handleBackToScenes} // <--- ECCOLO
            />
        )}

        {/* ... FileUpload rimane uguale ... */}
        {appState === 'idle' && (
            <FileUpload onFileSelect={handleFileSelect}>
                {videoFile && (
                    <div className="mt-6 text-center">
                        <p className="mb-4 text-green-400">Video caricato: {videoFile.name}</p>
                        <button onClick={uploadAndAnalyze} className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 px-6 rounded">
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