import React from 'react';
import type { PipelineResult } from '../types';

interface ResultsViewProps {
  result: PipelineResult;
  originalVideoUrl: string;
  editedVideoUrl: string;
  onReset: () => void;        // Pulsante "Nuovo Progetto"
  onBackToScenes: () => void; // NUOVO: Pulsante "Scegli altra scena"
}

const InfoCard: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="bg-slate-800 rounded-lg p-4 shadow-md h-full border border-slate-700">
    <h3 className="text-lg font-semibold text-indigo-400 mb-2">{title}</h3>
    {children}
  </div>
);

export const ResultsView: React.FC<ResultsViewProps> = ({ 
  result, originalVideoUrl, editedVideoUrl, onReset, onBackToScenes 
}) => {
  const plan = result.plan || { mood: "N/A", music: "N/A", color: "N/A", caption: "", fx: [] };

  return (
    <div className="w-full animate-fade-in pb-10">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-bold mb-4 text-center text-slate-300">Video Originale</h2>
          <video src={originalVideoUrl} controls className="w-full rounded-lg shadow-xl bg-black aspect-video"></video>
        </div>
        <div>
          <h2 className="text-xl font-bold mb-4 text-center text-indigo-400">✨ Reel Generato</h2>
          <div className="flex justify-center">
            <video src={editedVideoUrl} controls autoPlay loop className="h-[500px] rounded-lg shadow-2xl border-4 border-indigo-600 bg-black"></video>
          </div>
        </div>
      </div>

      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
        <InfoCard title="Dettagli Reel">
          <ul className="space-y-2 text-slate-300 text-sm">
            <li><span className="text-slate-500">Titolo:</span> {plan.caption}</li>
            <li><span className="text-slate-500">Musica:</span> {plan.music}</li>
            <li><span className="text-slate-500">Effetti:</span> {plan.fx.join(", ")}</li>
          </ul>
        </InfoCard>

        <InfoCard title="Contenuto">
           <p className="text-slate-300 text-sm leading-relaxed italic">
            "{result.transcript}"
          </p>
        </InfoCard>
      </div>
      
      {/* PULSANTIERA */}
      <div className="flex flex-col sm:flex-row justify-center gap-6 mt-12">
        <button
          onClick={onBackToScenes}
          className="bg-slate-700 text-white font-bold py-3 px-8 rounded-lg hover:bg-slate-600 transition-all shadow-lg flex items-center justify-center gap-2"
        >
          ⬅ Scegli un'altra scena
        </button>

        <button
          onClick={onReset}
          className="bg-indigo-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-indigo-500 transition-all shadow-lg flex items-center justify-center gap-2"
        >
           Carica Nuovo Episodio
        </button>
      </div>
    </div>
  );
};