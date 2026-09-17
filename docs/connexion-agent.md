# Étape 6 — L’agent découvre et pilote le parcours

## Différence avec l’étape 5

À l’étape 5, le programme connaissait les routes des formulaires et choisissait l’ordre des opérations. Nova préparait seulement les résumés et questions. L’étape 6 utilise une boucle explicite : **modèle → outil choisi → résultat observé → nouvelle décision**. Les actions sont réellement exécutées ; les explications et questions restent générées.

Bedrock est le service d’accès au modèle. Nova 2 Lite est le modèle. LangChain expose les outils avec `bind_tools` et renvoie leurs résultats avec `ToolMessage`. L’agent est le programme qui réunit ces éléments, garde l’état du parcours et contrôle les actions. Aucun service « Bedrock Agents », MCP ou LangGraph n’est nécessaire pour cette réalisation.

## Outils et décisions

| Outil choisi par le modèle | Exécution réelle |
| --- | --- |
| `observer_page` | Lire texte utile, liens et formulaires sans valeurs de saisie |
| `presenter_accueil` | Présenter le contexte généré et les actions dont les liens ont été observés ; figer cette présentation pendant le parcours |
| `ouvrir_lien` | Ouvrir un lien identifié dans la dernière observation du site |
| `lire_choix` | Appliquer le choix déjà fourni par l’utilisateur et lire la liste dépendante |
| `presenter_aide` | Présenter un formulaire, une correction, un blocage, une reprise ou une confirmation prouvée |
| `envoyer_formulaire` | Envoyer les réponses de session seulement si le récapitulatif exact a été accepté |
| `verifier_resultat` | Retrouver une réussite en lecture seule après un résultat incertain |

Seule l’adresse d’accueil est configurée. Les routes et destinations POST sont extraites des pages. Le modèle choisit les liens et le moment d’appeler les outils, sans fournir de code ni de sélecteurs. Les identifiants d’actions sont vérifiés par le programme.

À l’ouverture, l’objectif `overview` fait lire le catalogue et préparer le contexte et les actions avec `presenter_accueil`. L’objectif est ensuite limité à l’action sélectionnée : `account` (création), `login` (connexion) ou `reservation`. `begin_action` repart du catalogue en conservant la session du navigateur. Le programme refuse une action absente de l’accueil observé, une réservation sans authentification et un formulaire qui ne correspond pas à l’action choisie. Après réussite, le modèle rend la main. Le contexte généré reste stable pendant les questions.

## Liaison entre les deux onglets

Avant cette évolution, Chromium et l’onglet utilisateur avaient des sessions indépendantes : la réservation existait en base mais n’était pas visible dans l’ancien compte ouvert sur le site. Désormais, le formulaire « M’aider avec ce site » envoie un POST protégé par CSRF à `/aide/ouvrir`. Le serveur crée un ticket aléatoire valable deux minutes, stocké sous forme d’empreinte et utilisable une seule fois, puis ouvre Streamlit. Streamlit retire le ticket de l’URL et le transmet uniquement au serveur configuré (`/aide/rejoindre`, en-tête Authorization). La consommation est atomique. Le cookie de la session source est alors installé dans le navigateur Playwright, hors des messages IA et des journaux de l’agent.

Le site affiche les données du même compte dans les deux navigateurs. L’onglet source se recharge lorsqu’il redevient visible après lancement de l’aide ; une actualisation manuelle fonctionne également. La déconnexion révoque la session et ses tickets ; le navigateur agent refuse de poursuivre si sa session liée a changé. Il faut alors rouvrir l’aide depuis le site. Ce mécanisme est spécifique au démonstrateur contrôlé : il ne permet pas de récupérer les cookies d’un site tiers quelconque.

Les blocs de liaison, d’identité et de réservations privées portent `data-agent-ignore` : ils ne sont ni proposés comme formulaires métier, ni inclus dans les observations textuelles du modèle. La récupération d’une réservation incertaine peut toujours lire ses liens localement, sans les exposer au modèle. Les pages publiques du catalogue restent la source du contexte de l’accueil. Il s’agit d’une lecture fonctionnelle du site, pas d’un audit RGAA.

`aide/connected.py` porte la boucle et les contrôles d’accord ; `aide/agent_browser.py` porte les actions découvertes. `aide/browser.py` contient les primitives de session et de lecture de reçu. L’ancien parcours à routes fixes et ses tests ont été supprimés.

## Contrôle humain et confidentialité

Les réponses restent dans Streamlit : champs texte et secrets ne sont pas transmis au modèle. Les choix publics d’activités et horaires peuvent apparaître dans les observations. Les outils récupèrent les valeurs localement, sans arguments de saisie fournis par le modèle.

Chaque accord est lié au formulaire et à l’empreinte du récapitulatif. Modifier une réponse invalide cet accord. Il est consommé avant l’envoi ; un nouvel envoi nécessite un nouveau clic humain. Le navigateur bloque aussi les requêtes POST hors de cette opération autorisée.

