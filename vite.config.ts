import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// База под GitHub Pages: сайт живёт на /instrukciya-k-mechte/preview/, пока корень занят макетом.
// В dev-режиме база корневая, чтобы локальные URL оставались простыми.
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/instrukciya-k-mechte/preview/' : '/',
  plugins: [react()]
}));
