# Les ateliers du quartier — Fiche du site fictif

**Étape 1 : décrire le site avant de le coder.**

Cette fiche constitue la proposition de référence à relire ensemble. Elle décrit le site source, ses contenus et ses règles. Les explications attendues de l’assistant servent de critères de démonstration ; l’interface d’aide sera conçue à l’étape suivante prévue pour elle.

## 1. Le service et l’histoire de la démonstration

« Les ateliers du quartier » est une association fictive bordelaise qui organise des ateliers gratuits de peinture, de poterie et de photographie. Les ateliers photo réunissent des participants francophones et anglophones. Une courte présentation dans les deux langues facilite leur mise en relation.

Le personnage de démonstration est Alex Martin, un adulte ayant une trisomie 21. Alex sait naviguer, lire des phrases simples et saisir des réponses courtes. Ses besoins dans ce scénario concernent la compréhension des consignes, l’organisation des étapes et la correction des erreurs. Ce personnage ne représente pas les capacités de toutes les personnes ayant une trisomie 21.

**Objectif d’Alex : créer son compte, puis s’inscrire à un atelier photo.**

**Résultat observable :** le site affiche une référence d’inscription, l’activité, le créneau et les choix enregistrés. La réussite repose sur l’enregistrement effectif par le site.

Toutes les personnes, coordonnées et inscriptions de la démonstration sont fictives. Les ateliers sont gratuits, le matériel est fourni et aucun règlement bancaire n’est demandé. Le lieu affiché est « Maison des ateliers — Bordeaux, lieu fictif ».

## 2. Les quatre pages

| Page | Adresse prévue | Contenu et fonction |
| --- | --- | --- |
| Les ateliers | `/` | Présentation dense de l’association, catalogue et conditions ; accès à la création du compte |
| Création du compte | `/compte/creation` | Identité, courriel, mot de passe, date de naissance et code d’adhérent facultatif |
| Inscription | `/inscription` | Choix de l’activité, du créneau, du niveau, des attentes, présentations et conditions |
| Confirmation | `/confirmation/{reference}` | Résultat de l’inscription et récapitulatif des valeurs enregistrées |

Parcours normal : **catalogue → création du compte → inscription → confirmation**.

Après création du compte, le site conserve une session locale et ouvre le formulaire d’inscription. Le compte est alors déjà créé, même si Alex abandonne ensuite l’inscription. L’assistant devra expliquer ces deux engagements séparément.

L’accès direct au formulaire sans session renvoie vers la création du compte. La confirmation est accessible uniquement dans la session correspondante. La connexion à un compte existant, la récupération du mot de passe et la modification d’une inscription terminée sont hors du parcours de cette version.

Un accès « Retour aux ateliers » reste disponible sur les pages de saisie. Il conserve les réponses pendant la session. Une réinitialisation réservée à l’équipe de démonstration permettra ultérieurement de retrouver l’état initial.

## 3. Contenus du site

### Page « Les ateliers »

**Bandeau commun :** « Site fictif — démonstration du hackathon. Utilisez uniquement des données fictives. »

**Titre :** « Les ateliers du quartier »

**Sous-titre :** « Programme d’activités et modalités d’inscription — automne 2026 »

**Texte principal à afficher :**

> L’association Les ateliers du quartier propose un programme d’initiation et de pratique collective à destination des adultes. L’accès aux séances s’effectue après ouverture d’un espace personnel et transmission d’une demande d’inscription mentionnant l’activité sollicitée, la session retenue et les attentes du participant. La création de l’espace personnel ne vaut pas inscription à une activité. Chaque demande porte sur un atelier et un créneau ; son enregistrement est confirmé à l’issue de la procédure.
>
> Les séances ne donnent lieu à aucun paiement et le matériel nécessaire est mis à disposition sur place. Elles se déroulent à la Maison des ateliers — Bordeaux, lieu fictif. Pour permettre aux animateurs de préparer l’accueil, le formulaire sollicite un positionnement expérientiel, une expression de la finalité participative ainsi qu’une sélection des attentes associées à la participation. Une à trois attentes doivent être renseignées.
>
> Les séances de photographie avec échanges internationaux accueillent des participants francophones et anglophones. Une présentation succincte en français et sa version anglaise sont demandées pour cette activité. L’anglais n’est pas un prérequis pour participer : une aide à la traduction est autorisée. Pour les autres activités, seule la présentation française est nécessaire.
>
> Les personnes déjà adhérentes à l’association peuvent reporter le code à six chiffres figurant sur leur carte. Ce renseignement est facultatif et son absence ne fait pas obstacle à la création du compte. Les modalités relatives au compte, aux limites de saisie et à la participation sont précisées dans les formulaires suivants.

