import { Router } from 'express';
import { readdir, readFile, writeFile, access, mkdir } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import matter from 'gray-matter';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '../..');

const router = Router();

// --- helpers ---

async function readArtifact(filePath) {
  try {
    await access(filePath);
    const raw = await readFile(filePath, 'utf-8');
    const { data, content } = matter(raw);
    return { frontmatter: data, body: content.trim() };
  } catch {
    return null;
  }
}

function deriveStatus(classification, draft) {
  if (draft) return draft.frontmatter['artifact:status'] || 'draft-ready';
  if (classification) return 'classified';
  return 'unprocessed';
}

const PRIORITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };

// --- GET /api/tickets ---
router.get('/', async (_req, res) => {
  try {
    const ticketsDir = path.join(ROOT, 'tickets');
    const files = await readdir(ticketsDir);
    const txtFiles = files.filter((f) => f.endsWith('.txt'));

    const tickets = await Promise.all(
      txtFiles.map(async (filename) => {
        const id = filename.replace('.txt', '');
        const content = await readFile(path.join(ticketsDir, filename), 'utf-8');

        const classification = await readArtifact(
          path.join(ROOT, 'artifacts', 'classifications', `${id}_classification.md`)
        );
        const draft = await readArtifact(
          path.join(ROOT, 'artifacts', 'drafts', `${id}_draft.md`)
        );

        return {
          id,
          content,
          classification: classification ? { ...classification.frontmatter } : null,
          draft: draft ? { ...draft.frontmatter, body: draft.body } : null,
          status: deriveStatus(classification, draft),
        };
      })
    );

    // Ordina: prima per priorità (critical → low), poi per id
    tickets.sort((a, b) => {
      const pa = PRIORITY_ORDER[a.classification?.['artifact:priority']] ?? 9;
      const pb = PRIORITY_ORDER[b.classification?.['artifact:priority']] ?? 9;
      return pa - pb || a.id.localeCompare(b.id);
    });

    res.json(tickets);
  } catch (err) {
    console.error('GET /tickets:', err);
    res.status(500).json({ error: 'Errore lettura ticket' });
  }
});

// --- GET /api/tickets/:id ---
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    // Validate id to prevent path traversal
    if (!/^[\w-]+$/.test(id)) {
      return res.status(400).json({ error: 'ID ticket non valido' });
    }

    const ticketPath = path.join(ROOT, 'tickets', `${id}.txt`);
    const content = await readFile(ticketPath, 'utf-8');

    const classification = await readArtifact(
      path.join(ROOT, 'artifacts', 'classifications', `${id}_classification.md`)
    );
    const draft = await readArtifact(
      path.join(ROOT, 'artifacts', 'drafts', `${id}_draft.md`)
    );

    res.json({
      id,
      content,
      classification: classification ? { ...classification.frontmatter } : null,
      draft: draft ? { ...draft.frontmatter, body: draft.body } : null,
      status: deriveStatus(classification, draft),
    });
  } catch (err) {
    if (err.code === 'ENOENT') return res.status(404).json({ error: 'Ticket non trovato' });
    console.error('GET /tickets/:id:', err);
    res.status(500).json({ error: 'Errore lettura ticket' });
  }
});

// --- PUT /api/tickets/:id/draft — salva bozza modificata ---
router.put('/:id/draft', async (req, res) => {
  try {
    const { id } = req.params;
    if (!/^[\w-]+$/.test(id)) {
      return res.status(400).json({ error: 'ID ticket non valido' });
    }

    const { body } = req.body;
    if (typeof body !== 'string') {
      return res.status(400).json({ error: 'Campo body richiesto' });
    }

    const draftPath = path.join(ROOT, 'artifacts', 'drafts', `${id}_draft.md`);
    const existing = await readArtifact(draftPath);
    if (!existing) return res.status(404).json({ error: 'Bozza non trovata' });

    // Ricostruisce il file con frontmatter invariato e body aggiornato
    const updated = matter.stringify(body, existing.frontmatter);
    await writeFile(draftPath, updated, 'utf-8');

    res.json({ success: true });
  } catch (err) {
    console.error('PUT /tickets/:id/draft:', err);
    res.status(500).json({ error: 'Errore salvataggio bozza' });
  }
});

