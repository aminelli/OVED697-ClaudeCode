import { Router } from 'express';
import { readdir, readFile } from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import matter from 'gray-matter';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '../..');
const router = Router();

// GET /api/artifacts — lista tutti gli artifact
router.get('/', async (_req, res) => {
  try {
    const dirs = ['classifications', 'drafts'];
    const all = [];

    for (const dir of dirs) {
      const dirPath = path.join(ROOT, 'artifacts', dir);
      try {
        const files = await readdir(dirPath);
        for (const f of files.filter((f) => f.endsWith('.md'))) {
          const raw = await readFile(path.join(dirPath, f), 'utf-8');
          const { data } = matter(raw);
          all.push({ type: dir, filename: f, frontmatter: data });
        }
      } catch { /* dir vuota */ }
    }

    res.json(all);
  } catch (err) {
    res.status(500).json({ error: 'Errore lettura artifact' });
  }
});

export default router;
