import React, { useRef } from 'react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  children?: React.ReactNode;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, children }) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) onFileSelect(e.target.files[0]);
  };

  return (
    <div className="flex flex-col items-center w-full">
      <div 
        className="w-full max-w-xl p-10 border-2 border-dashed border-slate-600 rounded-xl hover:border-indigo-500 cursor-pointer bg-slate-800 text-center"
        onClick={() => inputRef.current?.click()}
      >
        <input ref={inputRef} type="file" accept="video/*" onChange={handleChange} className="hidden" />
        <p className="text-xl font-bold text-slate-200">Clicca per caricare un video</p>
        <p className="text-sm text-slate-400 mt-2">Formati supportati: MP4, MOV</p>
      </div>
      {children}
    </div>
  );
};