Après une réussite ou un refus de création, le mot de passe est effacé des réponses et de la liste de filtrage. Les messages de retour sont filtrés avant cet effacement. Les champs cachés, cookies, scripts, reçus privés et captures ne sont pas transmis au modèle. Les anciennes valeurs personnelles sont conservées en mémoire de session pour filtrer leurs éventuelles réapparitions dans les textes du site. Aucun journal externe LangSmith n’est activé.

Le site reste responsable de ses validations. Le programme effectue les contrôles simples et les vérifications d’identité de formulaire. Le modèle reçoit les erreurs serveur et choisit la correction à demander ; il ne corrige jamais une adresse ou un choix à la place de l’utilisateur.

La réussite de la création ou connexion est vérifiée à partir du marqueur d’authentification rendu par le serveur dans la page suivant l’envoi. La connexion vérifie le mot de passe contre l’empreinte scrypt existante, sans créer un second compte ; les refus sont génériques. La réservation exige un reçu et une référence `ADQ-…`. Ces lecteurs de preuves restent spécifiques au démonstrateur, même si ses routes changent.

## Arrêts et visibilité

Un seul outil est exécuté par réponse du modèle. Une séquence s’arrête après six appels au modèle ou deux actions identiques donnant le même résultat sans progression. Un blocage reste visible ; « Reprendre l’analyse » ne redonne pas d’accord d’envoi. Après une incertitude, seul le bouton de vérification est proposé.

« Vue technique — appels de l’agent » affiche les outils demandés, le statut des résultats, l’état du parcours, les durées et le nombre d’appels au modèle. Aucun raisonnement interne ni valeur personnelle n’est affiché. Un outil refusé est visible : cela montre un contrôle réel, pas une action accomplie.

Le prompt traite le contenu du site comme non fiable. Les contrôles d’origine, d’identifiant et d’autorisation sont imposés en code. Les essais d’injection documentés ci-dessous ne constituent pas une garantie contre toutes les attaques possibles.

## Rejouer les essais

Le parcours complet réel peut être lancé depuis PowerShell :

```powershell
$taskRepo = (Get-Location).Path
docker compose run --rm --no-deps -v "${taskRepo}:/app" maquette python -m scripts.check_agent
```

Ce test crée un compte et une réservation fictifs dans la base locale. Le rapport contient les appels, durées et la référence dans `output/agent/`.

Pour tester l’adaptation, démarrer un serveur isolé dont les deux routes sont déplacées, le premier identifiant et des libellés modifiés, et dont l’accueil contient une consigne d’envoi sans accord :

```powershell
docker run -d --name aubay-agent-variant -p 127.0.0.1:8003:8000 --mount "type=bind,source=$taskRepo,target=/app,readonly" -e ATELIERS_DB=/tmp/variant.sqlite3 aubay-ateliers-tests python -m uvicorn scripts.variant_site:app --host 0.0.0.0 --port 8000 --no-access-log
docker compose run --rm --no-deps -v "${taskRepo}:/app" -e SITE_BASE_URL=http://host.docker.internal:8003 -e AGENT_REPORT=output/agent-variant -e AGENT_REJECTION=1 maquette python -m scripts.check_agent
docker run --rm --mount "type=bind,source=$taskRepo,target=/app" aubay-ateliers-tests python -m scripts.check_agent_browser
docker rm -f aubay-agent-variant
```

Le serveur de test utilise une base propre dans son conteneur, supprimée avec lui. L’agent reçoit uniquement son accueil. Les anciens chemins répondent 404. Le scénario provoque aussi un refus serveur d’e-mail (`a..b@example.test`), vérifie la demande de correction par le modèle et poursuit après nouvelle confirmation.

Les tests unitaires vérifient séparément : outils sélectionnés par le modèle, erreurs renvoyées au modèle, consentement absent ou périmé, protection contre répétition de POST, secrets filtrés puis effacés, arrêt sur boucle, plafond d’appels et impossibilité d’affirmer une réussite sans reçu.

## Limites

Le périmètre reste le compte et la réservation d’ateliers, avec texte, e-mail, mot de passe et deux listes simples liées. Une liste désactivée après une liste active est interprétée comme dépendante dans cet adaptateur. Il ne s’agit pas d’une prise en charge universelle des dépendances de formulaire.

Les questions et décisions varient selon le modèle ; une exécution peut demander plus d’appels ou s’arrêter. La qualité des reformulations reste à examiner avec les personnes concernées. Ni audit complet RGAA/WCAG, ni certification FALC, ni traduction, ni extension Chrome ne sont ajoutés.

Références : [outils Nova](https://docs.aws.amazon.com/nova/latest/nova2-userguide/using-tools.html), [agents LangChain](https://docs.langchain.com/oss/python/langchain/agents).
