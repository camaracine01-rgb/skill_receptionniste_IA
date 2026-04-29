# Skill — Réceptionniste IA Bilingue (VAPI + Claude Code)

Ce skill Claude Code génère un agent vocal bilingue FR/EN complet pour une compagnie de services, déployé sur Railway et connecté à VAPI, Google Sheets, Google Calendar et Twilio.

## Ce que le skill crée

- **Agent VAPI** avec system prompt structuré (7 sections)
- **Serveur Flask** sur Railway avec endpoint `/tools` et `/webhook`
- **8 outils Python** : gestion clients (CRM Google Sheets), disponibilités (Google Calendar), réservations, SMS Twilio
- **Workflows WAT** documentés en Markdown
- **Google Sheet CRM** avec 3 feuilles : Clients, Reservations, transcriptions

## Prérequis

- Claude Code installé
- Comptes : Google Cloud, Twilio, Railway, VAPI, GitHub

## Installation

**Option 1 — Via Claude Code (recommandé)**

Ouvre Claude Code dans n'importe quel dossier et écris :

```
Installe ce skill : https://github.com/camaracine01-rgb/skill_receptionniste_IA
```

Claude Code installe automatiquement le skill.

**Option 2 — Via le gestionnaire de plugins**

Ajoute ce marketplace dans `~/.claude/settings.json` :

```json
"extraKnownMarketplaces": {
  "receptionniste-ia": {
    "source": {
      "source": "github",
      "repo": "camaracine01-rgb/skill_receptionniste_IA"
    }
  }
}
```

Puis ouvre le gestionnaire de plugins Claude Code et installe `create_bilingual_receptionist`.

## Utilisation

Dans un nouveau projet vide, tape :

```
/create_bilingual_receptionist
```

Le skill guide à travers 6 phases :
1. Collecte des informations business
2. Confirmation des outils et workflows
3. Génération du system prompt VAPI
4. Construction complète du projet
5. Instructions de configuration manuelle (Google Cloud, Twilio, Railway)
6. Finalisation (init Google Sheets, création agent VAPI, push GitHub)

## Stack technique

| Composant | Technologie |
|---|---|
| Agent vocal | VAPI + Claude Sonnet |
| Voix | ElevenLabs (Sarah) |
| Transcription | Deepgram Nova-2 |
| Serveur | Flask sur Railway |
| CRM | Google Sheets |
| Calendrier | Google Calendar |
| SMS | Twilio |