**Bouton principal :** « Constituer mon dossier » → création du compte.

### Catalogue exact

| Activité | Description | Créneaux disponibles |
| --- | --- | --- |
| Peinture | Découvrir la peinture et réaliser une création personnelle. Tous niveaux. | 3 octobre 2026, 10 h–12 h ; 10 octobre 2026, 10 h–12 h |
| Poterie | Découvrir le modelage et fabriquer un petit objet. Tous niveaux. | 7 octobre 2026, 14 h–16 h ; 14 octobre 2026, 14 h–16 h |
| Photographie avec échanges internationaux | Découvrir la photographie et échanger avec des participants francophones et anglophones. Tous niveaux. | 10 octobre 2026, 14 h–16 h ; 17 octobre 2026, 14 h–16 h |

Ces dates constituent les données fixes de la démonstration. Il n’y a ni jauge de places ni fermeture automatique des inscriptions. L’équipe pourra donc rejouer le parcours après les dates affichées.

### Page « Création du compte »

**Titre :** « Ouverture de l’espace adhérent »

**Introduction :** « Renseignez les éléments d’identification du titulaire. Les champs marqués d’un astérisque sont requis. Le code d’adhérent est facultatif. L’ouverture de cet espace précède la sélection d’une activité et ne constitue pas une inscription à un atelier. »

**Bloc de consignes, séparé des champs :** « L’adresse électronique doit comporter un @ et un domaine avec une extension. Le secret d’authentification doit comporter au moins 12 caractères. Sa confirmation doit être identique. La date de naissance est attendue au format JJ/MM/AAAA. Le code d’adhérent, lorsqu’il est fourni, comporte exactement six chiffres. »

**Bouton d’envoi :** « Valider ».

### Page « Inscription »

**Titre :** « Demande de participation à une session »

**Introduction :** « Votre espace personnel est créé. Procédez à la sélection d’une activité et d’une session. Un seul choix est attendu pour l’activité, le créneau et le positionnement expérientiel. Sélectionnez entre une et trois attentes. »

**Bloc explicatif :** « Le positionnement expérientiel correspond à votre expérience dans l’activité choisie. La finalité participative désigne les raisons pour lesquelles vous souhaitez participer : ce que vous voulez découvrir, apprendre ou partager. La présentation française et, le cas échéant, sa version anglaise sont limitées chacune à 200 caractères, espaces compris. »

**Consignes conditionnelles pour la photographie :** « Pour cette activité, reportez également votre présentation en anglais. Une traduction assistée est autorisée. L’absence de maîtrise de l’anglais ne constitue pas un motif d’exclusion. »

**Conditions de participation :** « Je confirme le choix de mon atelier et de mon créneau. Je comprends que l’activité est gratuite, que le matériel est fourni et que l’inscription concerne uniquement cette séance. »

**Bouton d’envoi :** « Valider ».

### Page « Confirmation »

**Titre :** « Inscription enregistrée »

**Texte :** « Votre inscription a bien été enregistrée. Retrouvez ci-dessous les informations de votre séance. Aucun paiement n’est demandé. »

Afficher la référence réelle attribuée par le site, le prénom et le nom, le courriel, l’activité, le créneau, le lieu, le niveau, les attentes, la présentation française et la présentation anglaise lorsqu’elle est requise. Les attentes sont présentées dans l’ordre du formulaire.

