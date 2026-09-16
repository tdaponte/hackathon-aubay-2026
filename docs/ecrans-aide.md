# Écrans d’aide — proposition à examiner

Cette étape définit le parcours avant connexion à l’agent. La maquette navigable est disponible sur http://127.0.0.1:8001 quand le service Docker `maquette` est démarré. Elle ne contacte ni Bedrock ni le site source. Ses propositions sont des exemples écrits à l’avance et ses confirmations sont explicitement simulées.

## Intention et présentation

Nom de travail : **Pas à pas**. L’interface s’adresse directement à la personne avec des phrases simples et un ton adulte. Le tutoiement reprend les exemples du scénario ; il reste à valider avec les personnes concernées. Aucun diagnostic n’est affiché ni demandé.

Un écran pose une question. Une date peut avoir trois champs (jour, mois, année) : ils répondent ensemble à la même question. Une liste de cases répond aussi à une seule question. Les écrans de contexte et de récapitulatif sont des exceptions utiles : ils expliquent ou rassemblent les réponses au lieu de demander une nouvelle information.

Les informations apparaissent dans cet ordre :

1. Nom du site accompagné et phase courante : « Mon compte » ou « Mon atelier ».
2. Question en titre, puis courte consigne à proximité du champ.
3. Réponse ou choix, sans présélection des préférences.
4. « Explique-moi » ouvre une explication sous la question, sans perdre la réponse.
5. « Retour » et une action principale au libellé précis.

Pas de conversation vide à démarrer, pas de minuteur, pas d’avancement automatique après une sélection. Les options restent visibles, les cases et boutons sont grands, le texte est aligné à gauche. Les erreurs sont exprimées en mots près du champ, sans code technique. Les instructions essentielles sont toujours visibles ; l’explication facultative apporte seulement du détail.

Le contexte complet reste accessible depuis « De quoi parle ce site ? ». Il s’ouvre dans la même interface et le bouton « Reprendre ma réponse » ramène exactement à la question en cours. La maquette garde les réponses en mémoire tant que la page reste ouverte ; un rechargement remet la simulation à zéro. La reprise après fermeture devra être définie pour la version connectée, sans promesse de sauvegarde durable à ce stade.

## Écran d’entrée : comprendre puis agir

Titre : **« Que peux-tu faire sur ce site ? »**

- Choisir un atelier de peinture, de poterie ou de photo.
- Les ateliers sont gratuits. Le matériel est fourni.
- Les ateliers ont lieu à Bordeaux et sont réservés aux adultes.

Puis : « Je vais t’aider à créer ton compte. Ensuite, tu pourras choisir ton atelier. »

Action principale : **« Commencer mon compte »**. Consulter le contexte ne déclenche aucune inscription.

## Parcours A — Mon compte

| Écran | Question / contenu affiché | Réponse et aide |
| --- | --- | --- |
| A1 | Quel est ton prénom ? | Texte. « Écris ton prénom. » |
| A2 | Quel est ton nom de famille ? | Texte. Explication de la différence avec le prénom. |
| A3 | Quelle est ton adresse e-mail ? | Texte conservé en cas d’erreur. Exemple clairement identifié, jamais utilisé comme correction automatique. |
| A4 | Quelle est ta date de naissance ? | Jour, mois en toutes lettres, année. Relecture de la date complète. |
| A5 | Quel mot de passe veux-tu utiliser ? | Masqué, 12 à 128 caractères. Collage autorisé ; bouton Afficher / Masquer dans la version connectée. |
| A6 | Peux-tu écrire encore ton mot de passe ? | Masqué. En cas de différence, permettre de corriger ou revenir à A5. |
| A7 | As-tu un code d’adhérent ? | Oui / Non, sans présélection. « Ce code n’est pas obligatoire. Tu peux continuer sans code. » |
| A8 conditionnel | Quel est ton code d’adhérent ? | Six chiffres. « Il se trouve sur ta carte d’adhérent. » Action « Continuer sans code ». |
| A9 | Vérifie les informations de ton compte | Prénom, nom, e-mail, date, code ou « Sans code ». Mot de passe : « Renseigné », jamais sa valeur. Modifier chaque réponse. |
| A10 | Confirmation de création | Après retour positif du site uniquement : « Ton compte est créé. Tu n’es pas encore inscrit à un atelier. » |

Sur A9, action explicite **« Créer mon compte »** et explication « Ces informations seront envoyées au site Les ateliers du quartier. Cela crée ton compte. Tu choisiras ton atelier ensuite. » La maquette emploie **« Simuler la création du compte »** et un résultat marqué comme simulation.

