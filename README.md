# Skill — Réceptionniste IA Bilingue (VAPI + Claude Code)

Ce skill Claude Code génère un agent vocal bilingue FR/EN complet pour une compagnie de services, déployé sur Railway et connecté à VAPI, Google Sheets, Google Calendar et Twilio.

## Ce que le skill crée

- **Agent VAPI** avec system prompt structuré (7 sections)
- **Serveur Flask** sur Railway avec endpoint `/tools` (dispatch des outils) et `/webhook` (transcriptions)
- **8 outils Python** : gestion clients (CRM Google Sheets), disponibilités (Google Calendar), réservations, SMS Twilio
- **Workflows WAT** documentés en Markdown
- **Google Sheet CRM** avec 3 feuilles : Clients, Reservations, transcriptions

## Prérequis

- Claude Code installé
- Comptes : Google Cloud, Twilio, Railway, VAPI, GitHub

## Installation

```bash
# Copier le skill dans Claude Code
cp create_bilingual_receptionist.md ~/.claude/commands/

# Copier le template de prompt engineering
mkdir -p ~/.claude/commands/templates/bilingual_receptionist
cp templates/bilingual_receptionist/prompt_engineering.md ~/.claude/commands/templates/bilingual_receptionist/
cp templates/bilingual_receptionist/server.py ~/.claude/commands/templates/bilingual_receptionist/
```

## Utilisation

Dans un nouveau projet vide, lance Claude Code et tape :

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
