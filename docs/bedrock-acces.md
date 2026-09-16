# Étape 3 — Valider l’accès à Bedrock

Le test est indépendant du site fictif. Il utilise Boto3, le SDK Python d’AWS, dans un conteneur Docker dédié. Cela permet d’isoler les éventuels problèmes de clé, de région et de droits avant de brancher LangChain.

## Résultat du test réel — 16 septembre 2026

**Accès validé** depuis le conteneur Docker avec la clé API fournie par l’équipe.

| Mesure | Résultat |
| --- | --- |
| Région | `eu-west-1` |
| Modèle | `eu.amazon.nova-2-lite-v1:0` |
| API | Converse via Boto3 |
| Durée observée pour cet appel | 1,16 seconde |
| Tokens d’entrée / sortie | 67 / 39 |
| Fin de génération | `end_turn` |

La réponse contient notamment « Cet atelier est gratuit. ». Le modèle a aussi ajouté un préambule, une autre reformulation et du Markdown malgré la demande d’une seule phrase. L’accès technique fonctionne ; la maîtrise du format et la qualité de simplification restent à évaluer lors de l’intégration de l’assistant. Cette mesure unique n’est pas un benchmark de latence. La clé n’est pas conservée dans ce compte rendu.

## Configuration locale

Le mode d’accès retenu est la **clé API Bedrock**, fournie par l’organisateur. Ce n’est pas une paire AWS Access Key / Secret Key. Boto3 reconnaît la variable `AWS_BEARER_TOKEN_BEDROCK` : [documentation AWS](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys-use.html).

Copier `.env.bedrock.example` vers `.env.bedrock` si ce dernier n’existe pas, puis remplir ce fichier dans un éditeur :

```dotenv
AWS_REGION=region-fournie-par-organisateur
AWS_BEARER_TOKEN_BEDROCK=cle-fournie-par-organisateur
BEDROCK_MODEL_ID=eu.amazon.nova-2-lite-v1:0
```

Ne pas mettre de guillemets autour des valeurs. Le fichier `.env.bedrock` est exclu de Git et du contexte de construction Docker. La clé ne doit pas être collée dans une conversation ni dans une commande qui la conserverait dans l’historique.

Le modèle par défaut, Nova 2 Lite, figure dans la liste fournie par l’équipe et prend en charge Converse. Ce choix permet un premier test textuel simple ; ce n’est pas encore une comparaison de qualité entre modèles. Le préfixe `eu.` désigne un profil d’inférence européen ; la région de l’appel doit être confirmée séparément avec l’organisateur. [Fiche AWS du modèle](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-2-lite.html).

## Exécution

Depuis la racine du dépôt :

```powershell
docker build -f Dockerfile.bedrock -t aubay-bedrock-check .
docker run --rm --env-file .env.bedrock aubay-bedrock-check --check-only
```

`--check-only` contrôle la présence de la configuration sans contacter AWS. Il ne prouve pas la validité de la clé.

Pour effectuer le test réel :

```powershell
docker run --rm --env-file .env.bedrock aubay-bedrock-check
```

Le script effectue un seul appel à l’API **Converse**, sans nouvelle tentative automatique, avec une sortie limitée à 64 tokens. Cet appel peut être facturé selon les conditions du compte du hackathon. Le texte envoyé est fictif : « Réécris en français simple, en une phrase : La participation à cet atelier ne nécessite aucun paiement. »

Le résultat affiche le modèle, la région, la réponse, la durée et le nombre de tokens lorsque l’API les fournit. Aucune donnée du formulaire ni aucun document du hackathon n’est envoyé. La clé sert uniquement à authentifier la requête HTTPS auprès d’AWS.

## Lire le résultat

| Statut | Signification / prochaine action |
| --- | --- |
| `configuration_incomplete` | Compléter les variables indiquées dans le fichier local. |
| `configuration_presente` | Contrôle local réussi ; appel réel encore nécessaire. |
| `acces_valide` | Le modèle a répondu par du texte : l’accès à ce modèle dans cette région fonctionne. |
| `appel_refuse` | Consulter le code et l’indication affichés : droits, clé expirée, modèle/région ou quota. |
| `connexion_impossible` | Vérifier le réseau, le proxy éventuel et la configuration. |
| `reponse_sans_texte` | AWS a répondu, mais le test de génération de texte n’est pas validé. |

Un succès ne valide ni tous les modèles de la liste, ni la qualité de simplification, ni l’utilisation d’outils par l’agent. Ces contrôles viendront avec LangChain et les scénarios de l’assistant.

Le diagnostic n’affiche pas les messages bruts d’erreur AWS, les en-têtes ou la clé. En cas de refus, transmettre seulement le code d’erreur, le modèle et la région à l’organisateur. La commande ne modifie aucun droit AWS.

## Chemin de l’appel

```text
.env.bedrock → environnement du conteneur → Boto3
            → requête HTTPS Converse → Amazon Bedrock → réponse texte
```

Boto3 se charge de la communication JSON et de l’authentification. LangChain pourra ensuite utiliser ce même service Bedrock pour organiser les messages et les appels d’outils. [Exemples AWS de Converse avec Nova](https://docs.aws.amazon.com/nova/latest/nova2-userguide/using-converse-api.html).
