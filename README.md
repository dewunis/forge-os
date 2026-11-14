# ForgeOS

ForgeOS est une organisation d’ingénierie logicielle multi-agents utilisable avec OpenAI Codex et Claude Code. Elle fournit une gouvernance CTO commune, 17 spécialistes, 16 procédures réutilisables, des profils technologiques et un installateur Python sûr pour Windows, macOS et Linux.

ForgeOS n’est ni un système d’exploitation ni un framework applicatif. Il organise le travail des agents autour du code et des conventions déjà présents dans un projet.

## Principes

- Le code, les tests, les manifestes et les configurations réelles priment sur les profils ForgeOS.
- Le CTO mobilise uniquement les spécialistes nécessaires et conserve l’arbitrage technique.
- Les opérations sensibles, de production et de publication restent soumises à autorisation humaine.
- Les changements importants exigent une revue indépendante.
- Les technologies, dépendances et modèles ne sont jamais installés ou remplacés implicitement.

## Architecture

`AGENTS.md` est la gouvernance commune. Les rôles canoniques se trouvent dans `.codex/agents/` et les Skills canoniques dans `.agents/skills/`. L’adaptateur Claude Code génère ses agents et son miroir de Skills sous `.claude/`.

```text
Utilisateur
  └─ CTO ForgeOS
      ├─ cadrage : Product Manager, Software Architect, UI/UX Designer
      ├─ livraison : Tech Lead et ingénieurs spécialisés
      ├─ assurance : QA, Security, Performance, Code Reviewer
      └─ documentation et release : Technical Writer, Release Manager

Sources ForgeOS
  ├─ AGENTS.md
  ├─ .codex/agents/*.toml
  └─ .agents/skills/*/SKILL.md
        └─ adaptateur généré : .claude/agents + .claude/skills
```

Les profils de `profiles/` sont un catalogue de technologies, jamais une preuve des versions installées dans un projet.

## Agents

ForgeOS comprend 17 sous-agents :

| Domaine | Agents |
| --- | --- |
| Produit et architecture | Product Manager + Business Analyst, Software Architect, Tech Lead |
| Développement | Frontend Engineer, Backend Engineer, Mobile Engineer, Database Engineer, AI/LLM Engineer |
| Expérience | UI/UX Designer |
| Plateforme et exploitation | Platform / DevOps Engineer, Reliability Engineer |
| Qualité et sécurité | QA Engineer, Security Engineer, Performance Engineer, Code Reviewer |
| Documentation et livraison | Technical Writer & API Documentation Engineer, Release Manager |

Le CTO est l’orchestrateur racine et n’est pas compté parmi ces 17 sous-agents.

## Skills

Les 16 Skills couvrent : développement frontend, backend, mobile et IA ; migrations de données ; UI/UX ; CI/CD ; réponse aux incidents ; audits de performance et de sécurité ; documentation API ; tests ; revue de code ; gestion de release ; versionnement sémantique ; génération de changelog.

Chaque Skill utilise un manifeste obligatoire `SKILL.md`. Les copies sous `.claude/skills/` sont générées pour la découverte Claude Code et ne doivent pas être modifiées directement.

## Technologies couvertes

- Backend : Laravel/PHP, NestJS/TypeScript, FastAPI/Python.
- Web : Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Nuxt et Vue.
- Mobile : Expo, React Native, Expo Router, React Native Reusables, NativeWind et Uniwind.
- Données : PostgreSQL, MySQL/MariaDB, Redis et SQLite mobile lorsque justifié.
- Plateforme : Docker, GitHub Actions, Linux, Nginx, Caddy et Terraform dans un périmètre autorisé.
- Qualité : Pest/PHPUnit, Vitest, Jest, Playwright, Maestro, Lighthouse, k6 et outils natifs du projet.

ForgeOS n’installe aucune de ces technologies. Il détecte et respecte les versions réellement présentes.

## Prérequis

- Python 3.9 ou version ultérieure pour l’installateur, sans dépendance externe.
- Codex et/ou Claude Code installés et authentifiés séparément.
- Python 3.11 ou version ultérieure pour le validateur source `scripts/bootstrap.py`, qui utilise `tomllib`.

## Installation

