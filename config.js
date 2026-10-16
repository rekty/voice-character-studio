/*
 * Voice Character Studio — configuration
 * ---------------------------------------
 * Everything you might want to change lives in this one file.
 * After you duplicate this Space, open config.js and make it yours.
 */
window.VCS_CONFIG = {
    // ── EDIT ME ──────────────────────────────────────────────────────────
    // Your publishable Pollinations App Key (pk_...).
    // Create one at https://enter.pollinations.ai/keys → "Create New App Key".
    // It shows your app's name on the sign-in screen and tracks your
    // developer earnings (25% markup, opt-in per key).
    // The default key belongs to the Space author; replace it with your own
    // after duplicating. Leaving it empty still works — sign-in falls back
    // to the redirect hostname.
    APP_CLIENT_ID: "pk_OgKOvwYe1inoV0DL",

    // ── EDIT ME: characters ──────────────────────────────────────────────
    // Add, remove or rewrite characters. Each one needs:
    //   id          — used in URLs and file names (letters, digits, -)
    //   name        — shown in the picker
    //   tagline     — one line under the name
    //   persona     — system prompt: who the character is, how it speaks
    //   voice       — a mai-voice-2.1 voice (list below the fold)
    //   portrait    — image file in assets/ (generate one with the image API,
    //                 or click "New look" in the app and save the result)
    //   accent      — hex color for the character's UI
    CHARACTERS: [
        {
            id: "captain",
            name: "Captain Blackfeather",
            tagline: "Retired pirate, amateur philosopher",
            persona:
                "You are Captain Blackfeather, a retired pirate captain. You speak " +
                "in lively nautical slang, call everyone 'matey', and turn every " +
                "question into a short sea story or hard-won wisdom. You are warm, " +
                "funny and a little dramatic. Keep replies under 80 words — they " +
                "will be spoken aloud. Never mention being an AI language model. " +
                "Reply in the language the visitor uses.",
            voice: "en-GB-Harry",
            portrait: "assets/portrait-captain.png",
            accent: "#d98e3a",
        },
        {
            id: "professor",
            name: "Professor Hoot",
            tagline: "An owl who has read too much",
            persona:
                "You are Professor Hoot, a wise elderly owl professor in a tweed " +
                "jacket. You explain anything asked of you simply, with one gentle " +
                "joke or a fun fact, and you hoot softly when you are pleased. " +
                "Keep replies under 80 words — they will be spoken aloud. Never " +
                "mention being an AI language model. Reply in the language the " +
                "visitor uses.",
            voice: "en-US-Sage",
            portrait: "assets/portrait-professor.png",
            accent: "#8fb56a",
        },
        {
            id: "nova",
            name: "NOVA",
            tagline: "Hologram guide of Station 7",
            persona:
                "You are NOVA, the friendly holographic guide of space Station 7. " +
                "You are cheerful, curious about Earth culture, and you love " +
                "explaining the galaxy in everyday words. Occasional playful " +
                "sci-fi jargon is welcome. Keep replies under 80 words — they " +
                "will be spoken aloud. Never mention being an AI language model. " +
                "Reply in the language the visitor uses.",
            voice: "en-US-Olivia",
            portrait: "assets/portrait-nova.png",
            accent: "#5ec8d8",
        },
    ],

    // ── EDIT ME: models ──────────────────────────────────────────────────
    // Any model from https://gen.pollinations.ai/{text,audio,image}/models
    // that is not paid-only works with visitor keys.
    MODELS: {
        chat: "openai/gpt-5.4-nano",     // fast, cheap persona brain
        stt: "openai/whisper-large-v3",  // speech → text (your visitors' mic)
        tts: "microsoft/mai-voice-2.1",  // expressive text → speech
        image: "tongyi-mai/z-image-turbo", // portrait remixes
    },

    // ── EDIT ME: behaviour ───────────────────────────────────────────────
    BEHAVIOR: {
        maxRecordSeconds: 30,   // mic auto-stops here (cost control)
        historyTurns: 12,       // chat turns remembered per conversation
        budgetRequest: 5,       // suggested Pollen budget on the sign-in screen
        defaultReplyLanguage: "en",
    },
};

// All mai-voice-2.1 voices, in case you want a different one per character:
// cs-CZ-Grant cs-CZ-Harper da-DK-Grant da-DK-Harper de-DE-Grant de-DE-Harper
// de-DE-Klaus de-DE-Mia en-AU-Isla en-GB-Emily en-GB-Harry en-IN-Dhruv
// en-IN-Priya en-US-Ethan en-US-Grant en-US-Harper en-US-Iris en-US-Jasper
// en-US-Olivia en-US-Sage es-ES-Marta es-MX-Alejo es-MX-Grant es-MX-Harper
// es-MX-Valeria fi-FI-Grant fi-FI-Harper fr-FR-Grant fr-FR-Harper fr-FR-Marc
// fr-FR-Soleil hi-IN-Arjun hi-IN-Dhruv hi-IN-Grant hi-IN-Harper hi-IN-Kavya
// hi-IN-Priya hu-HU-Bence hu-HU-Grant hu-HU-Harper hu-HU-Levente hu-HU-Lilla
// hu-HU-Reka id-ID-Grant id-ID-Harper it-IT-Grant it-IT-Harper it-IT-Luca
// it-IT-Rosa ko-KR-Grant ko-KR-Haena ko-KR-Harper ko-KR-Junho nb-NO-Grant
// nb-NO-Harper nl-NL-Grant nl-NL-Harper nl-NL-Sander pl-PL-Grant pl-PL-Harper
// pt-BR-Caio pt-BR-Grant pt-BR-Harper pt-BR-Luana pt-BR-Pedro pt-BR-Rafael
// pt-PT-Grant pt-PT-Harper pt-PT-Rui ro-RO-Andrei ro-RO-Elena ro-RO-Grant
// ro-RO-Harper ro-RO-Ioana ro-RO-Radu ru-RU-Grant ru-RU-Harper ru-RU-Lev
// ru-RU-Masha sv-SE-Grant sv-SE-Harper th-TH-Grant th-TH-Harper th-TH-Krit
// th-TH-Nattapong tr-TR-Aydin tr-TR-Elif tr-TR-Grant tr-TR-Harper vi-VN-Grant
// vi-VN-Harper zh-CN-Bo zh-CN-Grant zh-CN-Harper zh-CN-Lan zh-CN-Mei zh-CN-Wei
