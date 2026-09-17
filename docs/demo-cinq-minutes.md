# Démonstration connectée de cinq minutes

Avant l’oral : démarrer Docker, vérifier l’accès Bedrock et ouvrir le site sur le port 8000. Si un ancien compte est connecté, cliquer « Se déconnecter ». Préparer une adresse fictive **encore inutilisée**. Ouvrir l’aide uniquement avec le bouton du site pour partager sa session. Répéter avec le présentateur et chronométrer : les temps réseau varient.

| Temps | Action | Explication |
| --- | --- | --- |
| 0:00–0:40 | Montrer catalogue et formulaire du site source | Informations dispersées et vocabulaire administratif ; créer un compte ne réserve rien |
| 0:40–1:15 | Cliquer « M’aider avec ce site » ; montrer le contexte et les actions préparés ; choisir la création de compte | L’agent lit le catalogue puis découvre les champs à expliquer |
| 1:15–2:40 | Prénom, une erreur d’e-mail, correction, mot de passe et récapitulatif ; créer le compte puis revenir brièvement dans l’onglet source | Le prénom et l’e-mail sont affichés sur le vrai site ; aucune réservation encore |
| 2:40–4:10 | Cliquer « Réserver une activité », choisir Photographie puis le 10 octobre ; revoir la réservation | Compte réellement créé ; démarche choisie explicitement ; créneaux lus sur le site ; possibilité de modifier avant l’envoi |
| 4:10–5:00 | Cliquer « Réserver cet atelier » ; retourner sur le site source et montrer la même référence dans les réservations ; si le temps le permet, montrer la vue technique | Le compte et la réservation sont visibles dans les deux interfaces grâce à la session partagée |

Données possibles : Alex ; `alex.demo17example.test` puis `alex.demo17@example.test` ; `AtelierDemo2026!` ; Photographie ; 10 octobre 2026, 14 h–16 h. Changer le suffixe `17` à chaque répétition. Une seule erreur volontaire suffit ; conserver les autres cas pour les questions du jury.

Phrase pédagogique : « L’agent choisit un outil, reçoit son résultat et décide de la suite. Bedrock lui donne accès au modèle Nova. Playwright agit dans le navigateur. Le programme garde mes réponses, contrôle les règles simples et impose ma confirmation avant chaque envoi. »

Le contexte et les actions de l’accueil sont produits par le modèle à partir de sa lecture du site. Le contexte reste ensuite stable pendant la conversation. Les questions et explications viennent également du modèle. La connexion à un compte existant fonctionne : la garder pour les questions du jury. Le mot de passe reste masqué et hors des messages du modèle.

Ouvrir « Vue technique — appels de l’agent » pour montrer observer_page, ouvrir_lien, envoyer_formulaire et leurs résultats. Ce sont des événements réels, pas le raisonnement interne du modèle. L’absence de @ est détectée par le programme : ne pas l’attribuer à l’IA. Le scénario séparé de routes déplacées et refus serveur est conservé pour les questions du jury, afin de garder une seule erreur volontaire pendant l’oral.

Le bouton « M’aider avec ce site » relie la session du navigateur utilisateur à celle pilotée par Playwright. La capture est une preuve complémentaire : le compte et la réservation sont aussi visibles directement dans l’onglet source, après actualisation. Ne pas changer de navigateur ou de profil entre les deux interfaces.

Si Bedrock échoue après création du compte, utiliser « Reprendre l’analyse » : aucun nouvel accord d’envoi n’est donné et le compte reste créé. Si l’envoi a un résultat incertain, utiliser « Vérifier auprès du site » : aucun formulaire n’est renvoyé. En cas de panne persistante, montrer les vidéos de secours en annonçant explicitement qu’il s’agit d’un parcours réel enregistré. Le mode simulé a été supprimé.

Les essais automatisés de l’agent ont pris environ 20 à 25 secondes hors saisie humaine selon le scénario, avec 10 à 13 appels au modèle. Ces mesures ponctuelles ne garantissent pas la latence future. Répéter l’oral avec les explications et conserver une marge dans les cinq minutes.

Avec la liaison des deux onglets et l’accueil généré par l’agent, l’essai navigateur a pris 64,95 secondes avec saisie automatisée, une erreur d’e-mail, un changement d’activité, les preuves sur le site et une reconnexion au compte. Ce résultat inclut les outils et l’interface mais ne mesure pas le temps d’une personne qui lit, répond et présente le projet. La reconnexion n’est pas nécessaire pendant les cinq minutes de démonstration.

Oral : 2 minutes pour le besoin, 5 pour la démonstration, 2 pour l’architecture, 1 pour les limites et perspectives ; puis 3 minutes de questions. Préciser que l’adaptateur couvre ce site et que le vocabulaire reste à évaluer avec les personnes concernées.
