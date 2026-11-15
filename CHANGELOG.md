# Changelog

Toutes les modifications notables de ForgeOS sont consignées dans ce fichier.
Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
projet utilise [Semantic Versioning](https://semver.org/lang/fr/).

## Unreleased

### Ajouté

- Adaptateur double cible Google Antigravity (`agy` CLI & Antigravity IDE) et Gemini CLI
  générant `.gemini/agents/*.md` (schéma Gemini CLI et outils natifs à moindre privilège),
  `.gemini/antigravity-agents/*.md` (frontmatter `subagent: true`, `mainAgent: false`,
  `tools:` à moindre privilège et `skills: ../skills/<skill>`), le miroir
  `.gemini/skills/`, `.agents/agents.json`, `.gemini/GEMINI.md`, `.gemini/settings.json`
  et le script durci `scripts/gemini_adapter.py` (écritures atomiques, classification exhaustive
  des rôles, détection/nettoyage des liens symboliques cassés).
- Prise en charge de la cible `--tool gemini` (et inclusion dans `--tool all`) dans
  l'installateur Python `scripts/forgeos.py` et ses tests isolés, incluant
  `.agents/agents.json` -> `.gemini/antigravity-agents` / `.agents/skills.json` en local et
  `~/.gemini/config/{GEMINI.md,agents.json,skills.json}` en installation globale.
- Couverture Google Gemini API, Interactions API, Gemini Live API et Google GenAI SDK
  (`google-genai` / `@google/genai`) dans `ai-llm-engineer`, `ai-development`,
  `AGENTS.md`, `profiles/python-ai.yaml` et `docs/technology-catalog.md`.

## 0.1.0 - 2026-11-14

### Ajouté

- Gouvernance CTO commune pour Codex et Claude Code, avec 17 sous-agents
  spécialisés et des frontières de responsabilité explicites.
- 16 Skills réutilisables couvrant le développement, la qualité, la sécurité,
  les performances, la documentation et la préparation des releases.
- Adaptateur Claude Code générant les agents natifs et le miroir de découverte
  des Skills à partir des sources canoniques ForgeOS.
- Profils indicatifs pour Laravel, Next.js, Nuxt, NestJS, Expo et les produits
  multi-stack, sans installation ni mise à niveau implicite.
- Installateur Python 3 sans dépendance externe avec les commandes `install`,
  `update`, `status` et `uninstall`, pour Codex, Claude Code ou les deux, en
  portée locale ou globale.
- Gestion des conflits, sauvegardes explicites, manifeste de propriété,
  détection de dérive et désinstallation limitée aux fichiers ForgeOS.
- Validateurs structurels, contrôle de synchronisation Claude Code et tests
  isolés du cycle de vie de l'installateur.
- Distribution du projet sous licence MIT.

### Limitations connues

- La compatibilité de l'installateur a été exécutée nativement sur Windows
  uniquement ; macOS et Linux restent à vérifier dans leurs environnements.
- Les contrôles structurels ne prouvent pas tout le comportement d'exécution :
  Claude Code a découvert les 17 agents, mais l'exécution dynamique des Skills
  et le modèle restent non vérifiés en raison d'une authentification expirée.
- ForgeOS ne configure pas l'authentification, les protections GitHub, les
  permissions distantes ni les environnements de production.
- Les profils technologiques sont des recommandations et ne prouvent jamais la
  stack ou les versions d'un projet cible.
- Les réglages Codex et Claude Code susceptibles de modifier les permissions
  restent optionnels et exigent un consentement explicite.