Le bouton Retour avant A9 ne crée rien. Après création effective, revenir à une question ne doit pas faire croire que le compte existant sera modifié : la modification de compte est hors périmètre du site. A10 propose « Choisir mon atelier ». Arrêter ici conserve le compte réellement créé, mais aucune inscription.

Les mots de passe de la future interface ne doivent jamais entrer dans les messages du modèle, les traces ou les récapitulatifs. La maquette demande seulement un mot de passe fictif. La séparation entre collecte du secret et contexte du modèle devra être vérifiée lors de l’intégration.

## Parcours B — Mon atelier

| Écran | Question / contenu affiché | Réponse et aide |
| --- | --- | --- |
| B1 | Quel atelier veux-tu faire ? | Trois boutons radio : Peinture, Poterie, Photographie. Une phrase décrit chaque activité. Pour la photo, expliquer les échanges en français et en anglais. |
| B2 | Quand veux-tu venir ? | Deux créneaux compatibles, dates en toutes lettres et horaires visibles. Un seul choix. |
| B3 | As-tu déjà fait cette activité ? | Jamais / De temps en temps / Souvent. Correspondances exactes : aucune / occasionnelle / régulière. |
| B4 | Qu’aimerais-tu faire pendant cet atelier ? | Six cases, une à trois réponses. Nombre de choix visible. L’utilisateur décide quelles cases retirer s’il en coche quatre. |
| B5 | Pourquoi veux-tu participer à cet atelier ? | Texte libre ; consigne sur les 200 caractères. La saisie dans l’aide accepte un texte plus long. « Explique-moi » explique « finalité participative ». |
| B6 conditionnel | Cette version courte te convient-elle ? | Texte initial conservé, proposition distincte, longueur calculée. Accepter, refuser et réécrire. |
| B7 photo seulement | Veux-tu utiliser cette version anglaise ? | Français accepté puis anglais proposé. Accepter, refuser ou demander une explication. |
| B8 | Es-tu d’accord avec ces conditions ? | Gratuit, matériel fourni, inscription pour une seule séance. Oui / Non explicites, sans présélection. |
| B9 | Veux-tu recevoir les nouvelles de l’association ? | Oui / Non explicites. « Tu peux dire non et t’inscrire quand même. » |
| B10 | Vérifie ton inscription | Atelier, créneau, lieu, niveau, attentes, présentation FR/EN et décisions. Modifier chaque réponse. |
| B11 | Résultat de l’inscription | Référence et informations réellement confirmées par le site. Aucun résultat anticipé. |

Sur B10, action **« M’inscrire à cet atelier »**. Explication : « Tes réponses seront envoyées au site. Cela t’inscrit à cette séance. » La maquette utilise **« Simuler mon inscription »**, puis « Exemple de confirmation — aucune inscription envoyée ». Aucun faux identifiant ne doit être présenté comme preuve réelle.

## Explications, erreurs et refus

| Cas | Formulation proposée | Suite possible |
| --- | --- | --- |
| E-mail sans @ | « Il manque le signe @ dans ton adresse. Vérifie ton adresse et écris-la à nouveau. » | Corriger, sans effacer la saisie. Ne pas inventer l’emplacement du @. |
| Fin de domaine manquante | « Vérifie la fin de ton adresse e-mail. Elle contient normalement un point, puis des lettres, comme .fr ou .com. » | L’utilisateur fournit la vraie fin ; aucune extension ajoutée automatiquement. |
| Date impossible | « Cette date n’existe pas. Vérifie le jour, le mois et l’année. » | Conserver les trois parties pour les corriger. |
| Date future | « Ta date de naissance doit être avant aujourd’hui ou aujourd’hui. Vérifie l’année. » | Corriger sans modifier automatiquement. |
| Moins de 18 ans | « Ce site réserve ses ateliers aux personnes de 18 ans ou plus. Vérifie ta date si tu t’es trompé. » | Corriger ou arrêter ; ne pas proposer une date permettant de contourner la règle. |
| Lettre dans le code | « Le code doit contenir 6 chiffres. Vérifie le code sur ta carte. » | Corriger ou continuer sans code. Garder les zéros initiaux. |
| Quatre attentes | « Tu as choisi 4 réponses. Le site en accepte 3 au maximum. Décoche une réponse de ton choix. » | Aucun retrait automatique. |
| Texte trop long | « Ton texte dépasse la limite du site. Je peux te proposer une version plus courte. » | Original conservé ; proposition validée sur sa longueur avant affichage. |
| Refus du raccourcissement | « D’accord. Ton texte de départ est conservé. Tu peux le modifier. » | Retour à la saisie complète ; pas d’insistance ni d’acceptation implicite. Dans l’agent futur : demander une autre proposition ou signaler une idée à garder. |
| Refus de traduction | « Cette version n’est pas retenue. » | Réécrire soi-même, faire expliquer un passage ou demander une autre traduction dans la version connectée. Ne pas demander de certifier une langue que la personne ne comprend pas. |
| Refus des conditions | « Le site demande d’accepter ces conditions pour s’inscrire. Tu peux les relire ou arrêter ici. » | Le Non reste conservé. Aucun envoi possible ; le compte déjà créé reste présent. |
| Refus des actualités | « Tu ne recevras pas les nouvelles de l’association. » | L’inscription continue normalement. |

