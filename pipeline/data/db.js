'use strict';

/**
 * SQLite helper using sql.js (pure WASM — no native build tools required).
 * Database is saved to disk after every write batch.
 */

const fs = require('fs');
const path = require('path');

let _SQL = null;  // lazy-loaded sql.js module

async function getSql() {
  if (_SQL) return _SQL;
  const initSqlJs = require('sql.js');
  _SQL = await initSqlJs();
  return _SQL;
}

const SCHEMA = `
  CREATE TABLE IF NOT EXISTS candles_daily (
    symbol    TEXT NOT NULL,
    exchange  TEXT NOT NULL,
    date      TEXT NOT NULL,
    open      REAL,
    high      REAL,
    low       REAL,
    close     REAL,
    volume    REAL,
    PRIMARY KEY (symbol, exchange, date)
  );

  CREATE TABLE IF NOT EXISTS candles_5min (
    symbol    TEXT NOT NULL,
    exchange  TEXT NOT NULL,
    datetime  TEXT NOT NULL,
    open      REAL,
    high      REAL,
    low       REAL,
    close     REAL,
    volume    REAL,
    PRIMARY KEY (symbol, exchange, datetime)
  );

  CREATE TABLE IF NOT EXISTS fetch_log (
    symbol        TEXT,
    exchange      TEXT,
    timeframe     TEXT,
    fetched_at    TEXT,
    candles_count INTEGER,
    status        TEXT
  );
`;

async function initDb(dbPath) {
  const dir = path.dirname(dbPath);
  fs.mkdirSync(dir, { recursive: true });

  const SQL = await getSql();
  let db;
  if (fs.existsSync(dbPath)) {
    const data = fs.readFileSync(dbPath);
    db = new SQL.Database(data);
  } else {
    db = new SQL.Database();
  }
  db.run(SCHEMA);
  _save(db, dbPath);

  // Attach save path for later writes
  db._path = dbPath;
  return db;
}

function _save(db, dbPath) {
  const data = db.export();
  fs.writeFileSync(dbPath || db._path, Buffer.from(data));
}

function upsertCandles(db, table, rows) {
  if (!rows || rows.length === 0) return 0;
  const col = table === 'candles_daily' ? 'date' : 'datetime';
  const stmt = db.prepare(
    `INSERT OR REPLACE INTO ${table} (symbol, exchange, ${col}, open, high, low, close, volume)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
  );
  db.run('BEGIN');
  for (const r of rows) {
    stmt.run([r.symbol, r.exchange, r.ts, r.open, r.high, r.low, r.close, r.volume]);
  }
  db.run('COMMIT');
  stmt.free();
  _save(db);
  return rows.length;
}

function getLatestDate(db, symbol, exchange) {
  const stmt = db.prepare(
    'SELECT MAX(date) AS d FROM candles_daily WHERE symbol=? AND exchange=?'
  );
  stmt.bind([symbol, exchange]);
  if (stmt.step()) {
    const row = stmt.getAsObject();
    stmt.free();
    return row.d || null;
  }
  stmt.free();
  return null;
}

function getAllCandles(db, symbol, exchange, limit = 300) {
  const results = [];
  const stmt = db.prepare(
    `SELECT date AS ts, open, high, low, close, volume
     FROM candles_daily
     WHERE symbol=? AND exchange=?
     ORDER BY date DESC LIMIT ?`
  );
  stmt.bind([symbol, exchange, limit]);
  while (stmt.step()) results.push(stmt.getAsObject());
  stmt.free();
  return results.reverse();
}

function get5minCandles(db, symbol, exchange, limit = 800) {
  const results = [];
  const stmt = db.prepare(
    `SELECT datetime AS ts, open, high, low, close, volume
     FROM candles_5min
     WHERE symbol=? AND exchange=?
     ORDER BY datetime DESC LIMIT ?`
  );
  stmt.bind([symbol, exchange, limit]);
  while (stmt.step()) results.push(stmt.getAsObject());
  stmt.free();
  return results.reverse();
}

function logFetch(db, symbol, exchange, timeframe, count, status) {
  db.run(
    `INSERT INTO fetch_log (symbol, exchange, timeframe, fetched_at, candles_count, status)
     VALUES (?, ?, ?, datetime('now'), ?, ?)`,
    [symbol, exchange, timeframe, count, status]
  );
  _save(db);
}

module.exports = { initDb, upsertCandles, getLatestDate, getAllCandles, get5minCandles, logFetch };