La date de naissance, le mot de passe et le code d’adhérent ne sont pas affichés sur cette page. Aucun courriel de confirmation n’est envoyé : la preuve de réussite est le résultat affiché et enregistré localement.

## 4. Champs et règles de validation

Les identifiants ci-dessous sont les identifiants techniques des contrôles HTML. Ils permettront de relier une réponse au bon champ et d’écrire les tests. Les règles utiles sont présentes dans le contenu, les attributs des champs ou les messages du site, afin d’être observables par Playwright.

### Création du compte

| Identifiant | Libellé du site | Contrôle | Obligatoire | Règle |
| --- | --- | --- | --- | --- |
| `first_name` | Prénom du titulaire | Texte | Oui | Non vide après retrait des espaces extérieurs ; 80 caractères maximum ; accents, espaces et traits d’union admis |
| `last_name` | Nom du titulaire | Texte | Oui | Même règle que le prénom |
| `email` | Adresse électronique de correspondance | Courriel | Oui | Syntaxe valide, sans espace ; règle propre à la démo : domaine comportant au moins un point et une extension d’au moins deux lettres ; 254 caractères maximum |
| `password` | Secret d’authentification | Mot de passe masqué | Oui | De 12 à 128 caractères ; collage autorisé ; aucune modification automatique |
| `password_confirmation` | Réitération du secret | Mot de passe masqué | Oui | Identique au mot de passe |
| `birth_date` | Date de naissance | Texte | Oui | Date réelle au format JJ/MM/AAAA ; non future ; titulaire âgé d’au moins 18 ans |
| `member_code` | Référence d’adhésion antérieure | Texte avec clavier numérique suggéré | Non | Vide ou exactement six chiffres ASCII de 0 à 9 ; conserver les zéros initiaux |

La règle de domaine du courriel appartient au site fictif. Elle ne constitue pas une définition universelle des adresses valides. Les terminaisons `.fr`, `.org`, `.com` et `.test` sont notamment admises. Aucune vérification de l’existence de la boîte ni aucun envoi ne sont effectués.

Pour comparer les comptes existants, la démo retire les espaces extérieurs et compare les courriels sans distinction de casse. Un doublon bloque la création sans créer un deuxième compte. Ce cas constitue une erreur à expliquer ; il n’ouvre pas un parcours de connexion supplémentaire.

Les noms et le courriel peuvent perdre leurs espaces extérieurs au moment de la validation. Les mots de passe restent strictement inchangés. Le code d’adhérent est vérifié tel que saisi : aucune suppression de lettres ou remplacement de `O` par `0`.

L’âge est calculé par rapport à la date locale du site, en Europe/Paris. Pour une naissance le 29 février, l’anniversaire est fixé au 1er mars les années non bissextiles dans cette démo. Le code d’adhérent est seulement contrôlé sur son format ; aucune vérification contre un fichier d’adhérents n’est prévue.

### Inscription à l’atelier

| Identifiant | Libellé du site | Contrôle | Obligatoire | Règle |
| --- | --- | --- | --- | --- |
| `activity` | Activité sollicitée | Liste à choix simple | Oui | Une activité parmi les trois du catalogue ; aucun choix présélectionné |
| `slot` | Session de rattachement | Liste à choix simple | Oui | Un des deux créneaux de l’activité sélectionnée ; indisponible avant le choix de l’activité |
| `experience` | Positionnement expérientiel | Liste à choix simple | Oui | Une valeur : « Aucune pratique », « Pratique occasionnelle », « Pratique régulière » |
| `expectations` | Attentes associées à la participation | Groupe de cases à cocher | Oui | De une à trois valeurs parmi les six options ci-dessous ; aucune présélection |
| `presentation_fr` | Finalité participative — version française | Zone de texte | Oui | Texte non vide ; 200 caractères maximum ; contenu décrivant les raisons de participer |
| `presentation_en` | Finalité participative — version anglaise | Zone de texte conditionnelle | Pour la photographie | Texte non vide ; 200 caractères maximum ; traduction de la présentation française |
| `terms_accepted` | Acceptation des conditions de participation | Case indépendante | Oui | Doit être cochée explicitement |
| `newsletter` | Réception des actualités associatives | Case indépendante | Non | Décochée initialement ; son refus ne bloque pas l’inscription |

