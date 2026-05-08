import { Router } from 'express';
import { readFile, writeFile, mkdir } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '../..');
const STATE_PATH = path.join(ROOT, 'state', 'pipeline-state.json');

const INITIAL_STATE = {
  pipeline_version: '1.0',
  last_updated: new Date().toISOString(),
  tickets: {},
  global: { total_processed: 0, pending_review: 0 },
};

const router = Router();

async function readState() {
  try {
    const raw = await readFile(STATE_PATH, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return { ...INITIAL_STATE, last_updated: new Date().toISOString() };
  }
}

// GET /api/state
router.get('/', async (_req, res) => {
  try {
    const state = await readState();
    res.json(state);
  } catch (err) {
    console.error('GET /state:', err);
    res.status(500).json({ error: 'Errore lettura stato pipeline' });
  }
});

// PUT /api/state — aggiorna l'intero stato (usato da Claude Code tramite tool)
router.put('/', async (req, res) => {
  try {
    const body = req.body;
    if (!body || typeof body !== 'object') {
      return res.status(400).json({ error: 'Body JSON richiesto' });
    }

    // Validazione base dello schema
    if (!body.pipeline_version || !body.tickets || !body.global) {
      return res.status(400).json({ error: 'Schema stato non valido' });
    }

    const toSave = { ...body, last_updated: new Date().toISOString() };
    await mkdir(path.dirname(STATE_PATH), { recursive: true });
    await writeFile(STATE_PATH, JSON.stringify(toSave, null, 2), 'utf-8');
    res.json({ success: true, last_updated: toSave.last_updated });
  } catch (err) {
    console.error('PUT /state:', err);
    res.status(500).json({ error: 'Errore salvataggio stato' });
  }
});

// PATCH /api/state/tickets/:id — aggiorna solo un ticket
router.patch('/tickets/:id', async (req, res) => {
  try {
    const { id } = req.params;
    if (!/^[\w-]+$/.test(id)) {
      return res.status(400).json({ error: 'ID ticket non valido' });
    }

    const updates = req.body;
    const state = await readState();

    if (!state.tickets[id]) {
      state.tickets[id] = {
        status: 'unprocessed',
        classification_artifact: null,
        draft_artifact: null,
        steps_completed: [],
        current_step: null,
        errors: [],
      };
    }

    // Applica aggiornamenti parziali
    Object.assign(state.tickets[id], updates);

    // Ricalcola global
    const statuses = Object.values(state.tickets).map((t) => t.status);
    state.global.pending_review = statuses.filter((s) => s === 'draft-ready').length;
    state.global.total_processed = statuses.filter(
      (s) => ['draft-ready', 'approved', 'rejected'].includes(s)
    ).length;
    state.last_updated = new Date().toISOString();

    await writeFile(STATE_PATH, JSON.stringify(state, null, 2), 'utf-8');
    res.json({ success: true, ticket: state.tickets[id] });
  } catch (err) {
    console.error('PATCH /state/tickets/:id:', err);
    res.status(500).json({ error: 'Errore aggiornamento stato ticket' });
  }
});

export default router;
