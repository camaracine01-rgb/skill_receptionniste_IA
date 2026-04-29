# Skill : create_bilingual_receptionist

Tu vas construire un agent vocal bilingue (FR/EN) complet pour une compagnie de services, en suivant le framework WAT déjà en place dans ce projet (CLAUDE.md).

Ton rôle : exécuter tout ce que tu peux automatiquement, t'arrêter et donner des instructions claires uniquement quand l'utilisateur doit agir manuellement.

---

## PHASE 1 — Collecter les informations business

Pose les questions suivantes à l'utilisateur. Si un PDF ou document est joint, lis-le et extrais les informations toi-même sans poser les questions déjà répondues.

Questions à poser :
1. Quel est le nom de la compagnie ?
2. Quel est le prénom de l'agente (ex: Mary, Sophie, Emma) ?
3. Quels services offrez-vous ? (nom, durée, prix — précise si le prix varie selon le type de véhicule ou autre critère)
4. Quels sont vos horaires d'ouverture ?
5. Quelle est votre adresse ?
6. Quel est votre numéro de téléphone et email de contact ?
7. Quelle est la langue par défaut de vos clients (fr ou en) ?
8. Y a-t-il des informations spécifiques à connaître ? (politiques, abonnements, garanties, modes de paiement, etc.)

Résume les informations collectées avant de passer à la phase suivante.

---

## PHASE 2 — Confirmer les outils et workflows

Présente à l'utilisateur la liste des outils et workflows qui seront créés, et demande confirmation avant de continuer.

**Outils qui seront créés dans `tools/` :**
- `get_client` — rechercher un client dans le CRM (Google Sheets) par téléphone ou nom
- `create_client` — enregistrer un nouveau client dans le CRM
- `get_availability` — vérifier les créneaux libres dans Google Calendar
- `create_reservation` — créer un rendez-vous dans Google Calendar + envoyer SMS de confirmation
- `send_sms` — envoyer un SMS via Twilio

**Outil natif VAPI (pas à coder) :**
- `handoff` — transfert de l'appel vers un agent humain (configuré directement sur VAPI)

**Outils de gestion de réservations à déduire systématiquement** — si l'agent peut créer des réservations, il doit aussi pouvoir les lister, les modifier et les annuler :
- `get_reservation` — lister les réservations à venir d'un client depuis Google Calendar
- `update_reservation` — replanifier un événement + SMS de confirmation
- `cancel_reservation` — annuler un événement + SMS d'annulation

**Workflows fixes (toujours créés) :**
- `answer_call.md` — accueil, détection langue, routage
- `register_client.md` — nouveau client non trouvé dans le CRM
- `answer_information.md` — répondre aux questions générales via le knowledge base
- `escalate_to_human.md` — escalade via handoff VAPI

**Workflows conditionnels (selon les outils confirmés) :**
- `book_reservation.md` — si `create_reservation` retenu
- `modify_reservation.md` — si `update_reservation` retenu
- `cancel_reservation.md` — si `cancel_reservation` retenu

Demande à l'utilisateur : "Est-ce que ces outils et workflows correspondent à tes besoins ? Y a-t-il des ajustements ?"

Attends confirmation avant de continuer.

---

## PHASE 3 — Générer le system prompt VAPI

Lis le fichier `~/.claude/commands/templates/bilingual_receptionist/prompt_engineering.md` pour connaître la structure exacte et les règles fixes du prompt.

Génère le system prompt complet en adaptant les sections avec :
- Les infos business collectées en Phase 1
- Les outils confirmés en Phase 2
- Les règles fixes définies dans `prompt_engineering.md`

Présente le prompt complet à l'utilisateur et demande : "Est-ce que ce prompt te convient ? Des ajustements avant qu'on continue ?"

Attends validation avant de continuer.

Sauvegarde le prompt validé dans `vapi_system_prompt.md` à la racine du projet.

---

## PHASE 4 — Construire le projet

Exécute tout dans l'ordre suivant sans t'arrêter :

### 4a — Fichiers de configuration
Crée dans l'ordre (adapte avec le nom de la compagnie et les vraies infos) :
- `requirements.txt` avec : flask, python-dotenv, twilio, google-api-python-client, google-auth
- `Procfile` : `web: python server.py`
- `nixpacks.toml` avec build pip et start python server.py
- `runtime.txt` : python-3.13.0
- `.gitignore` : exclure .env, .tmp/, credentials.json, token.json, __pycache__, .venv, .DS_Store
- `.env.example` avec toutes les variables nécessaires (voir Phase 5)