Options exactes du choix multiple :

1. Découvrir une activité.
2. Apprendre une technique.
3. Rencontrer des personnes.
4. Créer quelque chose.
5. Partager mon expérience.
6. Pratiquer une langue.

Les listes simples comportent une entrée initiale « Sélectionner » qui ne constitue pas une réponse. Une sélection remplace la précédente. Les cases multiples permettent d’ajouter et de retirer chaque choix séparément.

### Règles dépendant des réponses

- Changer d’activité efface le créneau précédent et charge les créneaux de la nouvelle activité.
- Le choix photographie affiche le champ anglais et le rend obligatoire. Pour peinture ou poterie, ce champ est masqué et n’est pas soumis au serveur.
- Un brouillon anglais peut être conservé pendant la session, mais doit être revérifié si l’utilisateur revient à la photographie. L’assistant devra invalider une ancienne traduction lorsque le texte français change.
- Le changement d’activité conserve le niveau, les attentes et la présentation française. Le récapitulatif de l’assistant permettra à l’utilisateur de les revoir avant de confirmer.
- Le site contrôle le nombre d’attentes : zéro ou quatre choix produisent une erreur. L’assistant expliquera cette limite avant la sélection.
- Une inscription comporte une seule activité et un seul créneau. Un compte ne peut pas avoir deux inscriptions pour la même activité dans la démo.
- Les contrôles de langue et de fidélité des textes ne sont pas confiés au serveur du site fictif. Celui-ci contrôle présence et longueur ; la traduction et sa vérification qualitative appartiennent à l’assistant et à la revue du scénario.

## 5. Erreurs affichées par le site source

Le site affiche les erreurs en haut du formulaire dans un bloc compact intitulé « Anomalies de saisie ». Il conserve les réponses autres que les mots de passe. En cas d’échec de création du compte, les deux champs de mot de passe sont vidés et doivent être renseignés à nouveau.

Les erreurs sont listées dans l’ordre des champs. Les validations du serveur produisent ce bloc pour que les scénarios soient reproductibles. Les attributs HTML décrivent également les contraintes, mais les messages natifs du navigateur ne remplacent pas le bloc du site.

| Situation | Message exact du site source |
| --- | --- |
| Champ obligatoire vide | `E100 — Valeur requise : {libellé}.` |
| Courriel non conforme | `E101 — Adresse électronique non conforme au format attendu.` |
| Courriel déjà associé à un compte | `E102 — Identifiant électronique déjà affecté.` |
| Mot de passe hors limites | `E103 — Secret d’authentification : longueur attendue de 12 à 128 caractères.` |
| Confirmation différente | `E104 — Discordance des secrets d’authentification.` |
| Date impossible ou mauvais format | `E105 — Date non conforme. Format attendu : JJ/MM/AAAA.` |
| Date future | `E106 — Date de naissance postérieure à la date courante.` |
| Titulaire mineur | `E107 — Condition de majorité non satisfaite.` |
| Code d’adhérent incorrect | `E108 — Référence attendue : six caractères numériques.` |
| Valeur de liste non autorisée | `E109 — Sélection non reconnue : {libellé}.` |
| Créneau incompatible avec l’activité | `E110 — Incompatibilité activité/session.` |
| Nombre d’attentes incorrect | `E111 — Cardinalité des attentes non conforme : de 1 à 3 valeurs.` |
| Texte trop long | `E112 — Longueur maximale dépassée : {libellé}, {limite} caractères.` |
| Conditions non acceptées | `E113 — Acceptation des conditions requise.` |
| Inscription déjà existante | `E114 — Participation déjà enregistrée pour cette activité.` |

