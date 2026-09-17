# Interface d’aide Streamlit

L’application finale utilise uniquement le parcours connecté. L’ancienne revue simulée a été retirée.

## Interface connectée actuelle

L’entrée est le bouton « M’aider avec ce site » du site source. Il ouvre Streamlit dans un autre onglet en liant les sessions. L’agent lit alors le catalogue et prépare le contexte à gauche et les actions à droite avec `presenter_accueil`. Les intitulés des actions viennent du modèle ; création et connexion sont regroupées dans une entrée compte. Les liens doivent avoir été observés. Le contexte explique l’association, les activités et leurs conditions d’après le site, puis reste stable pendant la conversation. Sans connexion, la réservation affiche une invitation à se connecter ou créer un compte. Sur mobile, le contexte précède les actions.

Le choix du compte propose la création ou la connexion. L’agent découvre le formulaire correspondant, génère les questions et leurs explications, puis rend la main. Une conversation montre les questions et les réponses déjà données ; la réponse courante utilise un champ texte, un champ masqué ou des choix sans présélection. « Explique-moi », « Retour » et « Modifier » restent disponibles. Le mot de passe ne figure jamais en clair dans la conversation ni le récapitulatif.

Les libellés affichés sont distincts des libellés techniques extraits : « Mot de passe » et « Date et horaire » remplacent le jargon, aussi dans les récapitulatifs. Le modèle propose les mots simples ; la présentation normalise également les deux termes demandés. Les identifiants et contraintes du formulaire restent ceux du site.

La création demande prénom, e-mail et mot de passe. La connexion demande e-mail et mot de passe. Après confirmation et preuve du site, l’aide annonce la réussite puis propose de réserver, sans démarrer automatiquement la réservation. Celle-ci demande une activité et un créneau compatible, puis un accord final. Changer d’activité efface le créneau précédent.

Après chaque réussite, « Voir mon compte et mes réservations sur le site » ouvre la vraie page source. L’onglet d’origine affiche également les nouvelles données après actualisation. Le site montre le prénom et l’e-mail du compte connecté, ses seules réservations et un bouton de déconnexion. Il n’affiche pas les réservations des autres comptes.

« Retour aux actions » abandonne la conversation et efface le secret saisi, en conservant la connexion déjà établie. Un envoi incertain doit d’abord être vérifié en lecture seule. Une « Vue technique — appels de l’agent » montre les outils et résultats réels. Voir [la connexion actuelle](connexion-agent.md).
