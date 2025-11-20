// frontend/types.ts

// --- Tipi per l'Analisi Episodio (Nuovo Flusso) ---

export interface NarrativeSection {
  title: string;
  summary: string;
  start_sec: number;
  end_sec: number;
  keywords: string[];
}

export interface AnalysisResult {
  narrative_sections: NarrativeSection[];
  full_transcript?: string;
}

// QUESTA È L'INTERFACCIA CHE MANCAVA
export interface JobStatusResponse {
  job_id: string;
  status: 'queued' | 'processing' | 'analyzed' | 'error';
  results: AnalysisResult | null;
  error: string | null;
}

// --- Tipi per l'Editing Clip (Vecchio Flusso / Clip Finale) ---

export interface EditPlan {
  mood: string;
  music: string;
  caption: string;
  fx: string[];
  color: string;
}

export interface PipelineResult {
  ok: boolean;
  video_path: string;
  transcript: string;
  plan: EditPlan;
  output_video: string;
}

export interface ClipResult {
  ok: boolean;
  output_video: string;
}