Installation locale dans un projet :

```shell
python scripts/forgeos.py install --tool all --scope local --target /chemin/du/projet
```

Installation globale pour l’utilisateur courant :

```shell
python scripts/forgeos.py install --tool all --scope global
```

Valeurs disponibles pour `--tool` : `codex`, `claude` ou `all`. La portée `local` utilise le projet ciblé ; la portée `global` utilise le répertoire personnel retourné par Python et les dossiers natifs `.codex`, `.agents/skills` et `.claude`.

Les fichiers de réglages qui influencent le sandbox, les approbations ou les permissions ne sont pas installés par défaut. Leur installation exige un consentement explicite :

```shell
python scripts/forgeos.py install --tool all --scope local --target /chemin/du/projet --include-settings
```

Si un fichier existe déjà, l’installation s’arrête sans mutation. Pour demander explicitement sa sauvegarde avant remplacement :

```shell
python scripts/forgeos.py install --tool all --scope local --target /chemin/du/projet --conflict backup
```

Consultez [docs/installation.md](docs/installation.md) pour les chemins, les sauvegardes, les codes de résultat et les exemples Windows, macOS et Linux.

## Utilisation et maintenance

```shell
python scripts/forgeos.py status --tool all --scope global
python scripts/forgeos.py update --tool all --scope global
python scripts/forgeos.py uninstall --tool all --scope global
```

Pour une installation locale, ajoutez `--target /chemin/du/projet`. La sélection d’outil et la portée doivent correspondre au manifeste créé lors de l’installation.

L’installateur maintient un manifeste `.forgeos/install-manifest.json` avec les empreintes des fichiers qu’il possède. Une modification utilisateur est signalée comme dérive et n’est ni écrasée ni supprimée sans choix explicite. La désinstallation ne touche pas les fichiers extérieurs au manifeste et restaure les sauvegardes préexistantes lorsqu’elle peut le faire sans perte.

## Validation du dépôt source

```shell
python scripts/claude_adapter.py --check
python scripts/bootstrap.py
python tests/bootstrap.py
python -m unittest tests.test_installer -v
```

Les tests de l’installateur utilisent uniquement des répertoires temporaires. Ils ne modifient pas la configuration globale réelle.

## Sécurité

- Aucun secret, token ou fichier d’environnement réel ne doit être copié dans ForgeOS.
- Les instructions d’agents sont une gouvernance, pas une frontière de sécurité.
- Les permissions effectives dépendent du sandbox, des identités, des règles Git, de la CI et des environnements protégés.
- Aucun push, merge, tag, déploiement ou changement de production n’est autorisé implicitement.
- L’option `--include-settings` et le mode de conflit `backup` sont des consentements explicites à des mutations supplémentaires ; inspectez toujours leur portée avant exécution.

## Limitations

- L’installateur ne configure ni l’authentification Codex/Claude ni les permissions distantes.
- Les profils technologiques sont indicatifs et n’installent aucune dépendance.
- Une gouvernance utilisateur existante peut entrer en conflit avec ForgeOS ; le comportement par défaut est alors l’arrêt sans écriture.
- Les instantanés de récupération créés pendant une mise à jour sont conservés après désinstallation lorsqu’ils peuvent contenir des modifications utilisateur ; le CLI signale leur emplacement pour nettoyage manuel.
- La compatibilité multiplateforme repose sur la bibliothèque standard Python et doit également être vérifiée dans la CI native de chaque système avant une distribution publique.
- Les réglages et formats natifs de Codex et Claude Code peuvent évoluer ; validez une mise à jour de CLI avant de la généraliser.

## Contribution

1. Préservez `AGENTS.md`, `.codex/agents/` et `.agents/skills/` comme sources de vérité.
2. Régénérez l’adaptateur Claude avec `python scripts/claude_adapter.py`.
3. N’éditez pas manuellement les fichiers générés sous `.claude/agents/` ou `.claude/skills/`.
4. Ajoutez ou adaptez les tests isolés pour toute évolution de l’installateur.
5. Exécutez toutes les validations ci-dessus et documentez uniquement les résultats réellement observés.
6. Ne modifiez pas les conventions du code applicatif au nom des conventions internes ForgeOS.
