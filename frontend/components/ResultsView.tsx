// src/components/ResultsView.tsx
import React from 'react';
import type { PipelineResult } from '../types';

interface ResultsViewProps {
  result: PipelineResult;
  originalVideoUrl: string;
  editedVideoUrl: string;
  onReset: () => void;
}

const InfoCard: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="bg-slate-800 rounded-lg p-4 shadow-md h-full">
    <h3 className="text-lg font-semibold text-indigo-400 mb-2">{title}</h3>
    {children}
  </div>
);

export const ResultsView: React.FC<ResultsViewProps> = ({ result, originalVideoUrl, editedVideoUrl, onReset }) => {
  // Fallback sicuri se result.plan è null/undefined
  const plan = result.plan || {
    mood: "N/A",
    music: "N/A",
    color: "N/A",
    caption: "",
    fx: []
  };

  return (
    <div className="w-full animate-fade-in pb-10">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-2xl font-bold mb-4 text-center">Video Originale</h2>
          <video src={originalVideoUrl} controls className="w-full rounded-lg shadow-2xl bg-black"></video>
        </div>
        <div>
          <h2 className="text-2xl font-bold mb-4 text-center">Video Montato</h2>
          <video src={editedVideoUrl} controls className="w-full rounded-lg shadow-2xl border-2 border-indigo-500 bg-black"></video>
        </div>
      </div>

      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
        <InfoCard title="Dettagli Montaggio">
          <ul className="space-y-2 text-slate-300">
            <li><strong>Mood:</strong> {plan.mood}</li>
            <li><strong>Musica:</strong> {plan.music}</li>
            <li><strong>Color:</strong> {plan.color}</li>
            {plan.caption && <li><strong>Caption:</strong> "{plan.caption}"</li>}
            {plan.fx.length > 0 && (
              <li>
                <strong>Effetti:</strong>
                <div className="flex flex-wrap gap-2 mt-1">
                  {plan.fx.map((effect, i) => (
                    <span key={i} className="bg-slate-700 text-xs font-medium px-2.5 py-1 rounded-full">{effect}</span>
                  ))}
                </div>
              </li>
            )}
          </ul>
        </InfoCard>

        <InfoCard title="Trascrizione">
           <p className="text-slate-300 text-sm leading-relaxed max-h-48 overflow-y-auto pr-2">
            {result.transcript || "Trascrizione non disponibile per questa clip."}
          </p>
        </InfoCard>
      </div>
      
      <div className="text-center mt-12">
        <button
          onClick={onReset}
          className="bg-slate-600 text-white font-bold py-3 px-8 rounded-lg hover:bg-slate-700 transition-all duration-300 shadow-lg text-xl"
        >
          Monta un Altro Video
        </button>
      </div>
    </div>
  );
};