Pour une traduction, une reformulation en français de son sens peut aider à la compréhension, mais ne constitue pas une preuve indépendante de fidélité. La revue humaine du cas de démonstration devra vérifier les deux versions.

## Retour arrière et modification depuis un récapitulatif

- Retour conserve la saisie, même invalide ou trop longue. Une proposition refusée ne remplace jamais le texte initial.
- « Modifier » ouvre la question choisie. « Enregistrer ma modification » ramène au récapitulatif, sans obliger à refaire toutes les questions.
- Modifier l’activité efface le créneau et demande un nouveau choix. Le niveau, les attentes et le texte français restent visibles pour relecture.
- Modifier le texte français invalide toute traduction acceptée. Une nouvelle version doit être proposée puis acceptée avant l’envoi pour la photo.
- Passer de photo à une autre activité retire l’anglais des données à envoyer. Revenir à la photo exige une nouvelle relecture de l’anglais.
- Une modification des conditions en Non bloque l’envoi, même si le récapitulatif avait été prêt auparavant.
- Une fois envoyé, Retour ne signifie jamais annuler une création réelle. La version actuelle du site n’offre pas d’annulation d’inscription.

## États supplémentaires à prévoir lors de la connexion

| État | Affichage et comportement |
| --- | --- |
| Proposition en cours | « Je prépare une proposition. » Réponse initiale conservée, aucun envoi au site. |
| Agent indisponible | « Je n’arrive pas à préparer la proposition. Ton texte est conservé. » Réessayer ou modifier soi-même. |
| Envoi en cours | « J’envoie tes réponses au site. » Bloquer le double envoi. |
| Réponse du site incertaine | « Je n’ai pas encore pu vérifier si ton inscription est enregistrée. » Vérifier l’état avant de proposer un nouvel envoi. |
| Refus du site | Expliquer l’erreur et ouvrir la question concernée en conservant les autres réponses ; redemander les mots de passe si le site les a effacés. |
| Session expirée | Expliquer la perte de session. Ne pas annoncer de réussite ni promettre la reconnexion, qui est hors périmètre du site. |

Ces états réseau sont décrits ici mais ne sont pas simulés par la maquette locale : celle-ci sert à relire les écrans, pas à valider l’automatisation.

## Scénario de revue

1. Lire le contexte : comprendre le prix, le lieu et les deux démarches.
2. Saisir un e-mail incorrect ; vérifier que l’erreur explique quoi corriger sans inventer l’adresse.
3. Revenir en arrière et demander une explication : les réponses doivent être conservées.
4. Vérifier le récapitulatif du compte, modifier une réponse, puis simuler sa création.
5. Choisir la photo, un créneau et quatre attentes ; retirer soi-même une attente.
6. Charger le texte long de démonstration depuis les outils de revue, refuser sa proposition courte, puis accepter après relecture.
7. Refuser la traduction puis reprendre ; vérifier que le refus n’a rien accepté.
8. Dire Non aux actualités et vérifier que cela ne bloque pas l’inscription.
9. Depuis le récapitulatif, modifier l’activité ou le français : contrôler le nouveau créneau et la traduction invalidée.
10. Simuler l’envoi et vérifier que le résultat est clairement distinct d’une inscription réelle.

Questions de revue : les mots sont-ils compréhensibles ? La différence compte/inscription est-elle claire ? Les actions de refus sont-elles faciles à trouver ? Le parcours paraît-il trop long ? Ces points restent à examiner avec des utilisateurs concernés ; la maquette n’est pas une validation FALC ni une preuve de conformité.

## Références de conception

Les choix s’appuient sur les conseils complémentaires W3C COGA : [instructions par étapes](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o4p07-step-instructions/), [retour sans perte de données](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o4p02-back-undo/) et [correction des formulaires](https://www.w3.org/WAI/WCAG2/supplemental/patterns/o4p05-form-undo/). Ils guident la conception, sans remplacer des tests avec les personnes concernées.
