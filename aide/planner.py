"""Bedrock interprète les observations ; aucune réponse utilisateur n'est envoyée."""
import re
import os
import boto3
from botocore.config import Config
from langchain_aws import ChatBedrockConverse
from pydantic import BaseModel, ConfigDict, Field


class PlanningProblem(Exception):
    pass


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    label: str = Field(default="", max_length=120)
    question: str = Field(min_length=1, max_length=180)
    explanation: str = Field(min_length=1, max_length=600)


class Guidance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(min_length=1, max_length=700)
    location: str = Field(max_length=250)
    conditions: str = Field(max_length=500)
    fields: list[Question]


def make_model():
    """One shared configuration for text and agent tool calls."""
    region = os.environ.get("AWS_REGION")
    if not region or not os.environ.get("AWS_BEARER_TOKEN_BEDROCK"):
        raise PlanningProblem("La configuration Bedrock n’est pas disponible.")
    client = boto3.client("bedrock-runtime", region_name=region, config=Config(
        connect_timeout=10, read_timeout=50, retries={"total_max_attempts": 1},
        ignore_configured_endpoint_urls=True,
    ))
    return ChatBedrockConverse(client=client,
        model=os.environ.get("BEDROCK_MODEL_ID", "eu.amazon.nova-2-lite-v1:0"),
        provider="amazon", region_name=region, max_tokens=2000, temperature=0)


def plain_words(text):
    text = re.sub(r"secret d[’']authentification", "mot de passe", text, flags=re.IGNORECASE)
    return re.sub(r"session de rattachement", "date et horaire", text, flags=re.IGNORECASE)


def describe_stage(observed, guidance):
    account = observed["stage"] in {"account", "login"}
    login = observed["stage"] == "login"
    fields = []
    for source, question in zip(observed["fields"], guidance.fields, strict=True):
        field = dict(source)
        field["question"], field["explanation"] = plain_words(question.question), plain_words(question.explanation)
        field["ui_label"] = plain_words(question.label or question.question.rstrip(" ?"))
        if field["kind"] == "secret":
            field["ui_label"] = "Mot de passe"
        elif field.get("depends_on"):
            field["ui_label"] = "Date et horaire"
        if field["kind"] == "secret":
            field["instruction"] = f"De {field.get('min_length', 1)} à {field.get('max_length', 128)} caractères. Utilise des données fictives pour la démonstration."
        fields.append(field)
    return {
        "id": observed["stage"], "fields": fields,
        "title": "Mon compte" if account else "Mon atelier",
        "review_title": "Vérifie les informations de ton compte" if account else "Vérifie ta réservation",
        "submit_label": "Me connecter" if login else "Créer mon compte" if account else "Réserver cet atelier",
        "commitment": "Ces informations seront envoyées au site pour te connecter." if login else "Ces informations seront envoyées au site pour créer ton compte." if account else "Tes réponses seront envoyées au site pour réserver cette séance.",
        "after_message": "Ton compte est créé. Tu n’as pas encore réservé d’atelier." if account else "",
        "show_conditions": not account,
    }