### 4b — Serveur Flask
Copie et adapte le template depuis `~/.claude/commands/templates/bilingual_receptionist/server.py`.
Le dispatcher doit inclure tous les outils confirmés en Phase 2.

### 4c — Outils (`tools/`)
Crée `tools/__init__.py` vide.
Génère chaque outil en suivant le framework WAT (scripts Python déterministes, gestion d'erreurs, bloc `__main__` pour test).

**Structure Google Sheet (référence obligatoire — tous les outils doivent respecter ces colonnes exactement) :**

| Feuille | Colonnes (dans l'ordre) |
|---|---|
| `Clients` | ID · Nom · Téléphone · Date · Notes |
| `Reservations` | ID · Nom Client · Service · Véhicule · Date · Heure · Statut · Notes |
| `transcriptions` | Call ID · Résumé · Date · Heure |

- `Reservations.Statut` : `"confirmed"` à la création, `"modified"` après modification, `"cancelled"` après annulation.
- Les dates sont toujours au format `YYYY-MM-DD`, les heures `HH:MM`.

---

**`tools/get_client.py`** — lecture feuille `Clients` (colonnes A:E), recherche par Téléphone (prioritaire) ou Nom. Retourne `{"status": "found", "client": {...}}` ou `{"status": "not_found"}`.

**`tools/create_client.py`** — écriture feuille `Clients`. Ligne : `[ID, Nom, Téléphone, Date, Notes]`. Retourne `{"status": "success", "client_id": "cli_..."}`.

**`tools/get_availability.py`** — API Google Calendar freebusy. Heures de travail issues des infos business. Intervalle de 30 min. Retourne tous les créneaux libres dans la plage demandée (aucun cap).

**`tools/create_reservation.py`** — crée événement Google Calendar + écrit ligne dans feuille `Reservations` (`[ID, Nom Client, Service, Véhicule, Date, Heure, "confirmed", Notes]`) + envoie SMS de confirmation. Retourne `{"status": "success", "reservation_id": "...", "datetime_friendly": "..."}`.

**`tools/send_sms.py`** — Twilio SMS. Message bilingue selon langue du client.

**`tools/get_reservation.py`** — liste les événements à venir du client via Google Calendar (filtre par phone ou client_id dans la description).

**`tools/update_reservation.py`** — met à jour date/heure d'un événement Calendar + met à jour colonnes Date (E), Heure (F) et Statut (G = `"modified"`) dans feuille `Reservations` + envoie SMS de confirmation.

**`tools/cancel_reservation.py`** — supprime événement Calendar + met à jour colonne Statut (G = `"cancelled"`) dans feuille `Reservations` + envoie SMS d'annulation.

**`tools/init_sheets.py`** — script d'initialisation unique : crée les trois feuilles (`Clients`, `Reservations`, `transcriptions`) avec les en-têtes exacts définis dans la table ci-dessus. À exécuter une seule fois après configuration du Service Account.

### 4d — Workflows (`workflows/`)
Génère les workflows en suivant le framework WAT, adaptés aux infos business et aux outils confirmés en Phase 2.

Chaque workflow doit couvrir : objectif, déclencheur, pré-conditions, étapes détaillées avec scripts FR+EN, gestion d'erreurs, règles importantes.

**Workflows fixes (toujours générés) :**
- `answer_call.md` — accueil, détection langue, routage vers les sous-workflows actifs
- `register_client.md` — nouveau client non trouvé dans le CRM
- `answer_information.md` — répondre aux questions générales via le knowledge base
- `escalate_to_human.md` — escalade via handoff VAPI

**Workflows conditionnels (générés uniquement si l'outil correspondant est confirmé) :**
- `book_reservation.md` — si `create_reservation` confirmé
- `modify_reservation.md` — si `update_reservation` confirmé
- `cancel_reservation.md` — si `cancel_reservation` confirmé

Important : mettre à jour la table de routage dans `answer_call.md` pour ne référencer que les workflows effectivement générés.

### 4e — GitHub
Crée un repo GitHub privé avec le nom de la compagnie en snake_case + "-receptionist".
Commit initial et push.

---

## PHASE 5 — Instructions manuelles

Arrête-toi et donne ces instructions à l'utilisateur dans l'ordre. Explique chaque étape clairement.

**Étape A — Google Cloud (Service Account)**
1. Aller sur console.cloud.google.com → créer un projet
2. Activer Google Sheets API et Google Calendar API
3. Créer un Service Account → télécharger la clé JSON
4. Créer un Google Sheet → noter l'ID (dans l'URL)
5. Créer un Google Calendar dédié → noter l'ID (Paramètres du calendrier)
6. Partager le Sheet ET le Calendar avec l'email du Service Account (rôle éditeur)

**Étape B — Twilio**
1. Créer un compte sur twilio.com
2. Acheter un numéro canadien avec capacité SMS
3. Noter : Account SID, Auth Token, numéro

**Étape C — Railway**
1. Aller sur railway.app → New Project → Deploy from GitHub
2. Sélectionner le repo créé en Phase 4e
3. Ajouter toutes les variables du `.env.example` dans Railway → Variables
4. Copier l'URL de déploiement Railway

**Étape D — Remplir le .env**
Copier `.env.example` en `.env` et remplir toutes les valeurs.

⚠️ Le JSON du Service Account doit être sur UNE SEULE ligne (minifié) dans le .env.

Dis à l'utilisateur : "Reviens quand le .env est complété et que Railway est déployé."

---

## PHASE 6 — Finalisation

Quand l'utilisateur revient avec le .env complété :

### 6a — Initialiser Google Sheets
```bash
python -m tools.init_sheets
```
Vérifie que les feuilles Clients et Reservations sont créées avec les bons en-têtes.

### 6b — Créer l'agent VAPI
Via l'API VAPI (`POST https://api.vapi.ai/assistant`), crée l'agent avec :
- `name` : le prénom de l'agente (Phase 1)
- `firstMessage` : message d'accueil bilingue adapté à la compagnie
- `model.provider` : anthropic
- `model.model` : claude-3-5-sonnet-20241022
- `model.systemPrompt` : contenu de `vapi_system_prompt.md`
- `model.tools` : définition complète de chaque outil confirmé en Phase 2 (voir format ci-dessous)
- `voice.provider` : 11labs, voiceId : sarah
- `transcriber` : deepgram, nova-2

**Format requis pour chaque outil dans `model.tools` :**
```json
{
  "type": "function",
  "function": {
    "name": "nom_outil",
    "description": "Ce que fait l'outil — utilisé par VAPI pour décider quand l'appeler",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": { "type": "string", "description": "..." },
        "param2": { "type": "string", "description": "..." }
      },
      "required": ["param1"]
    }
  },
  "server": {
    "url": "https://<url-railway>/tools"
  }
}
```

Déduire les paramètres de chaque outil directement depuis le code source dans `tools/`. Ne jamais inventer des paramètres — lire la signature de la fonction Python pour être exact.

Inclure également dans le payload de création :
- `serverUrl` : URL Railway + `/webhook` (ex: `https://<url-railway>/webhook`)

Cet endpoint reçoit les événements de fin d'appel VAPI (`end-of-call-report`) et enregistre automatiquement un résumé de l'appel dans la feuille `transcriptions` du Google Sheet (colonnes : Call ID | Résumé | Date | Heure). Le résumé provient du champ `summary` du payload VAPI — pas la transcription complète.

Sauvegarde l'assistant ID dans le `.env` sous `VAPI_ASSISTANT_ID`.

### 6c — Push final
Commit et push tous les fichiers créés (sauf .env).

### 6d — Confirmation finale
Affiche un résumé :
- Repo GitHub
- URL Railway
- VAPI Assistant ID
- Google Sheet ID
- Ce qu'il reste à faire manuellement : associer un numéro de téléphone à l'agent dans VAPI

---

## Règles générales

- Toujours respecter la structure WAT définie dans CLAUDE.md du projet
- Ne jamais committer le fichier .env
- Chaque tool doit avoir un bloc `__main__` pour pouvoir être testé individuellement
- Si un outil échoue pendant la finalisation, diagnostiquer l'erreur, corriger, retester avant de continuer
- Adapter le contenu (services, horaires, prix) à chaque nouveau projet — ne jamais laisser de valeurs génériques
