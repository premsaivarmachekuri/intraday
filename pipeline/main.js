'use strict';

require('dotenv').config();
const path = require('path');
const { initDb } = require('./data/db');
const { fetchAll } = require('./data/fetcher');

const DB_PATH = path.resolve(__dirname, process.env.DB_PATH || 'data/market.db');
const SYMBOLS_DIR = path.resolve(__dirname, 'symbols');

const args = process.argv.slice(2);
const limitIdx = args.indexOf('--limit');
const limit = limitIdx >= 0 ? parseInt(args[limitIdx + 1], 10) : 0;

(async () => {
  console.log('[main] Initialising database:', DB_PATH);
  const db = await initDb(DB_PATH);

  console.log('[main] Starting TradingView data fetch...');
  const start = Date.now();
  try {
    const count = await fetchAll(db, SYMBOLS_DIR, limit);
    const elapsed = ((Date.now() - start) / 1000).toFixed(1);
    console.log(`\n[main] Done. Processed ${count} instruments in ${elapsed}s`);
    process.exit(0);
  } catch (err) {
    console.error('[main] Critical failure:', err);
    process.exit(1);
  }
})();