// --- POST /api/tickets/:id/approve ---
router.post('/:id/approve', async (req, res) => {
  try {
    const { id } = req.params;
    if (!/^[\w-]+$/.test(id)) {
      return res.status(400).json({ error: 'ID ticket non valido' });
    }

    const { body } = req.body;
    const draftPath = path.join(ROOT, 'artifacts', 'drafts', `${id}_draft.md`);
    const existing = await readArtifact(draftPath);
    if (!existing) return res.status(404).json({ error: 'Bozza non trovata' });

    const updatedFrontmatter = {
      ...existing.frontmatter,
      'artifact:status': 'approved',
      'artifact:approved-at': new Date().toISOString(),
    };

    const updated = matter.stringify(typeof body === 'string' ? body : existing.body, updatedFrontmatter);
    await writeFile(draftPath, updated, 'utf-8');

    // Aggiorna pipeline state
    await updatePipelineState(id, 'approved', 'approve');

    res.json({ success: true });
  } catch (err) {
    console.error('POST /tickets/:id/approve:', err);
    res.status(500).json({ error: 'Errore approvazione' });
  }
});

// --- POST /api/tickets/:id/reject ---
router.post('/:id/reject', async (req, res) => {
  try {
    const { id } = req.params;
    if (!/^[\w-]+$/.test(id)) {
      return res.status(400).json({ error: 'ID ticket non valido' });
    }

    const { reason = '' } = req.body;
    const draftPath = path.join(ROOT, 'artifacts', 'drafts', `${id}_draft.md`);
    const existing = await readArtifact(draftPath);
    if (!existing) return res.status(404).json({ error: 'Bozza non trovata' });

    const updatedFrontmatter = {
      ...existing.frontmatter,
      'artifact:status': 'rejected',
      'artifact:rejected-at': new Date().toISOString(),
      'artifact:reject-reason': reason,
    };

    const updated = matter.stringify(existing.body, updatedFrontmatter);
    await writeFile(draftPath, updated, 'utf-8');

    await updatePipelineState(id, 'rejected');

    res.json({ success: true });
  } catch (err) {
    console.error('POST /tickets/:id/reject:', err);
    res.status(500).json({ error: 'Errore rifiuto bozza' });
  }
});

// --- helper: aggiorna state ---
async function updatePipelineState(ticketId, newStatus, stepCompleted) {
  try {
    const statePath = path.join(ROOT, 'state', 'pipeline-state.json');
    let state;
    try {
      const raw = await readFile(statePath, 'utf-8');
      state = JSON.parse(raw);
    } catch {
      return; // se lo state non esiste, non bloccare
    }

    if (!state.tickets[ticketId]) {
      state.tickets[ticketId] = {
        status: newStatus,
        classification_artifact: null,
        draft_artifact: null,
        steps_completed: [],
        current_step: null,
        errors: [],
      };
    } else {
      state.tickets[ticketId].status = newStatus;
    }

    if (stepCompleted && !state.tickets[ticketId].steps_completed.includes(stepCompleted)) {
      state.tickets[ticketId].steps_completed.push(stepCompleted);
    }

    // Ricalcola global stats
    const statuses = Object.values(state.tickets).map((t) => t.status);
    state.global.pending_review = statuses.filter((s) => s === 'draft-ready').length;
    state.global.total_processed = statuses.filter(
      (s) => ['draft-ready', 'approved', 'rejected'].includes(s)
    ).length;
    state.last_updated = new Date().toISOString();

    await writeFile(statePath, JSON.stringify(state, null, 2), 'utf-8');
  } catch (e) {
    console.error('updatePipelineState error:', e);
  }
}

export default router;
