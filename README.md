# Hackathon Aubay 2026 — Pazapa

Une aide à l’accessibilité cognitive pour comprendre le site des ateliers, créer un compte et réserver une séance. L’étape 6 utilise un **agent LangChain/Nova 2 Lite qui choisit ses outils**, découvre les formulaires depuis le catalogue et interprète les résultats de Playwright. Les confirmations créent réellement des données dans la base locale du démonstrateur.

## Démarrer

Docker Desktop doit fonctionner. Le fichier local `.env.bedrock` doit contenir les accès déjà configurés (voir `.env.bedrock.example`). Ne jamais publier ce fichier.

```powershell
docker compose up -d --build
```

- [Site source](http://127.0.0.1:8000/) : commencer ici, puis cliquer **M’aider avec ce site**. L’aide s’ouvre dans un autre onglet lié à la même session.
- [Aide connectée](http://127.0.0.1:8001/) : une ouverture directe invite à repartir du site pour établir la liaison.

Le service de l’aide conserve son nom historique `maquette`. Aucun Python Windows n’est nécessaire. Utiliser uniquement des données fictives et une adresse différente à chaque création, par exemple `alex.demo17@example.test`. Une adresse déjà enregistrée est refusée. Mot de passe fictif : `AtelierDemo2026!`.

L’accueil présente un contexte stable à gauche et les actions à droite. Une conversation guidée recueille une réponse à la fois. La création, la connexion à un compte existant et la réservation ont chacune un récapitulatif à confirmer. La réservation est accessible après authentification ; créer un compte ne lance pas automatiquement cette démarche. La confirmation finale affiche la référence réellement lue sur le site, avec une capture consultable. Il n’y a ni paiement ni courriel envoyé.

L’agent lit le catalogue avec Playwright, puis propose le contexte et les actions via `presenter_accueil`. Les liens proposés doivent appartenir aux liens observés. Le contexte reste identique pendant les démarches. Les questions, explications et libellés courts sont préparés à partir du formulaire découvert. « Mot de passe » et « Date et horaire » sont également garantis par la présentation ; le jargon reste sur le site source. Cette lecture n’est pas un audit de conformité RGAA.

Après création ou réservation, revenir dans l’onglet source (il s’actualise au retour, sinon actualiser manuellement) : l’identité connectée et « Mon compte et mes réservations » montrent les données réelles du même compte. Le lien équivalent dans Streamlit ouvre cette page. Si un ancien compte est connecté, cliquer **Se déconnecter** sur le site avant de lancer une nouvelle démonstration. Les anciens comptes et réservations restent en base ; ils ne sont jamais mélangés avec ceux d’un nouveau compte.

## Fonctionnement

1. Le bouton du site établit une liaison de session. L’agent observe le catalogue et présente le contexte et les actions. L’utilisateur choisit une démarche ; l’agent découvre son formulaire.
2. Les résultats Playwright sont renvoyés au modèle avec `ToolMessage`. Celui-ci choisit la prochaine opération et prépare les questions accessibles.
3. Streamlit recueille les réponses en session. Les valeurs personnelles et le mot de passe ne sont pas envoyés au modèle.
4. Après confirmation du récapitulatif, l’agent peut demander l’envoi. Le programme contrôle et consomme cet accord avant le POST.
5. Le modèle reçoit le résultat : il choisit de demander une correction, vérifier une opération incertaine ou afficher une confirmation prouvée. Une autre démarche demande un nouveau choix explicite de l’utilisateur.

Les appels IA dépendent des décisions et reprises : la limite de deux analyses est supprimée. Chaque reprise est limitée à six appels au modèle et s’arrête après deux actions identiques sans progrès. Retour arrière et validation simple d’e-mail restent programmés. Les adresses de formulaires sont découvertes ; la lecture des preuves de réussite reste adaptée au site d’ateliers. Le prototype n’est pas un agent universel.

Fichiers principaux : `aide/agent_browser.py` (navigation découverte et actions contrôlées), `aide/connected.py` (boucle agentique), `aide/planner.py` (connexion Bedrock et description), `aide/model.py` (état/validation), `aide/app.py` (rendu). `aide/browser.py` contient seulement les primitives de navigateur et la lecture des preuves. `ateliers/` contient le serveur FastAPI du site. Aucun serveur intermédiaire supplémentaire n’est nécessaire.

Dans l’aide, ouvrir **Vue technique — appels de l’agent** pour consulter les outils réellement demandés, résultats et durées. Le journal exclut les données personnelles et le raisonnement interne du modèle.

## Préparer la démonstration

Depuis la racine, lancer le contrôle avant l’oral :

```powershell
.\scripts\prepare-demo.cmd
```

Il attend que les deux services soient sains, puis vérifie Playwright et un vrai échange agentique Bedrock, sans créer de compte ni de réservation. Après une modification du code, utiliser `--build`. Pour une répétition automatisée complète avec captures et vidéos de secours : `.\scripts\prepare-demo.cmd --build --full`. Cette option crée un compte et une réservation fictifs. Les vidéos se trouvent dans `output/demo-secours/` ; elles montrent un parcours automatisé enregistré, sans narration, à annoncer comme tel en cas de panne.

Le lanceur Windows `.cmd` fonctionne sans Python local et sans modifier la politique d’exécution PowerShell. Le mode simulé et l’ancien adaptateur à routes prédéfinies ont été supprimés. Voir [la préparation détaillée](docs/preparation-demo.md).

## Données et arrêt

La base utilisée est `data/ateliers-v2.sqlite3`. L’ancienne `data/ateliers.sqlite3` est préservée. Les réponses et cookies de l’aide restent en mémoire de session ; recharger l’aide peut perdre cette session et **ne supprime pas les comptes déjà créés**. Le mot de passe est effacé de l’aide après création confirmée du compte ; le site conserve son empreinte scrypt.

Pour effacer explicitement les données de la nouvelle base de démonstration uniquement :

```powershell
docker compose exec site python -m ateliers reset --yes
```

Recharger ensuite les deux interfaces. Pour arrêter en conservant les données :

```powershell
docker compose down
```

## Vérifications

```powershell
docker build --target tests -t aubay-ateliers-tests .
$taskRepo = (Get-Location).Path
docker run --rm --mount "type=bind,source=$taskRepo,target=/app" aubay-ateliers-tests python -m pytest -q
docker run --rm --mount "type=bind,source=$taskRepo,target=/app" hackathon-aubay-2026-maquette python -m unittest discover -s aide/tests -v
docker run --rm --mount "type=bind,source=$taskRepo,target=/app" aubay-ateliers-tests python scripts/check_connected.py
```

Les tests unitaires utilisent des doublures pour les opérations externes. **Le dernier test utilise réellement Bedrock, crée un compte et une réservation fictifs puis se reconnecte à ce compte dans une nouvelle session.** Il produit ses captures, sa durée et sa référence dans `output/interface-conversationnelle/`. Le script `scripts/browser_check.py` teste séparément le site avec une base temporaire. Les données de test sont confinées dans `aide/tests/fixtures/` et ne sont jamais chargées par l’application. Voir la documentation de connexion pour les essais de routes déplacées, refus serveur et injection de consignes.

## Documents

- [Connexion et limites de l’agent](docs/connexion-agent.md).
- [Écrans d’aide](docs/ecrans-aide.md).
- [Démonstration de cinq minutes](docs/demo-cinq-minutes.md).
- [Préparation et secours](docs/preparation-demo.md).
- [Site source simplifié](docs/site-fictif-specification.md).
- [Configuration Bedrock](docs/bedrock-acces.md).
- [Suivi du plan](PLAN_hackathon.md).
