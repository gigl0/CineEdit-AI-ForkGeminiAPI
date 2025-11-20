import React from 'react';
import type { AnalysisResult, NarrativeSection } from '../types';

interface EpisodeEditorViewProps {
  originalVideoUrl: string;
  analysisResult: AnalysisResult;
  onEditSection: (section: NarrativeSection) => void;
  onReset: () => void;
}

// Helper interno per le card (non serve exportarlo)
const SectionCard: React.FC<{ section: NarrativeSection; onSelect: () => void }> = ({ section, onSelect }) => (
  <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 hover:border-indigo-500 transition-all duration-300 mb-4">
    <h3 className="font-bold text-lg text-white">{section.title}</h3>
    <p className="text-slate-400 text-sm mt-1 mb-3">{section.summary}</p>
    <div className="flex flex-wrap gap-2 mb-4">
      {section.keywords.map(kw => (
        <span key={kw} className="bg-slate-700 text-xs font-medium px-2 py-0.5 rounded-full">{kw}</span>
      ))}
    </div>
    <button
      onClick={onSelect}
      className="w-full bg-indigo-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors"
    >
      Crea Reel
    </button>
  </div>
);

// === QUESTA È LA PARTE CHE CAUSAVA L'ERRORE ===
// Assicurati che ci sia "export const" e non "export default" o solo "const"
export const EpisodeEditorView: React.FC<EpisodeEditorViewProps> = ({
  originalVideoUrl,
  analysisResult,
  onEditSection,
  onReset
}) => {
  return (
    <div className="w-full animate-fade-in pb-10">
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        
        {/* Colonna Sinistra: Video Player */}
        <div className="lg:col-span-3">
          <h2 className="text-2xl font-bold mb-4 text-center text-white">Episodio Originale</h2>
          <div className="sticky top-4">
             <video 
               src={originalVideoUrl} 
               controls 
               className="w-full rounded-lg shadow-2xl bg-black border border-slate-700"
             >
             </video>
          </div>
        </div>

        {/* Colonna Destra: Lista Scene */}
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-bold mb-4 text-center text-white">Scene AI</h2>
          <div className="max-h-[70vh] overflow-y-auto pr-2">
            {analysisResult.narrative_sections.length === 0 ? (
              <p className="text-slate-500 text-center">Nessuna scena identificata.</p>
            ) : (
              analysisResult.narrative_sections.map((section, index) => (
                <SectionCard 
                  key={index} 
                  section={section} 
                  onSelect={() => onEditSection(section)} 
                />
              ))
            )}
          </div>
        </div>
      </div>
      
      <div className="text-center mt-12">
        <button
          onClick={onReset}
          className="bg-slate-700 text-white font-bold py-3 px-8 rounded-lg hover:bg-slate-600 transition-all"
        >
          Carica un Altro Episodio
        </button>
      </div>
    </div>
  );
};