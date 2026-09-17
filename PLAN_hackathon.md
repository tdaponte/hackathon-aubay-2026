# Suivi du plan du hackathon

Ce fichier récapitule les étapes déjà convenues dans la conversation ; il n’existait pas dans le dépôt avant cette mise à jour.

| Étape | Objet | État |
| --- | --- | --- |
| 1 | Décrire le site avant de le coder | Réalisée ; spécification mise à jour pour le parcours simplifié |
| 2 | Implémenter le site fictif | Réalisée ; compte et réservation simplifiés |
| 3 | Valider l’accès à Bedrock | Réalisée : Nova 2 Lite, eu-west-1 ; voir le compte rendu |
| 4 | Définir les écrans d’aide et examiner le parcours | Validée par l’utilisateur |
| 5 | Connecter extraction, validation et actions | Réalisée et validée ; première orchestration programmée |
| 6 | Ajouter les aides IA et les actions, avec découverte et pilotage agentiques | Implémentée et testée ; prête à la relecture utilisateur |

L’étape 6 reprend l’intitulé du plan initial : « Ajouter les aides IA et les actions : raccourcissement, traduction, explications et remplissage accepté par l’utilisateur ». Dans le périmètre court validé, raccourcissement et traduction restent retirés. Les explications et les actions acceptées sont conservées ; le modèle choisit désormais ses outils et découvre le parcours depuis le catalogue.

L’aide sur le port 8001 pilote le site du port 8000 avec Playwright. L’agent LangChain/Nova 2 Lite observe, choisit un lien, présente les questions, demande les envois autorisés et adapte la suite aux résultats. Les deux récapitulatifs restent obligatoires. La référence finale provient du site. Le mode simulé de l’étape 4 a été supprimé lors du nettoyage final.

Voir [la connexion de l’agent](docs/connexion-agent.md) pour les responsabilités des composants et les limites du périmètre.

Vérifications de l’étape 6 : 31 tests serveur et 12 tests d’aide réussis. Parcours réel avec routes déplacées, identifiant/libellés modifiés, consigne malveillante dans la page et refus serveur d’e-mail : réservation confirmée. Récupération en lecture seule et refus des doublons vérifiés sur une base temporaire. L’essai de variante a pris 24,64 secondes hors saisie humaine pour 11 appels au modèle ; ce n’est pas une répétition orale. Le déroulé oral reste à chronométrer avec le présentateur.

Le parcours navigateur Streamlit a aussi réussi : une erreur d’e-mail, retour arrière, modification depuis le récapitulatif, changement d’activité, secret masqué, clavier et largeurs 320/390 px. Durée automatisée : 28,28 secondes ; référence ADQ-DA26A168C65E retrouvée en base. Aucune erreur JavaScript détectée. L’ancienne base a conservé son empreinte SHA-256.

Voir [les écrans d’aide](docs/ecrans-aide.md), [le site simplifié](docs/site-fictif-specification.md) et [la démonstration de cinq minutes](docs/demo-cinq-minutes.md).

## Refonte demandée : contexte et conversation

L’aide affiche désormais le contexte stable de l’association à gauche et les deux actions à droite. Le clic ouvre une conversation guidée. La création, la connexion à un compte existant et la réservation sont des démarches séparées, choisies par l’utilisateur. Sans connexion, la réservation affiche une invitation à créer un compte ou se connecter. Le modèle découvre le formulaire correspondant à chaque choix ; après réussite, il rend la main.

Une page de connexion réelle a été ajoutée au site source, avec vérification scrypt, protection CSRF et message générique en cas de refus. Cette première refonte n’avait pas changé le schéma ni supprimé de données. Le jargon reste sur le site source ; l’aide affiche des questions simples, « Mot de passe » et « Date et horaire », jusque dans les récapitulatifs. Le contexte était initialement éditorial dans `aide/context.json` ; il a été remplacé par la lecture dynamique décrite ci-dessous.

Vérifications de cette refonte : 35 tests serveur et 16 tests d’aide réussis. Parcours navigateur avec Bedrock : accueil, réservation bloquée sans connexion, création, erreur d’e-mail et correction, retour, modification du prénom et de l’activité, créneau effacé, réservation prouvée puis connexion au compte existant depuis une nouvelle session. Largeurs 320/390 px, secret masqué et choix au clavier contrôlés. Les captures et le dernier résultat sont dans `output/interface-conversationnelle/`. L’ancienne base conserve son empreinte SHA-256.

## Démonstration liée au vrai site et accueil issu de la lecture

Le bouton « M’aider avec ce site » ouvre Streamlit dans un autre onglet et relie la session du site à celle de Playwright. Une table de tickets temporaires a été ajoutée à la base v2, sans modifier les comptes ni réservations existants. L’identité du compte est visible sur le site, avec un accès aux réservations et une déconnexion. Les anciens essais restent rattachés à leurs comptes ; aucun effacement n’est nécessaire pour une nouvelle démonstration.

L’agent observe le catalogue puis appelle `presenter_accueil` pour proposer le contexte et les actions. Les actions doivent référencer des liens observés. Ce contexte généré reste stable pendant les questions ; le mode connecté ne lit plus le fichier de contexte éditorial. La liaison technique de session n’est pas exposée au modèle. Un accès direct à Streamlit invite à ouvrir l’aide depuis le site.

Validation : 37 tests serveur et 17 tests d’aide réussis. Le test navigateur avec Bedrock a créé un compte, vérifié son identité et l’absence de réservation sur le site, réservé puis retrouvé **ADQ-4C25A85FC671** dans les deux interfaces. Déconnexion et reconnexion vérifiées, ancienne session révoquée, aucun mélange de comptes. Durée automatisée : 64,95 secondes, incluant les corrections, modifications et reconnexion ; le temps de parole reste à répéter. Captures `preuve-compte-site.png` et `preuve-reservation-site.png` dans `output/interface-conversationnelle/`.

## Nettoyage et préparation finale

Suppression du mode simulé, du contexte fixe, du style de l’ancienne interface, des scripts de vérification de la maquette et du parcours à routes fixes, ainsi que de l’ancien appel de reformulation isolé. Le navigateur de base ne conserve que les primitives utiles. Les jeux de données factices restants sont réservés aux tests ; ceux-ci vérifient maintenant le rendu de l’interface connectée. Les données locales et les fichiers d’accès sont préservés.

Contrôles de santé Docker ajoutés aux deux services. `scripts/prepare-demo.cmd` démarre les services et teste réellement Playwright et les appels d’outils Bedrock, sans création de compte. `--build --full` reconstruit puis répète le parcours avec captures et vidéos. Dernière validation : 37 tests serveur, 18 tests d’aide ; précontrôle prêt en 4,57 secondes ; parcours réel en 59,60 secondes, référence **ADQ-7AA327509578**, visible dans les deux interfaces. Vidéos de secours dans `output/demo-secours/`. Voir [la préparation](docs/preparation-demo.md).

Limite du nettoyage local : le contrôle automatique a refusé les commandes de suppression récursive, y compris une commande limitée au cache pytest, sans motif détaillé. Les anciens répertoires `.venv`, `.pytest_cache` et les anciens résultats dans `output/` restent donc présents et exclus du code livré ; ils ne sont pas utilisés par la solution finale. Le dossier `maquette-aide` est vide. Les suppressions ciblées de code ont réussi.
