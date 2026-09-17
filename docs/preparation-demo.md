# Préparer une démonstration fiable

## La veille ou après la dernière modification

Depuis la racine du projet, avec Docker Desktop ouvert :

```powershell
.\scripts\prepare-demo.cmd --build --full
```

Le contrôle s’arrête en erreur si un service ou l’analyse IA ne fonctionne pas. Il attend les contrôles de santé Docker, teste la lecture Playwright et les appels d’outils Bedrock, puis joue le parcours complet dans un navigateur. Cette répétition crée des données fictives avec une adresse unique, contrôle les preuves dans le site source et produit captures et vidéos. Aucun secret n’est affiché.

Les dépendances Python restent épinglées dans les fichiers `requirements*.txt`. Conserver les images Docker qui viennent de réussir ; ne pas actualiser les dépendances, changer de modèle ou reconstruire juste avant de parler. Le code a déjà une limite d’appels, des envois soumis à accord et une récupération en lecture seule pour éviter les doublons. Une validation réussie ne garantit pas la disponibilité future du réseau ou de Bedrock.

Ouvrir et vérifier les deux vidéos de secours : `output/demo-secours/aide-parcours-reel.webm` et `site-preuves-reelles.webm`. Elles sont issues du test automatisé, sans narration ; elles ne remplacent pas une répétition orale. Pour un secours plus fluide, enregistrer aussi une répétition manuelle de cinq minutes avec les commentaires du présentateur.

## Quinze minutes avant

```powershell
.\scripts\prepare-demo.cmd
```

Ce contrôle ne crée aucun compte ni réservation. Il vérifie l’accès réel au modèle et la découverte des trois actions attendues. En cas d’échec : vérifier Docker, Internet, la clé Bedrock et le quota avec l’organisateur. Le diagnostic spécifique `scripts/check_bedrock.py` reste disponible via son Dockerfile dédié pour obtenir le code de refus AWS sans révéler la clé.

Brancher le portable, couper la veille et les notifications, vérifier le réseau dans la salle et disposer d’une connexion de secours si possible. Fermer les onglets superflus. Préparer deux adresses fictives distinctes, par exemple `alex.demo17a@example.test` et `alex.demo17b@example.test`, avec `AtelierDemo2026!` comme mot de passe fictif. Ne pas réutiliser une adresse déjà créée pendant une répétition.

Sur `http://127.0.0.1:8000/`, se déconnecter du compte précédent. Garder le même navigateur, profil et adresse hôte pendant la démo. Partir du catalogue, montrer le formulaire difficile, puis ouvrir l’aide exclusivement avec « M’aider avec ce site ». Le ticket de liaison est valable deux minutes : ne pas préparer un lien Streamlit avec ticket à l’avance. Ne pas recharger Streamlit pendant une saisie.

## Pendant les cinq minutes

Suivre [le déroulé](demo-cinq-minutes.md). Une seule erreur volontaire : l’e-mail sans `@`. Les changements d’activité, la reconnexion et les autres refus serveur restent pour les questions. Après la création, montrer le compte sur le site. Après réservation, montrer la même référence dans les deux interfaces. Actualiser le site si nécessaire.

Pendant l’attente IA, expliquer une seule fois : « L’agent lit le site, choisit ses outils et vérifie le résultat. Il attend mon accord pour envoyer. » Garder environ trente secondes de marge. Ne pas cliquer plusieurs fois ni lancer plusieurs démonstrations en parallèle sur la même session.

## Si quelque chose bloque

| Situation | Action |
| --- | --- |
| Adresse déjà utilisée | Utiliser l’adresse de secours ou se connecter au compte existant. |
| Anciennes réservations visibles | Vérifier l’identité affichée sur le site ; se déconnecter puis relancer l’aide pour un nouveau compte. |
| Lien de liaison expiré, onglet fermé ou Streamlit rechargé | Revenir au site et cliquer à nouveau sur « M’aider avec ce site ». Si le compte a déjà été créé, le retrouver plutôt que tenter de le recréer. |
| Analyse IA bloquée | Une seule reprise avec « Reprendre l’analyse » ou « Relire le site ». Si elle échoue encore, passer au secours. |
| Envoi au résultat incertain | Utiliser « Vérifier auprès du site ». Ne pas envoyer une seconde fois. Vérifier la liste des réservations. |
| Internet ou Bedrock indisponible | Annoncer explicitement que la suite montrée est un enregistrement du parcours réel testé. Montrer la vidéo ou les captures, puis expliquer l’architecture. |

Ne pas effacer la base, reconstruire les images ou modifier une clé à l’écran pendant l’oral. Les comptes existants et leurs preuves restent disponibles même si l’IA est momentanément indisponible.

## Ce qu’on peut affirmer au jury

Le modèle choisit des outils à partir d’observations réelles et reçoit leurs résultats. Les contrôles simples, le stockage des réponses et l’autorisation d’envoi sont programmés. La session partagée et la lecture des preuves sont adaptées à ce site contrôlé. Le prototype ne constitue ni un audit RGAA complet ni une preuve de prise en charge de n’importe quel site. Une évaluation avec les utilisateurs concernés reste nécessaire.
