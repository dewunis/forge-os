# Git workflow and release process

## Branches

- `main` contient uniquement les versions stables ou les candidats validés.
- `dev` est la branche d'intégration. Elle est créée depuis `main` et reçoit les
  changements vérifiés avant toute proposition de promotion.
- Une évolution isolée peut utiliser une branche courte issue de `dev`, puis
  revenir dans `dev` par revue.

L'historique ne doit pas être réécrit. Les force-pushes, suppressions de branche
stable et contournements de protection sont interdits.

## Commits

Les nouveaux commits suivent Conventional Commits : `feat`, `fix`, `docs`,
`test`, `refactor`, `perf`, `build`, `ci`, `chore` ou `revert`, avec un scope
facultatif. Un commit doit représenter une unité cohérente et ne doit contenir
ni secret, ni fichier temporaire, ni résultat présenté comme vérifié sans preuve.

## Préparation d'une release

1. Partir d'un `dev` propre et identifier le commit candidat.
2. Déduire la version du comportement public réellement vérifié et mettre à
   jour le changelog canonique.
3. Exécuter les contrôles de synchronisation, le bootstrap, les tests
   structurels et les tests de l'installateur.
4. Faire examiner les changements significatifs par un reviewer indépendant.
5. Ouvrir une pull request `dev` vers `main` et attendre les contrôles et
   approbations requis.
6. Après autorisation, fusionner sans réécrire l'historique et revérifier le
   commit exact de `main`.
7. Après autorisation distincte, créer le tag annoté `vX.Y.Z` sur ce commit,
   pousser le tag et publier la GitHub Release depuis `main`.

Une préparation réussie n'autorise pas le merge, le tag, la publication ou le
déploiement. Une validation critique en échec bloque la release.

## Protections GitHub recommandées

Configurer une ruleset pour `main` exigeant une pull request, au moins une revue
indépendante, la résolution des conversations et les contrôles automatisés
requis. Interdire les force-pushes et la suppression de `main`. Protéger aussi
les tags `v*` contre la modification et la suppression non autorisées.

ForgeOS documente ces contrôles mais ne les active pas implicitement : leur
configuration GitHub requiert une autorisation et des droits de dépôt adaptés.

## Récupération

Si un tag local incorrect est détecté, ne pas le pousser : suspendre la release,
documenter l'écart et demander une autorisation explicite avant toute correction.
Après publication, ne jamais déplacer silencieusement un tag ; choisir avec le
propriétaire du dépôt une correction explicite ou une nouvelle version. Les
défauts publiés sont corrigés par un commit et une version ultérieure, sans
réécriture de l'historique.