Un échec de validation ne crée aucun compte ou inscription partiel. La création du compte et l’inscription sont toutefois deux opérations distinctes : un compte créé reste présent si la demande d’inscription échoue ensuite.

## 6. Difficultés d’accessibilité intentionnelles

Le site doit sembler plausible, avec une présentation associative administrative. Les difficultés ciblées doivent être visibles et explicables au jury.

| Difficulté prévue | Manifestation sur le site | Effet à montrer |
| --- | --- | --- |
| Texte dense | Longs paragraphes sur le catalogue, conditions mêlées aux modalités | Alex peine à identifier le prix, le matériel et les étapes |
| Vocabulaire abstrait | « Constituer mon dossier », « Finalité participative », « Positionnement expérientiel » | Alex doit faire expliquer le sens d’une action ou d’un champ |
| Consignes éloignées | Formats et longueurs regroupés dans un bloc au-dessus du formulaire | Alex doit mémoriser puis retrouver la règle |
| Présentation chargée | Formulaires en deux colonnes sur grand écran ; champs d’une page affichés ensemble | Alex a du mal à choisir par où commencer |
| Hiérarchie faible | Instructions secondaires en petit texte gris ; informations importantes noyées dans le paragraphe | Les conditions utiles sont difficiles à repérer |
| Erreurs techniques | Bloc global avec codes, sans explication de correction ni lien vers le champ | Alex comprend difficilement comment reprendre |
| Progression peu visible | Absence d’indicateur d’étape ; bouton « Valider » sur les deux formulaires | La différence entre création de compte et inscription est difficile à suivre |
| Choix multiples peu accompagnés | Six cases visibles ; limite donnée seulement dans le bloc de consignes | Alex peut sélectionner trop d’options |

Les contrôles restent des éléments HTML natifs avec des libellés reliés aux champs. Les boutons sont utilisables au clavier. Ces bases rendent le site fonctionnel et observable ; les obstacles de la démonstration portent d’abord sur la compréhension et l’organisation de la saisie.

Les explications de référence présentes dans cette fiche ne seront pas injectées secrètement dans la page pour l’agent. L’assistant devra s’appuyer sur le contenu effectivement affiché et les contraintes observées.

## 7. Les cas d’usage à démontrer

| Cas | Saisie ou action d’Alex | Réaction attendue de l’assistant |
| --- | --- | --- |
| Courriel sans `@` | `alex.martinexample.test` | Signaler le symbole manquant et demander l’adresse exacte ; aucune correction inventée |
| Domaine incomplet selon le site | `alex.martin@example` | Demander de vérifier la fin de l’adresse ; aucune hypothèse automatique sur `.com` |
| Texte trop long | Réponse dépassant 200 caractères | Conserver le texte intégral dans l’aide, proposer un raccourcissement, recompter et faire accepter la proposition |
| Lettre dans un identifiant | `00A123` | Expliquer que le code attend six chiffres et demander la correction ; préserver `001234` si Alex le fournit |
| Traduction | Présentation française acceptée, atelier photographie choisi | Proposer une traduction anglaise fidèle, afficher les deux versions et attendre l’acceptation |
| Date de naissance | `31/02/2001`, ou une date sans année | Expliquer l’erreur ou demander l’année ; proposer jour, mois et année séparés |
| Intitulé obscur | « Que veut dire finalité participative ? » | Expliquer : « Pourquoi veux-tu participer à cet atelier ? », en s’appuyant sur le bloc explicatif du site |
| Choix simple | Alex souhaite « Peinture », puis choisit « Photographie » | Remplacer le choix précédent et redemander un créneau compatible |
| Choix multiples | Alex souhaite quatre attentes | Expliquer la limite de trois et lui demander lesquelles conserver ; ne pas choisir à sa place |

Exemple de réponse longue pour le scénario de raccourcissement (287 caractères) :

> Je souhaite participer à cet atelier parce que j’aime prendre des photos pendant mes promenades dans Bordeaux. J’aimerais apprendre à mieux utiliser mon appareil, découvrir comment cadrer une image et rencontrer d’autres personnes pour partager cette activité dans une ambiance agréable.

