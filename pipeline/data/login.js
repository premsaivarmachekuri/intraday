'use strict';

/**
 * TradingView authentication.
 *
 * Two methods supported (in priority order):
 *
 * Method 1 (RECOMMENDED — bypasses bot detection):
 *   Set TV_SESSION and TV_SIGNATURE in .env
 *   Get these from your browser after logging in to tradingview.com:
 *     Chrome DevTools → Application → Cookies → tradingview.com
 *     Copy values of: sessionid  and  sessionid_sign
 *
 * Method 2 (fallback — may be blocked by TradingView bot detection):
 *   Set TV_USERNAME and TV_PASSWORD in .env
 */

const TradingView = require('@mathieuc/tradingview');

async function login(username, password) {
  const session = process.env.TV_SESSION;
  const signature = process.env.TV_SIGNATURE || '';

  // Method 1: session cookie (preferred)
  if (session) {
    console.log('[login] Using session cookie from TV_SESSION...');
    try {
      const user = await TradingView.getUser(session, signature);
      console.log(`[login] Authenticated via session: ${user.username}`);
      return { session, signature };
    } catch (err) {
      console.warn(`[login] Session cookie failed: ${err.message}. Trying username/password...`);
    }
  }

  // Method 2: username + password
  if (!username || !password) {
    throw new Error(
      'Authentication failed. Set TV_SESSION+TV_SIGNATURE (from browser cookies) in .env, ' +
      'or set TV_USERNAME+TV_PASSWORD.'
    );
  }

  console.log(`[login] Authenticating with username: ${username}...`);
  try {
    const user = await TradingView.loginUser(username, password, true);
    console.log(`[login] Authenticated: ${user.username}`);
    return { session: user.session, signature: user.signature };
  } catch (err) {
    throw new Error(
      `Username/password login failed: ${err.message}\n` +
      'TIP: TradingView blocks automated logins. Use TV_SESSION+TV_SIGNATURE instead.\n' +
      'Get them from Chrome DevTools → Application → Cookies → tradingview.com\n' +
      '  - sessionid       → TV_SESSION\n' +
      '  - sessionid_sign  → TV_SIGNATURE'
    );
  }
}

module.exports = { login };
