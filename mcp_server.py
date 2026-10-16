#!/usr/bin/env python3
"""
Voice Character Studio — MCP server mode.

Lets agents and other Spaces call the same characters the web app talks to,
through the Model Context Protocol (stdio transport, newline-delimited
JSON-RPC — no dependencies beyond the standard library).

Setup:
    export POLLINATIONS_API_KEY=sk_your_key      # your own Pollen
    python mcp_server.py

Claude Desktop / any MCP client config:
    { "mcpServers": { "voice-character-studio": {
        "command": "python",
        "args": ["mcp_server.py"],
        "env": { "POLLINATIONS_API_KEY": "sk_your_key" } } } }

Tools:
    list_characters                — who is available
    talk(character, message)       — persona text reply
    speak(text, character?, save?) — expressive speech (mp3), optional file save
    full_turn(character, message)  — talk + speak in one call
"""

import json
import os
import re
import sys
import urllib.request

GEN = "https://gen.pollinations.ai"
API_KEY = os.environ.get("POLLINATIONS_API_KEY", "")

# Keep in sync with config.js when you make the Space your own.
CHARACTERS = {
    "captain": {
        "name": "Captain Blackfeather",
        "voice": "en-GB-Harry",
        "persona": (
            "You are Captain Blackfeather, a retired pirate captain. You speak "
            "in lively nautical slang, call everyone 'matey', and turn every "
            "question into a short sea story or hard-won wisdom. You are warm, "
            "funny and a little dramatic. Keep replies under 80 words. Never "
            "mention being an AI language model. Reply in the language the "
            "visitor uses."
        ),
    },
    "professor": {
        "name": "Professor Hoot",
        "voice": "en-US-Sage",
        "persona": (
            "You are Professor Hoot, a wise elderly owl professor in a tweed "
            "jacket. You explain anything asked of you simply, with one gentle "
            "joke or a fun fact, and you hoot softly when you are pleased. "
            "Keep replies under 80 words. Never mention being an AI language "
            "model. Reply in the language the visitor uses."
        ),
    },
    "nova": {
        "name": "NOVA",
        "voice": "en-US-Olivia",
        "persona": (
            "You are NOVA, the friendly holographic guide of space Station 7. "
            "You are cheerful, curious about Earth culture, and you love "
            "explaining the galaxy in everyday words. Occasional playful "
            "sci-fi jargon is welcome. Keep replies under 80 words. Never "
            "mention being an AI language model. Reply in the language the "
            "visitor uses."
        ),
    },
}

CHAT_MODEL = "openai/gpt-5.4-nano"
TTS_MODEL = "microsoft/mai-voice-2.1"
SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]")


def call(path, body=None, headers=None, method="POST"):
    """One HTTP call to the gateway; returns (status, bytes, headers)."""
    h = {"Authorization": "Bearer " + API_KEY}
    if headers:
        h.update(headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(GEN + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def persona_reply(character, message):
    """Chat with the character's persona; returns reply text."""
    c = CHARACTERS[character]
    status, data, _ = call("/v1/chat/completions", {
        "model": CHAT_MODEL,
        "max_tokens": 200,
        "messages": [
            {"role": "system", "content": c["persona"]},
            {"role": "user", "content": message},
        ],
    })
    if status != 200:
        raise RuntimeError(f"chat HTTP {status}: {data[:200].decode(errors='replace')}")
    j = json.loads(data)
    reply = (j.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
    if not reply:
        raise RuntimeError("empty reply from the model")
    return reply


def synthesize(text, character):
    """Text → mp3 bytes with the character's voice."""
    voice = CHARACTERS[character]["voice"]
    status, data, _ = call("/v1/audio/speech", {
        "model": TTS_MODEL, "voice": voice, "input": text,
    })
    if status != 200:
        raise RuntimeError(f"tts HTTP {status}: {data[:200].decode(errors='replace')}")
    return data


def text_content(text):
    return [{"type": "text", "text": text}]


TOOLS = [
    {
        "name": "list_characters",
        "description": "List the voice characters available in the studio, with their id, name and voice.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "talk",
        "description": "Send a message to a character and get its persona text reply (spoken by the character in the app).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "character": {"type": "string", "enum": list(CHARACTERS), "description": "Character id"},
                "message": {"type": "string", "description": "What to say to the character"},
            },
            "required": ["character", "message"],
        },
    },
    {
        "name": "speak",
        "description": "Turn text into expressive speech with a character's voice. Returns the audio as base64 when save is false, or saves an mp3 and returns its path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "What the character should say"},
                "character": {"type": "string", "enum": list(CHARACTERS), "description": "Character id (picks the voice)"},
                "save": {"type": "boolean", "description": "Save to an mp3 file instead of returning base64", "default": False},
            },
            "required": ["text", "character"],
        },
    },
    {
        "name": "full_turn",
        "description": "One call: the character answers your message with text AND spoken audio (saved as mp3).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "character": {"type": "string", "enum": list(CHARACTERS)},
                "message": {"type": "string"},
            },
            "required": ["character", "message"],
        },
    },
]


