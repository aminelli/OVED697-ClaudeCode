import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import ticketsRouter from './routes/tickets.js';
import artifactsRouter from './routes/artifacts.js';
import stateRouter from './routes/state.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3001;

// CORS — consenti richieste dal frontend Angular in sviluppo
app.use(cors({ origin: ['http://localhost:4200', 'http://127.0.0.1:4200'] }));
app.use(express.json());

// API routes
app.use('/api/tickets', ticketsRouter);
app.use('/api/artifacts', artifactsRouter);
app.use('/api/state', stateRouter);

// Health check
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// In produzione: servi la build Angular
if (process.env.NODE_ENV === 'production') {
  const frontendDist = path.resolve(__dirname, '../frontend/dist/frontend/browser');
  app.use(express.static(frontendDist));
  app.get('*', (_req, res) => {
    res.sendFile(path.join(frontendDist, 'index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`\n Backend API  → http://localhost:${PORT}/api`);
  console.log(`  Health check → http://localhost:${PORT}/api/health`);
  console.log(`  State API    → http://localhost:${PORT}/api/state\n`);
});
