"""Un appel Converse sur un texte fictif. Ne journalise jamais la clé API."""
import argparse
import json
import os
import re
import time

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


ERROR_HINTS = {
    "AccessDeniedException": "Vérifier avec l'organisateur les droits de la clé sur ce modèle et son profil d'inférence, notamment InvokeModel et CallWithBearerToken.",
    "ExpiredTokenException": "La clé ou le jeton a expiré : obtenir une clé renouvelée.",
    "InvalidClientTokenId": "La clé n'est pas reconnue : vérifier sa copie et sa validité.",
    "UnrecognizedClientException": "La clé n'est pas reconnue : vérifier sa copie et sa validité.",
    "ValidationException": "Vérifier le modèle, le profil d'inférence et la région communiqués par l'organisateur.",
    "ResourceNotFoundException": "Le modèle ou profil n'est pas trouvé dans cette région.",
    "ThrottlingException": "Quota atteint ou trop d'appels : réessayer plus tard ou vérifier le quota avec l'organisateur.",
    "ServiceUnavailableException": "Bedrock est temporairement indisponible : réessayer plus tard.",
}


def report(status, **details):
    print(json.dumps({"status": status, **details}, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Contrôler la présence de la configuration sans appeler AWS")
    args = parser.parse_args(argv)
    region = os.environ.get("AWS_REGION", "").strip()
    model = os.environ.get("BEDROCK_MODEL_ID", "eu.amazon.nova-2-lite-v1:0").strip()
    token = os.environ.get("AWS_BEARER_TOKEN_BEDROCK", "")
    missing = [name for name, value in [("AWS_REGION", region), ("AWS_BEARER_TOKEN_BEDROCK", token.strip()), ("BEDROCK_MODEL_ID", model)] if not value]
    if missing:
        report("configuration_incomplete", missing=missing, hint="Compléter .env.bedrock localement, sans partager la clé dans la conversation.")
        return 2
    if not re.fullmatch(r"[a-z]{2}(?:-[a-z0-9]+)+-\d+", region):
        report("configuration_invalide", hint="AWS_REGION doit contenir un code de région AWS, par exemple eu-west-3.")
        return 2
    if token != token.strip() or token.startswith(('\"', "'")):
        report("configuration_invalide", hint="Copier la clé sans guillemets ni espaces de début ou de fin.")
        return 2
    if args.check_only:
        report("configuration_presente", region=region, model=model, hint="Aucun appel AWS effectué. La validité de la clé et l'accès au modèle restent à tester.")
        return 0

    started = time.perf_counter()
    try:
        # Ignore endpoint overrides: credentials go only to the AWS endpoint
        # selected by the SDK for this region. Exactly one attempt, no retries.
        client = boto3.client("bedrock-runtime", region_name=region, config=Config(
            connect_timeout=10, read_timeout=45,
            retries={"mode": "standard", "total_max_attempts": 1},
            ignore_configured_endpoint_urls=True,
        ))
        response = client.converse(
            modelId=model,
            messages=[{"role": "user", "content": [{"text": "Réécris en français simple, en une phrase : La participation à cet atelier ne nécessite aucun paiement."}]}],
            inferenceConfig={"maxTokens": 64},
        )
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code", "ClientError")
        # Do not print raw exceptions, headers, request payloads or credentials.
        report("appel_refuse", error=code, hint=ERROR_HINTS.get(code, "Faire vérifier la clé, la région et l'accès au modèle par l'organisateur."))
        return 3
    except BotoCoreError as error:
        report("connexion_impossible", error=type(error).__name__, hint="Vérifier le réseau, le proxy éventuel et la configuration locale. Aucun détail sensible n'est affiché.")
        return 4

    text = "\n".join(block["text"] for block in response.get("output", {}).get("message", {}).get("content", []) if "text" in block).strip()
    if not text:
        report("reponse_sans_texte", stop_reason=response.get("stopReason"), hint="L'API a répondu mais le test de génération de texte n'est pas validé.")
        return 5
    usage = response.get("usage", {})
    report("acces_valide", region=region, model=model, response=text,
           elapsed_seconds=round(time.perf_counter() - started, 2),
           input_tokens=usage.get("inputTokens"), output_tokens=usage.get("outputTokens"),
           stop_reason=response.get("stopReason"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
