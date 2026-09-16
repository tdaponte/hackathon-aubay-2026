# hackathon-aubay-2026

Prototype d’assistant d’accessibilité cognitive : comprendre un site et être accompagné dans la création d’un compte puis l’inscription à un atelier.

## Cadrage du site fictif

La [fiche du site « Les ateliers du quartier »](docs/site-fictif-specification.md) décrit les pages, les textes, les formulaires, leurs règles et les difficultés d’accessibilité prévues pour la démonstration.

Le site fictif est implémenté : catalogue, création de compte, inscription à un atelier et confirmation enregistrée en base. L’assistant IA et son interface Streamlit constituent la prochaine étape.

L’[étape de validation de l’accès à Bedrock](docs/bedrock-acces.md) dispose d’un test Docker indépendant du site, à configurer avec la clé API et la région fournies par l’organisateur.

## Voir le site avec Docker

Prérequis : Docker Desktop démarré, avec les conteneurs Linux. Depuis la racine du dépôt :

```powershell
docker compose up -d --build
```

Ouvrir **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** dans le navigateur. Le premier lancement télécharge Python et les dépendances ; les suivants utilisent le cache. Aucun accès AWS n’est nécessaire pour cette étape.

Le site écoute uniquement sur ce poste. Docker fournit l’environnement Python : il n’est pas nécessaire d’installer Python sur Windows pour cette méthode.

Pour arrêter le site en conservant les données :

```powershell
docker compose down
```

Pour supprimer les comptes, inscriptions et sessions fictifs et rejouer la démonstration :

```powershell
docker compose exec site python -m ateliers reset --yes
```

Recharger ensuite la page du navigateur. Les données se trouvent dans `data/ateliers.sqlite3`, exclu de Git. La remise à zéro se fait par cette commande, sans bouton public sur le site.

## Jouer le parcours

Cliquer sur **Constituer mon dossier**, puis utiliser ces données fictives :

| Champ | Valeur de démonstration |
| --- | --- |
| Prénom / nom | Alex / Martin |
| Adresse électronique | `alex.martin@example.test` |
| Secret d’authentification et réitération | `AtelierDemo2026!` |
| Date de naissance | `14/03/2001` |
| Référence d’adhésion antérieure, facultative | `001234` |

Après la création du compte, choisir **Photographie avec échanges internationaux**, le créneau du **10 octobre 2026, 14 h–16 h**, puis **Aucune pratique**. Cocher **Apprendre une technique** et **Rencontrer des personnes**.

- Présentation française : `Je souhaite apprendre la photographie et rencontrer des personnes.`
- Présentation anglaise : `I want to learn photography and meet people.`
- Accepter les conditions de participation fictives ; laisser les actualités décochées.

Le bouton **Valider** enregistre l’inscription et affiche sa référence. L’atelier photographie permet de montrer le besoin de traduction ; les autres ateliers ne demandent pas de texte anglais.

Pour provoquer des erreurs, essayer un courriel sans `@` ou sans extension, la date `31/02/2001`, le code `00A123`, ou quatre attentes cochées. Les messages techniques et les intitulés complexes sont intentionnels. Les zones de présentation limitent la saisie à 200 caractères ; le serveur contrôle aussi cette limite. Le futur assistant pourra recevoir une réponse plus longue et proposer de la raccourcir avant de remplir le site.

Les brouillons sont conservés dans le même onglet lors d’un retour au catalogue. Les mots de passe ne font pas partie du brouillon et sont vidés après une erreur. La session dure 24 heures ; ce prototype ne comprend pas encore de page de reconnexion. Pour rejouer avec le même courriel, utiliser la remise à zéro.

## Organisation et technologies

```text
ateliers/
  app.py           Routes HTTP et parcours des quatre pages
  content.py       Textes, ateliers, créneaux et options du catalogue
  validation.py    Règles de saisie et codes d’erreur
  database.py      Comptes, sessions et inscriptions SQLite
  templates/       Pages HTML rendues avec Jinja2
  static/          CSS, JavaScript et favicon locaux
tests/             Tests des validations, du parcours et de la persistance
scripts/           Parcours Playwright et captures d’écran
docs/              Spécification approuvée
```

**FastAPI** reçoit les formulaires et applique les règles côté serveur. **Jinja2** produit le HTML visible dans le navigateur. **SQLite** conserve les inscriptions dans un fichier, sans serveur de base de données supplémentaire. **JavaScript** adapte les créneaux à l’atelier choisi, affiche le champ anglais et conserve les brouillons. **Uvicorn** fait fonctionner le serveur Python.

FastAPI est un choix pratique pour garder le projet en Python ; le besoin ne l’impose pas. Les formulaires envoient des données HTTP classiques, et le serveur renvoie du HTML. Le catalogue intégré à la page et les brouillons utilisent du JSON : c’est un format de données utile, compatible avec la future communication entre composants.

Le site reste volontairement difficile à comprendre : textes denses, vocabulaire administratif, consignes éloignées, erreurs globales et bouton générique. Il conserve des contrôles HTML natifs et des labels associés aux champs. Il ne constitue pas une interface d’assistance cognitive validée auprès d’utilisateurs.

Les mots de passe fictifs sont hachés avec scrypt. Les confirmations sont limitées à la session du compte. Il n’y a ni paiement, ni envoi de courriel, ni appel à un modèle IA dans ce site local.

## Vérifications reproductibles

Construire l’image de test, puis lancer les tests Python :

```powershell
docker build --target tests -t aubay-ateliers-tests .
docker run --rm aubay-ateliers-tests
```

Le parcours navigateur utilise une base temporaire indépendante de la démo. Cette commande PowerShell monte le dépôt pour récupérer les captures dans `output/screenshots/` :

```powershell
$taskRepo = (Get-Location).Path
docker run --rm --mount "type=bind,source=$taskRepo,target=/app" aubay-ateliers-tests python scripts/browser_check.py
```

Les tests couvrent les cas de saisie, les dates, les doublons, les choix multiples, le champ anglais conditionnel, les limites de longueur, les sessions et l’enregistrement réel. Playwright vérifie aussi la conservation du brouillon, le parcours jusqu’à la confirmation et l’absence de débordement sur les pages d’accueil et de création de compte à 390 et 320 pixels.

## Alternative avec Python installé

Avec un Python 3.12 ou plus récent déjà installé et autorisé sur le poste :

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m ateliers serve
```

Les fichiers `requirements.txt` et `requirements-dev.txt` fixent les versions utilisées. Pour le développement sans Docker, installer `requirements-dev.txt`, puis exécuter `python -m playwright install chromium` dans cet environnement avant le parcours navigateur.
