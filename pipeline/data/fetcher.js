'use strict';

const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');
const TradingView = require('@mathieuc/tradingview');
const { upsertCandles, getLatestDate, logFetch } = require('./db');

// Free-tier safe limits
const DAILY_RANGE = 300;
const MIN5_RANGE = 800;
const BATCH_SIZE = 5;
const BATCH_DELAY_MS = 2000;

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function readCsv(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  return parse(raw, { columns: true, skip_empty_lines: true });
}

function buildInstrumentList(symbolsDir) {
  const instruments = [];

  // NSE F&O stocks
  const nse = readCsv(path.join(symbolsDir, 'nse_fno.csv'));
  for (const row of nse) {
    instruments.push({
      symbol: row.symbol,
      exchange: 'NSE',
      tv_symbol: `NSE:${row.symbol}`,
      name: row.name,
      sector: row.sector,
    });
  }

  // MCX commodities
  const mcx = readCsv(path.join(symbolsDir, 'mcx.csv'));
  for (const row of mcx) {
    instruments.push({
      symbol: row.symbol,
      exchange: 'MCX',
      tv_symbol: row.tv_symbol,
      name: row.name,
      sector: 'MCX',
    });
  }

  // Indexes
  const idx = readCsv(path.join(symbolsDir, 'indexes.csv'));
  for (const row of idx) {
    const exchange = row.tv_symbol.startsWith('MCX') ? 'MCX' : 'NSE';
    instruments.push({
      symbol: row.symbol,
      exchange,
      tv_symbol: row.tv_symbol,
      name: row.name,
      sector: 'INDEX',
    });
  }

  return instruments;
}

/**
 * Fetch OHLCV candles for one instrument via TradingView WebSocket API.
 * Returns array of candle objects with {symbol, exchange, ts, open, high, low, close, volume}.
 */
function fetchCandles(client, tvSymbol, symbol, exchange, timeframe, range) {
  return new Promise((resolve, reject) => {
    const chart = new client.Session.Chart();
    const timeout = setTimeout(() => {
      chart.delete();
      reject(new Error(`Timeout fetching ${tvSymbol} tf=${timeframe}`));
    }, 30000);

    chart.setMarket(tvSymbol, { timeframe, range });

    // onUpdate fires when chart.periods is populated with OHLCV data
    // (onSymbolLoaded fires for metadata only — periods is empty there)
    let resolved = false;
    chart.onUpdate(() => {
      if (resolved) return;
      if (!chart.periods || chart.periods.length === 0) return;
      resolved = true;
      clearTimeout(timeout);
      try {
        const rows = chart.periods.map((p) => ({
          symbol,
          exchange,
          // period.time is Unix seconds; convert to ISO string
          ts: timeframe === 'D'
            ? new Date(p.time * 1000).toISOString().slice(0, 10)
            : new Date(p.time * 1000).toISOString().slice(0, 19).replace('T', ' '),
          open: p.open,
          high: p.max,   // TradingView API uses .max for high
          low: p.min,    // TradingView API uses .min for low
          close: p.close,
          volume: p.volume,
        }));
        chart.delete();
        resolve(rows);
      } catch (err) {
        chart.delete();
        reject(err);
      }
    });

    chart.onError((...args) => {
      clearTimeout(timeout);
      chart.delete();
      reject(new Error(`Chart error for ${tvSymbol}: ${JSON.stringify(args)}`));
    });
  });
}

async function fetchInstrument(client, db, instrument) {
  const { symbol, exchange, tv_symbol } = instrument;

  // --- Daily candles ---
  try {
    const latestDate = getLatestDate(db, symbol, exchange);
    const rows = await fetchCandles(client, tv_symbol, symbol, exchange, 'D', DAILY_RANGE);
    // Filter to only new rows when incremental
    const newRows = latestDate
      ? rows.filter((r) => r.ts > latestDate)
      : rows;
    const count = upsertCandles(db, 'candles_daily', newRows);
    logFetch(db, symbol, exchange, 'D', count, 'ok');
    console.log(`  [daily] ${symbol} — ${count} new candles (${rows.length} fetched)`);
  } catch (err) {
    console.error(`  [daily] ${symbol} ERROR: ${err.message}`);
    logFetch(db, symbol, exchange, 'D', 0, `error: ${err.message}`);
  }

  // --- 5-min candles (skip MCX indexes for brevity; they work the same) ---
  try {
    const rows = await fetchCandles(client, tv_symbol, symbol, exchange, '5', MIN5_RANGE);
    const count = upsertCandles(db, 'candles_5min', rows);
    logFetch(db, symbol, exchange, '5', count, 'ok');
    console.log(`  [5min]  ${symbol} — ${count} candles upserted`);
  } catch (err) {
    console.error(`  [5min]  ${symbol} ERROR: ${err.message}`);
    logFetch(db, symbol, exchange, '5', 0, `error: ${err.message}`);
  }
}

async function fetchAll(db, symbolsDir, limit) {
  let instruments = buildInstrumentList(symbolsDir);
  if (limit > 0) {
    instruments = instruments.slice(0, limit);
    console.log(`[fetcher] --limit ${limit}: processing first ${instruments.length} instruments`);
  }
  console.log(`[fetcher] Total instruments: ${instruments.length}`);

  // We create one client and reuse it; it connects via WebSocket
  // Credentials are loaded from env and passed in from main.js via global client
  const { login } = require('./login');
  const creds = await login(process.env.TV_USERNAME, process.env.TV_PASSWORD);
  const client = new TradingView.Client({ token: creds.session, signature: creds.signature });

  let total = 0;
  const batches = [];
  for (let i = 0; i < instruments.length; i += BATCH_SIZE) {
    batches.push(instruments.slice(i, i + BATCH_SIZE));
  }

  for (let bi = 0; bi < batches.length; bi++) {
    const batch = batches[bi];
    console.log(`\n[fetcher] Batch ${bi + 1}/${batches.length}: ${batch.map((x) => x.symbol).join(', ')}`);
    await Promise.all(batch.map((inst) => fetchInstrument(client, db, inst)));
    total += batch.length;
    if (bi < batches.length - 1) await sleep(BATCH_DELAY_MS);
  }

  client.end();
  return total;
}

module.exports = { fetchAll, buildInstrumentList };
