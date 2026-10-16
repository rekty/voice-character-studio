---
title: Voice Character Studio
emoji: 🎙️
colorFrom: purple
colorTo: indigo
sdk: static
app_file: index.html
pinned: false
---

# 🎙️ Voice Character Studio

**Speech in, expressive speech out.** Talk to AI characters with your microphone —
they answer in their own voice, with their own personality.

Every request is paid by **you**, with your own [Pollen](https://enter.pollinations.ai)
through [Bring Your Own Pollen](https://github.com/pollinations/pollinations/blob/main/BRING_YOUR_OWN_POLLEN.md),
so nobody's key runs dry. Sign in takes one click, sets your own budget, and the
key can be revoked anytime from your dashboard.

## What it does

1. **Sign in with Pollinations** — the device flow, so it keeps working the moment
   you duplicate this Space onto any URL. No redirect URI to configure, nothing to
   re-remember. Your key lives in this browser tab only (`sessionStorage`) and
   expires automatically (7 days by default).
2. **Pick a character** — Captain Blackfeather, Professor Hoot, NOVA, or your own
   (see below). Each has a persona, a distinct expressive voice, and a portrait.
3. **Hold the mic and talk** — your speech is transcribed (Whisper), the character
   answers in character (GPT-5.4-nano), and speaks the reply aloud
   (MAI-Voice-2.1). Or type, if you'd rather not talk.
4. **Watch the cost meter** — every turn shows its approximate Pollen cost live,
   priced from the current model lists. A whole conversation costs about
   **0.002 🌼** (a few tenths of a cent).

Buttons on the character card: **✨ New look** repaints the portrait with the image
API (0.004 🌼), **↺ New conversation** clears the memory.

## Make it your own

Everything editable lives in [`config.js`](config.js) — every value is marked
`EDIT ME`:

| What | Where |
| --- | --- |
| Your App Key (`pk_...`) | `APP_CLIENT_ID` — create one at [enter.pollinations.ai/keys](https://enter.pollinations.ai/keys) to show your app name on sign-in and earn 25% developer markup |
| Characters | `CHARACTERS` — persona prompt, voice, portrait, accent color |
| Models | `MODELS` — any non-paid-only model from the [text](https://gen.pollinations.ai/text/models), [audio](https://gen.pollinations.ai/audio/models) or [image](https://gen.pollinations.ai/image/models) lists |
| Budget / limits | `BEHAVIOR` — max record time, remembered turns, suggested sign-in budget |

To duplicate: click **Duplicate** above, edit `config.js`, done. The portraits in
`assets/` are yours to replace (or click **✨ New look** in the app and save the
result).

## MCP server mode

Agents and other Spaces can call the same characters through the Model Context
Protocol — stdio, standard library only, no dependencies:

```bash
export POLLINATIONS_API_KEY=sk_your_key   # your own Pollen
python mcp_server.py
```

```json
{ "mcpServers": { "voice-character-studio": {
    "command": "python",
    "args": ["mcp_server.py"],
    "env": { "POLLINATIONS_API_KEY": "sk_your_key" } } } }
```

Tools: `list_characters`, `talk(character, message)`,
`speak(text, character, save)`, `full_turn(character, message)` (text + saved mp3).

## Cost per turn (approximate)

| Step | Model | Cost |
| --- | --- | --- |
| Transcribe your speech | `openai/whisper-large-v3` | ~0.0002 🌼 (5 s of audio) |
| Character's answer | `openai/gpt-5.4-nano` | ~0.0002 🌼 |
| Speak the answer | `microsoft/mai-voice-2.1` | ~0.0006 🌼 (~8 s of speech) |
| **Total per turn** | | **~0.001 🌼** |

New portrait: 0.004 🌼 (`tongyi-mai/z-image-turbo`, flat rate).

## How it's built

Static HTML + vanilla JS — no build step, no server, nothing to install. All
Pollinations calls go straight from your browser to `gen.pollinations.ai`
(fully CORS-open), so your key never passes through any backend. See
[API docs](https://gen.pollinations.ai/docs) for the endpoints used:
`/v1/audio/transcriptions`, `/v1/chat/completions`, `/v1/audio/speech`,
`/image/{prompt}`.

Built for Pollinations quest [#17249](https://github.com/pollinations/pollinations/issues/17249).
