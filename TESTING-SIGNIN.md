# Testing sign-in end to end (real Pollinations account)

This is the manual test for the OAuth code flow with PKCE on the Space. Read the
"Prerequisites" section before you start; the flow cannot be tested without a
signed-in Pollinations account, because the approval screen and the token are
both tied to it.

Live app: https://rekty1988-voice-character-studio.static.hf.space
Callback: `https://rekty1988-voice-character-studio.static.hf.space/`
Client id (a metadata document, no App Key needed):
`https://rekty1988-voice-character-studio.static.hf.space/oauth-client.json`

## What you need to prepare

1. **A Pollinations account** that you can sign into with GitHub or Google
   (https://enter.pollinations.ai). This is the same account whose approval the
   consent screen asks for.
2. **Pollen on that account.** The app requests `budget=5`, which is a *cap*,
   not a charge: approving it allows up to 5 Pollen of usage for 7 days. A real
   conversation costs a fraction of a Pollen, but you need a non-zero balance,
   otherwise the chat turn fails with a billing error after sign-in (which would
   look like a sign-in bug).
3. **A browser profile you control**, with DevTools available. Use a normal
   window, not a private one if you can — `sessionStorage` works in private mode
   too, but it is easier to keep evidence in a normal profile. Disable
   extensions that block storage or third-party scripts (uBlock, privacy
   extensions) for this test.
4. **DevTools → Network → tick "Preserve log"** before clicking sign in. Without
   it, the full-page redirect to `enter.pollinations.ai` clears the request log
   and you lose the `authorize` and `token` calls you need when something fails.
5. **A note of your starting balance**: https://gen.pollinations.ai/account/balance
   (or the balance shown at enter.pollinations.ai). You compare it after the test.
6. **Microphone permission for the Space origin** if you want to test the voice
   turn: click the lock/mic icon in the address bar → set Microphone to **Allow**
   → reload. Only the hold-to-talk button needs it; typing works without it, so
   do not mistake a mic prompt for a sign-in problem. Symptom when it is still
   blocked: the status line reads "Microphone is blocked for this site — click
   the lock/mic icon in the address bar, set Microphone to Allow, reload. Or
   type below." while you are already signed in (older builds said simply
   "Microphone blocked — allow it in your browser, or type below.").

## No-account sanity checks (run first, 30 seconds)

These pass or fail without any login, so run them before blaming the sign-in:

```bash
# 1. client metadata document is served with the right type and content
curl -s https://rekty1988-voice-character-studio.static.hf.space/oauth-client.json

# 2. Pollinations sees the app for that client_id
curl -s "https://enter.pollinations.ai/api/app-lookup?client_id=https://rekty1988-voice-character-studio.static.hf.space/oauth-client.json"

# 3. the Space's root redirect keeps the OAuth query string
curl -s -o /dev/null -D - "https://rekty1988-voice-character-studio.static.hf.space/?code=abc&state=xyz" | grep -i '^location'

# 4. the browser is allowed to POST the token exchange (CORS preflight)
curl -s -o /dev/null -D - -X OPTIONS "https://enter.pollinations.ai/api/oauth/token" \
  -H "Origin: https://rekty1988-voice-character-studio.static.hf.space" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" | grep -i '^access-control'
```

Expected: `found:true` with `redirectUris` pointing at the Space; `Location:
/index.html?code=abc&state=xyz`; `Access-Control-Allow-Origin: *`.

## Happy path

Reset first: DevTools → Application → Session Storage → the Space origin →
delete `vcs_pkce` and `vcs_session_key`. Then reload.

