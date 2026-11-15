# Installation et maintenance

## Prérequis

- Python 3.9+ pour `scripts/forgeos.py`. L’installateur utilise uniquement la bibliothèque standard.
- Codex, Claude Code, Google Antigravity (`agy` CLI / Antigravity IDE) et/ou Gemini CLI installés et authentifiés séparément selon leur documentation officielle.
- Python 3.11+ uniquement pour `scripts/bootstrap.py`, car le validateur source analyse le TOML avec `tomllib`.

L’installateur ne télécharge aucune dépendance et ne modifie aucun service distant.

## Commandes

```text
python scripts/forgeos.py install   [options]
python scripts/forgeos.py update    [options]
python scripts/forgeos.py status    [options]
python scripts/forgeos.py uninstall [options]
```

Options communes :

- `--tool codex|claude|gemini|all` : adaptateur à gérer (`gemini` cible Google Antigravity `agy` CLI / Antigravity IDE et Gemini CLI) ; défaut `all`.
- `--scope global|local` : installation utilisateur ou projet ; défaut `global`.
- `--target PATH` : projet cible pour une installation locale ; défaut répertoire courant.
- `--home PATH` : remplacement de la racine utilisateur pour une installation globale isolée ou administrée. Cette option sert notamment aux tests et ne doit pas pointer vers un profil réel par accident.

Options d’écriture :

- `--conflict fail|backup` pour `install` et `update` ; défaut `fail`.
- `--include-settings` : consentement explicite à l’installation de `.codex/config.toml`, `.claude/settings.json` et/ou `.gemini/settings.json`.

La portée et la sélection d’outil utilisées par `update`, `status` et `uninstall` doivent correspondre au manifeste de l’installation.

## Installation locale

### Windows PowerShell

```powershell
python .\scripts\forgeos.py install --tool all --scope local --target C:\src\mon-projet
```

### macOS et Linux

```shell
python3 ./scripts/forgeos.py install --tool all --scope local --target /srv/mon-projet
```

Une installation locale place les fichiers dans les emplacements natifs du projet :

| Composant | Codex | Claude Code | Antigravity / Gemini CLI |
| --- | --- | --- | --- |
| Gouvernance | `AGENTS.md` | `AGENTS.md` importé par `.claude/CLAUDE.md` | `AGENTS.md` importé par `.gemini/GEMINI.md` |
| Agents | `.codex/agents/*.toml` | `.claude/agents/*.md` | `.gemini/agents/*.md` (Gemini CLI) et `.gemini/antigravity-agents/*.md` (Antigravity) |
| Découverte Antigravity | — | — | `.agents/agents.json` -> `.gemini/antigravity-agents` (+ `.agents/skills.json` si `gemini` seul) |
| Skills | `.agents/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` | `.gemini/skills/*/SKILL.md` |
| Ressources | `docs/`, `profiles/`, `standards/` | `docs/`, `profiles/`, `standards/` | `docs/`, `profiles/`, `standards/` |
| Propriété | `.forgeos/install-manifest.json` | `.forgeos/install-manifest.json` | `.forgeos/install-manifest.json` |

Une installation `claude` seule conserve ses sources ForgeOS internes sous `.forgeos/sources/` et ne crée pas `.codex/` ou `.agents/`. Une installation `gemini` seule crée uniquement les manifestes de découverte Antigravity `.agents/agents.json` et `.agents/skills.json` (sans `.codex/` ni `.agents/skills/`).

## Installation globale

### Windows PowerShell

```powershell
python .\scripts\forgeos.py install --tool all --scope global
```

### macOS et Linux

```shell
python3 ./scripts/forgeos.py install --tool all --scope global
```

Python résout le répertoire personnel de l’utilisateur sans chemin codé en dur. Les destinations sont identiques dans ce répertoire sur les trois plateformes :

| Composant | Destination globale |
| --- | --- |
| Gouvernance Codex | `~/.codex/AGENTS.md` |
| Agents Codex | `~/.codex/agents/*.toml` |
| Skills Codex | `~/.agents/skills/*/SKILL.md` |
| Entrée Claude | `~/.claude/CLAUDE.md` |
| Agents Claude | `~/.claude/agents/*.md` |
| Skills Claude | `~/.claude/skills/*/SKILL.md` |
| Entrée Gemini | `~/.gemini/GEMINI.md` |
| Gouvernance Antigravity | `~/.gemini/config/GEMINI.md` |
| Découverte agents Antigravity | `~/.gemini/config/agents.json` (-> `~/.gemini/antigravity-agents`) |
| Découverte Skills Antigravity | `~/.gemini/config/skills.json` (-> `~/.gemini/skills`) |
| Agents Gemini CLI | `~/.gemini/agents/*.md` |
| Agents Antigravity | `~/.gemini/antigravity-agents/*.md` |
| Skills Gemini / Antigravity | `~/.gemini/skills/*/SKILL.md` |
| Ressources partagées et manifeste | `~/.forgeos/` |

Les wrappers Claude et Gemini globaux (ainsi que `~/.gemini/config/GEMINI.md`) importent `~/.forgeos/AGENTS.md`. Les références contenues dans les agents sont rendues vers les Skills de la cible afin qu’elles ne dépendent pas du répertoire de travail courant.

## Réglages optionnels