Exemple de reformulation acceptable, à titre de référence pour la revue (138 caractères) :

> J’aime prendre des photos à Bordeaux. Je veux apprendre à utiliser mon appareil, mieux cadrer mes images et rencontrer d’autres personnes.

Le modèle n’a pas à reproduire ce texte mot pour mot. Il doit respecter la limite et les intentions exprimées. Aucune compétence, expérience ou préférence supplémentaire ne doit être inventée.

L’interface d’aide devra permettre une saisie dépassant 200 caractères : une troncature immédiate empêcherait de démontrer le raccourcissement. Le champ du site source conserve sa limite de 200 caractères. Un test direct du serveur vérifiera également le rejet d’une valeur trop longue.

## 8. Jeu de données et parcours de référence

| Information | Valeur fictive |
| --- | --- |
| Prénom et nom | Alex Martin |
| Courriel | `alex.martin@example.test` |
| Mot de passe de démonstration | `AtelierDemo2026!` — exclusivement pour ce site fictif |
| Date de naissance | `14/03/2001` |
| Code d’adhérent facultatif | `001234` |
| Activité | Photographie avec échanges internationaux |
| Créneau | 10 octobre 2026, 14 h–16 h |
| Niveau | Aucune pratique |
| Attentes | Apprendre une technique ; Rencontrer des personnes |
| Présentation française | Réponse longue ci-dessus, puis proposition courte acceptée |
| Présentation anglaise | Traduction de la proposition française acceptée |
| Conditions | Acceptées explicitement |
| Actualités | Refusées |

Les données ne sont pas présaisies dans les formulaires : elles servent à jouer et tester le scénario. La démonstration principale peut montrer le courriel incorrect, le texte trop long, la traduction et les choix. Les autres erreurs se rejouent séparément pour garder une présentation courte.

## 9. Critères de validation du site avant de connecter l’IA

- Les quatre pages et tous les contenus décrits sont accessibles dans le parcours prévu.
- Un compte valide permet d’ouvrir le formulaire d’inscription dans la même session.
- Le parcours de référence aboutit à une inscription réelle en base et à un récapitulatif exact.
- Une adresse en `.fr` et l’adresse fictive en `.test` sont acceptées ; les deux exemples de courriel incorrect sont rejetés.
- Le code `001234` conserve ses zéros ; `00A123` est rejeté ; un code vide est accepté.
- Le site rejette une date impossible, une date future et une date correspondant à un mineur ; accepte une date bissextile valide respectant l’âge requis.
- Une liste simple ne soumet qu’une valeur. Changer d’activité réinitialise le créneau.
- Les attentes acceptent une, deux ou trois valeurs distinctes et rejettent zéro ou quatre valeurs.
- Le champ anglais est obligatoire pour la photographie et absent des données envoyées pour les autres activités.
- Les deux présentations acceptent exactement 200 caractères et rejettent un dépassement côté serveur. Le comptage inclut espaces et retours à la ligne, normalisés en `\n`, et utilise les unités UTF-16 comme `maxlength` dans le navigateur. Prévoir un essai avec un emoji pour vérifier la cohérence du comptage côté Python.
- Une erreur conserve les réponses autres que les mots de passe ; ces derniers sont vidés après un refus de création du compte.
- Refuser les actualités n’empêche pas de s’inscrire ; omettre l’acceptation des conditions bloque l’inscription.
- Un double envoi ne produit pas deux comptes ou deux inscriptions identiques. Un doublon ne provoque pas d’annonce de nouvelle réussite.
- La confirmation reflète les valeurs persistées et ne contient aucun mot de passe.
- La réinitialisation permet de rejouer le scénario avec le même courriel fictif.

**Périmètre de cette étape :** cette fiche et son référencement dans le dépôt. Le code du site, l’accès AWS et l’interface Streamlit seront réalisés dans les étapes suivantes.