def run_tool(name, args):
    """Execute one tool; returns (content, is_error)."""
    if name == "list_characters":
        rows = [
            {"character": k, "name": v["name"], "voice": v["voice"]}
            for k, v in CHARACTERS.items()
        ]
        return text_content(json.dumps(rows, ensure_ascii=False, indent=2)), False

    if name == "talk":
        reply = persona_reply(args["character"], args["message"])
        return text_content(reply), False

    if name == "speak":
        audio = synthesize(args["text"], args["character"])
        if args.get("save"):
            path = SAFE_NAME.sub("_", f"vcs-{args['character']}.mp3")
            with open(path, "wb") as f:
                f.write(audio)
            return text_content(f"Saved {len(audio)} bytes to {path}"), False
        import base64
        return text_content(base64.b64encode(audio).decode()), False

    if name == "full_turn":
        reply = persona_reply(args["character"], args["message"])
        audio = synthesize(reply, args["character"])
        path = SAFE_NAME.sub("_", f"vcs-turn-{args['character']}.mp3")
        with open(path, "wb") as f:
            f.write(audio)
        summary = json.dumps({
            "character": CHARACTERS[args["character"]]["name"],
            "reply": reply,
            "audio_file": path,
            "audio_bytes": len(audio),
        }, ensure_ascii=False, indent=2)
        return text_content(summary), False

    return text_content(f"Unknown tool: {name}"), True


def main():
    if not API_KEY:
        print("Set POLLINATIONS_API_KEY (sk_...) to your own Pollinations key.", file=sys.stderr)
        sys.exit(1)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        mid = msg.get("id")
        method = msg.get("method", "")
        if method == "initialize":
            out = {
                "jsonrpc": "2.0", "id": mid,
                "result": {
                    "protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "voice-character-studio", "version": "1.0.0"},
                },
            }
        elif method in ("notifications/initialized", "initialized"):
            continue
        elif method == "ping":
            out = {"jsonrpc": "2.0", "id": mid, "result": {}}
        elif method == "tools/list":
            out = {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
        elif method == "tools/call":
            params = msg.get("params", {})
            name = params.get("name", "")
            args = params.get("arguments", {}) or {}
            try:
                content, is_error = run_tool(name, args)
            except Exception as e:  # noqa: BLE001 — report to the client
                content, is_error = text_content(str(e)), True
            out = {
                "jsonrpc": "2.0", "id": mid,
                "result": {"content": content, "isError": is_error},
            }
        elif mid is not None:
            out = {"jsonrpc": "2.0", "id": mid,
                   "error": {"code": -32601, "message": f"Method not found: {method}"}}
        else:
            continue
        sys.stdout.write(json.dumps(out) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
