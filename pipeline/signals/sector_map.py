"""Sector and sister-stock lookup tables loaded from symbols CSVs."""

import csv
import os

_BASE = os.path.dirname(os.path.dirname(__file__))
_NSE_CSV = os.path.join(_BASE, 'symbols', 'nse_fno.csv')
_IDX_CSV = os.path.join(_BASE, 'symbols', 'indexes.csv')

# wiki/pioneers/jesse-livermore.md §"Multi-Timeframe Logic — Level 2"
SECTOR_INDEX_MAP = {
    'BANKS': 'BANKNIFTY',
    'PSU_BANKS': 'BANKNIFTY',
    'NBFC': 'FINNIFTY',
    'INSURANCE': 'FINNIFTY',
    'AMC_BROKING': 'FINNIFTY',
    'IT': 'CNXIT',
    'TECH_INTERNET': 'CNXIT',
    'AUTO': 'CNXAUTO',
    'AUTO_ANCILLARY': 'CNXAUTO',
    'PHARMA': 'CNXPHARMA',
    'FMCG': 'CNXFMCG',
    'METALS': 'CNXMETAL',
    'MINING': 'CNXMETAL',
    'OIL_GAS': 'CNXENERGY',
    'POWER': 'CNXENERGY',
    'POWER_FINANCE': 'CNXENERGY',
    'REALTY': 'CNXREALTY',
    'INFRA': 'CNXINFRA',
    'DEFENCE': 'CNXDEFENCE',
    'CAPITAL_GOODS': 'NIFTY50',
    'CONSUMER': 'NIFTY50',
    'TELECOM': 'NIFTY50',
    'HEALTHCARE': 'NIFTY50',
    'RETAIL': 'NIFTY50',
    'CONGLOMERATE': 'NIFTY50',
    'AGRO_CHEM': 'NIFTY50',
    'AVIATION': 'NIFTY50',
    'HOSPITALITY': 'NIFTY50',
    'CEMENT': 'NIFTY50',
    'LOGISTICS': 'NIFTY50',
    'MCX': 'MCXICOMDEX',
}

_stocks = {}  # symbol → {sector, sister1, sister2, name}
_index_sectors = {}  # sector_for → symbol

def _load():
    global _stocks, _index_sectors
    if _stocks:
        return
    with open(_NSE_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            _stocks[row['symbol']] = {
                'name': row['name'],
                'sector': row['sector'],
                'sister1': row['sister1'],
                'sister2': row['sister2'],
            }
    with open(_IDX_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            _index_sectors[row['sector_for']] = row['symbol']

def get_sector(symbol: str) -> str:
    _load()
    return _stocks.get(symbol, {}).get('sector', 'UNKNOWN')

def get_sister_stocks(symbol: str) -> list:
    _load()
    info = _stocks.get(symbol, {})
    return [s for s in [info.get('sister1'), info.get('sister2')] if s]

def get_sector_index(sector: str) -> str:
    return SECTOR_INDEX_MAP.get(sector, 'NIFTY50')

def get_all_sectors() -> list:
    _load()
    return list({v['sector'] for v in _stocks.values()})

def get_stock_info(symbol: str) -> dict:
    _load()
    return _stocks.get(symbol, {})