Par défaut, l’installateur ne copie ni `.codex/config.toml`, ni `.claude/settings.json`, ni `.gemini/settings.json`. Il évite ainsi de modifier implicitement le sandbox, les approbations, le niveau de raisonnement ou les permissions d’un utilisateur.

Pour les inclure après inspection :

```shell
python3 scripts/forgeos.py install --tool all --scope global --include-settings
```

L’option doit également être fournie lors d’une mise à jour de cette même installation. Un fichier de réglages préexistant reste protégé par la politique de conflit.

## Conflits et sauvegardes

Le comportement par défaut est transactionnel et conservateur : si un fichier prévu existe mais n’appartient pas au manifeste ForgeOS, la commande s’arrête avant d’écrire.

```shell
python3 scripts/forgeos.py install --tool codex --scope local --target ./app
```

Pour remplacer explicitement les collisions après sauvegarde :

```shell
python3 scripts/forgeos.py install --tool codex --scope local --target ./app --conflict backup
```

Les sauvegardes sont placées sous `.forgeos/backups/`. Lors de la désinstallation, ForgeOS restaure le fichier antérieur lorsqu’aucune modification ultérieure ne rend l’opération ambiguë. Les mises à jour créent également des instantanés de récupération avant de remplacer ou retirer des fichiers gérés.

N’utilisez pas `backup` comme substitut à une sauvegarde du projet ou du profil utilisateur.

## Statut et dérive

```shell
python3 scripts/forgeos.py status --tool all --scope global
```

`status` compare les fichiers possédés avec leurs empreintes dans le manifeste. Un fichier manquant ou modifié est signalé comme dérive. La commande est en lecture seule.

Pour une installation locale :

```shell
python3 scripts/forgeos.py status --tool all --scope local --target ./app
```

## Mise à jour

```shell
python3 scripts/forgeos.py update --tool all --scope global
```

La mise à jour utilise les sources du checkout ForgeOS depuis lequel la commande est exécutée. Elle refuse par défaut d’écraser un fichier géré qui a été modifié. `--conflict backup` autorise explicitement sa sauvegarde puis son remplacement.

Inspectez le nouveau checkout et exécutez ses tests avant une mise à jour globale.

## Désinstallation

```shell
python3 scripts/forgeos.py uninstall --tool all --scope global
```

La désinstallation :

- ne traite que les chemins enregistrés dans le manifeste ;
- ne supprime pas les fichiers applicatifs ou sentinelles extérieurs au manifeste ;
- préserve un fichier ForgeOS modifié au lieu de le détruire ;
- restaure une sauvegarde préexistante lorsque cela reste sûr ;
- conserve le manifeste si des fichiers modifiés empêchent une désinstallation complète.

Les instantanés créés pendant une mise à jour peuvent contenir une modification utilisateur. Ils sont donc conservés sous `.forgeos/backups/` et leur nombre est affiché à la fin de la désinstallation. Après inspection ou archivage, leur suppression reste une décision manuelle.

Après avoir examiné un fichier préservé, restaurez son contenu ForgeOS attendu ou déplacez-le manuellement, puis relancez la désinstallation.

## Tests isolés

Les tests automatisés utilisent `tempfile.TemporaryDirectory` et une racine `--home` injectée. Ils ne doivent jamais viser le profil utilisateur réel.

```shell
python3 -m unittest tests.test_installer -v
```

Exemple de vérification manuelle isolée :

### Windows PowerShell

```powershell
$sandbox = Join-Path $env:TEMP 'forgeos-install-check'
New-Item -ItemType Directory -Force -Path $sandbox | Out-Null
python .\scripts\forgeos.py install --tool all --scope global --home $sandbox
python .\scripts\forgeos.py status --tool all --scope global --home $sandbox
python .\scripts\forgeos.py uninstall --tool all --scope global --home $sandbox
```

### macOS et Linux

```shell
sandbox="$(mktemp -d)"
python3 ./scripts/forgeos.py install --tool all --scope global --home "$sandbox"
python3 ./scripts/forgeos.py status --tool all --scope global --home "$sandbox"
python3 ./scripts/forgeos.py uninstall --tool all --scope global --home "$sandbox"
```

Supprimez ensuite uniquement le répertoire temporaire que vous avez explicitement créé.

## Validation du dépôt ForgeOS

Depuis la racine du dépôt source :

```shell
python3 scripts/claude_adapter.py --check
python3 scripts/gemini_adapter.py --check
python3 scripts/bootstrap.py
python3 tests/bootstrap.py
python3 -m unittest tests.test_installer -v
```

Les validations structurelles ne prouvent pas l’authentification, l’accès réseau ou les permissions distantes de Codex, Claude Code et Gemini CLI.

## Dépannage sûr

- `ForgeOS is not installed` : vérifiez la portée, la cible et le répertoire utilisateur effectif.
- `existing files would be replaced` : inspectez les fichiers listés ; choisissez `backup` uniquement après avoir confirmé la collision.
- `drift or conflicts` : comparez le fichier modifié avec la source ForgeOS avant toute sauvegarde ou mise à jour.
- manifeste invalide : ne le recréez pas à la main ; restaurez-le depuis une sauvegarde fiable ou examinez les fichiers possédés avant une intervention manuelle.
- erreur d’authentification Codex/Claude/Gemini : utilisez les commandes officielles du CLI concerné ; ForgeOS ne gère pas les identifiants.
