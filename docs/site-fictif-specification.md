# Site fictif — version simplifiée de l’étape 4

Cette version remplace le parcours initial plus long. Le scénario est : **créer un compte, puis réserver un atelier gratuit**. Toutes les informations personnelles de la démonstration sont fictives.

## Pages et fonctions

| Page | Adresse | Fonction |
| --- | --- | --- |
| Catalogue | `/` | Peinture, poterie et photographie ; modalités dans des paragraphes denses |
| Compte | `/compte/creation` | Prénom, e-mail et mot de passe |
| Connexion | `/compte/connexion` | E-mail et mot de passe d’un compte existant |
| Réservation | `/inscription` | Une activité et un créneau compatible |
| Confirmation | `/confirmation/{reference}` | Référence persistée, prénom, e-mail, activité, créneau et lieu |

Créer un compte ne réserve aucune activité. La session ouvre ensuite le formulaire de réservation. La connexion permet de retrouver un compte existant sans le recréer ; le serveur vérifie l’empreinte scrypt et ouvre une session authentifiée. Sans connexion, la réservation redirige vers le formulaire de connexion. Un échec de réservation conserve le compte. La confirmation est accessible uniquement à une session du compte concerné.

## Champs et règles

| Identifiant HTML | Intitulé source | Règle |
| --- | --- | --- |
| `first_name` | Prénom du titulaire | Obligatoire, 80 caractères maximum après retrait des espaces extérieurs |
| `email` | Adresse électronique de correspondance | Obligatoire, syntaxe valide, 254 caractères maximum ; domaine avec point et extension alphabétique d’au moins deux lettres |
| `password` | Secret d’authentification | Obligatoire, 12 à 128 caractères ; masqué, collage autorisé, jamais corrigé automatiquement |
| `activity` | Activité sollicitée | Une des activités proposées, sans présélection |
| `slot` | Session de rattachement | Un créneau de l’activité choisie ; changer d’activité efface le créneau |

Le comptage utilise les unités UTF-16 comme les limites des champs HTML. Les e-mails sont comparés sans distinction de casse ; `.fr`, `.com`, `.org` et `.test` sont notamment acceptés. Aucun contrôle de réception d’e-mail n’est effectué.

Le serveur refuse un double compte pour le même e-mail et une seconde réservation de la même activité pour un compte. Il n’annonce pas une nouvelle réussite lors d’un doublon. Les mots de passe sont hachés avec scrypt. Une erreur conserve les valeurs ordinaires et vide le mot de passe.

## Catalogue

| Activité | Créneaux |
| --- | --- |
| Peinture | 3 ou 10 octobre 2026, 10 h–12 h |
| Poterie | 7 ou 14 octobre 2026, 14 h–16 h |
| Photographie | 10 ou 17 octobre 2026, 14 h–16 h |

Lieu : Maison des ateliers — Bordeaux, lieu fictif. Participation gratuite, matériel fourni, réservation d’une seule séance. Les dates sont fixes pour rejouer la démonstration ; il n’y a pas de gestion de jauge ni de fermeture automatique.

Les champs de date de naissance, nom de famille, code d’adhérent, confirmation de mot de passe, expérience, attentes, textes français/anglais et newsletter sont retirés. Il n’y a plus d’exigence d’âge ou de traduction dans les textes ni de case de conditions à cocher.

## Difficultés intentionnelles

Le site garde des textes denses, des intitulés administratifs, des consignes éloignées, une présentation en colonnes, le bouton générique « Valider » et un bloc d’erreurs techniques. Les contrôles HTML restent natifs avec des libellés associés.

Erreurs conservées : E100 (obligatoire), E101 (e-mail), E102 (e-mail existant), E103 (longueur du mot de passe), E109 (activité inconnue), E110 (créneau incompatible), E112 (prénom trop long), E114 (réservation déjà existante), E120 (connexion refusée, message identique pour compte inconnu et mot de passe incorrect). Les règles sont observables sur la page ou dans les attributs HTML ; aucun texte secret n’est fourni à un agent.

## Persistance et validation

Le nouveau schéma utilise `data/ateliers-v2.sqlite3`. L’ancien fichier est préservé, sans migration ni effacement. Les tables gardent uniquement les comptes simplifiés, les sessions et les réservations. La remise à zéro de la démonstration cible la nouvelle base par défaut.

La validation couvre les quatre pages, les champs nécessaires, les limites et erreurs, la compatibilité activité/créneau, les doublons, le hachage du mot de passe, la confidentialité de la confirmation et la réservation réellement persistée.
