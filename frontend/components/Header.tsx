import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="text-center w-full">
      <h1 className="text-4xl sm:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-600">
        CineEdit-AI
      </h1>
      <p className="mt-2 text-lg text-slate-400">
        Il tuo assistente di montaggio video potenziato dall'intelligenza artificiale.
      </p>
    </header>
  );
};
