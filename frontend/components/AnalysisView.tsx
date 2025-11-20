// src/components/AnalysisView.tsx
import React, { useEffect, useState } from 'react';
import type { JobStatusResponse, AnalysisResult } from '../types';
import { ProcessingIndicator } from './ProcessingIndicator';

interface AnalysisViewProps {
  jobId: string;
  onAnalysisComplete: (result: AnalysisResult) => void;
  onError: (errorMessage: string) => void;
}

export const AnalysisView: React.FC<AnalysisViewProps> = ({ jobId, onAnalysisComplete, onError }) => {
  const [statusMessage, setStatusMessage] = useState("Avvio dell'analisi del tuo video...");

  useEffect(() => {
    const pollStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/episodes/status/${jobId}`);
        if (!response.ok) {
          throw new Error('Impossibile ottenere lo stato del job.');
        }
        const data: JobStatusResponse = await response.json();

        switch (data.status) {
          case 'analyzed':
            if (data.results) {
              onAnalysisComplete(data.results);
            } else {
              throw new Error("L'analisi è completata ma non ci sono risultati.");
            }
            break;
          case 'error':
            throw new Error(data.error || 'Si è verificato un errore durante l analisi.');
          case 'processing':
            setStatusMessage("Analisi in corso... Rilevamento scene e trascrizione audio. Potrebbe richiedere diversi minuti.");
            break;
          default:
            setStatusMessage("Il tuo video è in coda per l'elaborazione...");
            break;
        }
      } catch (err: any) {
        onError(err.message);
      }
    };

    // Fai polling ogni 7 secondi
    const intervalId = setInterval(pollStatus, 7000);

    // Pulisci l'intervallo quando il componente viene smontato
    return () => clearInterval(intervalId);
  }, [jobId, onAnalysisComplete, onError]);

  return <ProcessingIndicator message={statusMessage} />;
};