| # | Do this | Expect |
|---|---|---|
| 1 | Click **Sign in with Pollinations** | Full-page redirect to `enter.pollinations.ai/authorize?...` |
| 2 | Inspect that URL | `response_type=code`, `client_id` = the `oauth-client.json` URL, `redirect_uri` = Space root, `state` present, `code_challenge_method=S256`, `budget=5`, `expiry=7`, `models=text,audio,image` |
| 3 | Look at the consent screen | It names **Voice Character Studio** and the Space host, with the budget/expiry you requested |
| 4 | Approve | You land **back in the app** — not on a page that says "Access allowed. Code: …" |
| 5 | Look at the address bar | Origin + path only. No `code`, no `state`. Status line: "Signed in — your characters are listening." |
| 6 | Check Session Storage | `vcs_session_key` exists and starts with `sk_`; `vcs_pkce` is **gone** |
| 7 | Check Network | `POST /api/oauth/token` → 200, response body has `access_token` |
| 8 | Type a short message and send | A reply appears; the cost counter increases |
| 9 | Hold **Hold to talk**, say one sentence, release | Your words appear as a transcript and the character answers with audio |
| 10 | Reload the page | Still signed in (same tab). A brand-new tab is signed out — that is intended, the key lives in `sessionStorage` |
| 11 | Click **Sign out** | Key removed, input and talk disabled, status "Signed out." |
| 12 | Re-check your balance | It dropped by a small fraction of a Pollen, consistent with the few turns you did — not the whole 5 |

## Failure cases worth testing

- **Cancel / deny on the consent screen.** You should return to the app with
  status "Sign-in was cancelled: access_denied" and a clean URL. Nothing is
  stored.
- **Tampered state.** Open the Space with `/?code=abc&state=xyz` in a tab that
  has no `vcs_pkce`. Expect "Sign-in could not be verified — please try again."
  and **no** request to `/api/oauth/token` in the Network tab.
- **Reused code.** Approve, let the app sign in, then paste the previous
  callback URL (if you kept it) into a fresh tab. Expect a failed sign-in, not a
  second session.
- **Expired / revoked key.** While signed in, delete the key at
  https://enter.pollinations.ai/keys (if OAuth keys are listed there) or wait
  for expiry, then send a message. The app should show "Your session key expired
  or was revoked — sign in again." and drop back to the signed-out state.
- **Duplicate origin → device flow.** Copy the app to a different URL (or serve
  it on `localhost`) and click sign in. It must show the device-code overlay with
  a code and a verify link, because `AUTH.ORIGIN` no longer matches. That path
  needs no redirect URI and is expected to behave differently.

## If something fails, capture this for the issue

The maintainer cannot debug "it didn't work", so record:

- the exact `/authorize` URL (keep `state` if you like, it is single-use) and
  what the consent screen showed;
- the full URL you landed on after approving;
- `POST /api/oauth/token` → status code and response body from DevTools
  (this is where `invalid_grant`, `invalid_client` or CORS errors show up);
- the status line text in the app, and the `vcs_pkce` / `vcs_session_key`
  presence in Session Storage;
- browser name and version, and the UTC time of the attempt.

Note that a `code` is single use and short lived: if you wait or reload the
callback twice, `invalid_grant` is the correct answer, not a bug.

## Quick troubleshooting map

| Symptom | Likely cause |
|---|---|
| "Sign-in could not be verified" after approving | `vcs_pkce` was missing or the `state` did not match — usually a reload, a second tab, or storage blocked by an extension |
| `invalid_client` from the token endpoint | the metadata document at `CLIENT_METADATA_URL` is unreachable or its `client_id` no longer matches its own URL |
| `invalid_grant` on the first attempt | the `code` was already used or expired; retry from step 1 without reloading the callback |
| `redirect_uri` mismatch on the consent screen | `AUTH.REDIRECT_URI` in `config.js` differs from `redirect_uris` in `oauth-client.json`, including the trailing slash |
| Device-code overlay appears on the Space | `AUTH.ORIGIN` does not match `location.origin` (check `www.`, trailing slash, http vs https) or `CLIENT_METADATA_URL` is empty |
| Sign-in succeeds but the first message fails | key has no budget/balance, or `models=text,audio,image` does not cover the model you picked in `config.js` |
