"""État de navigation indépendant de Streamlit et du site source."""
import copy
import re


def length(value):
    return len(value.encode("utf-16-le")) // 2


class Journey:
    def __init__(self, description):
        self.description = copy.deepcopy(description)
        self.fields = {f["id"]: f for stage in self.description["stages"] for f in stage["fields"]}
        self.steps = []
        for stage in self.description["stages"]:
            self.steps.extend({"kind": "field", "stage": stage, "field": field} for field in stage["fields"])
            self.steps.append({"kind": "review", "stage": stage})
        self.steps.append({"kind": "done"})
        self.current = 0
        self.answers = {}
        self.secrets = {}
        self.editing_review = None
        self.completed = set()
        self.error = ""

    @property
    def step(self):
        return self.steps[self.current]

    def value(self, field):
        return (self.secrets if field["kind"] == "secret" else self.answers).get(field["id"], "")

    def options(self, field):
        if "depends_on" in field:
            return field["options_by_value"].get(self.answers.get(field["depends_on"]), [])
        return field.get("options", [])

    def set_answer(self, field_id, value):
        field = self.fields[field_id]
        target = self.secrets if field["kind"] == "secret" else self.answers
        if target.get(field_id) != value:
            target[field_id] = value
            for dependent in self.fields.values():
                if dependent.get("depends_on") == field_id:
                    self.answers.pop(dependent["id"], None)
        self.error = ""

    def validate(self, field):
        value = self.value(field)
        if field.get("required") and (value is None or not str(value).strip()):
            return "Choisis une réponse pour continuer." if field["kind"] == "choice" else "Écris ta réponse pour continuer."
        if field["kind"] == "choice":
            return "" if value in [o["value"] for o in self.options(field)] else "Ce choix n’est plus disponible. Choisis à nouveau."
        if field.get("format") == "email":
            if "@" not in value:
                return "Il manque le signe @ dans ton adresse. Vérifie ton adresse et corrige-la."
            if not re.fullmatch(r"[^\s@]+@[^\s@.]+(?:\.[^\s@.]+)*\.[a-zA-Z]{2,}", value.strip()):
                return "Vérifie ton adresse et sa fin : elle doit contenir un point puis des lettres, comme .fr ou .com."
        if length(value) < field.get("min_length", 0):
            return f"Écris au moins {field['min_length']} caractères."
        if length(value) > field.get("max_length", float("inf")):
            return f"Le site accepte {field['max_length']} caractères au maximum."
        return ""

    def public_answers(self):
        """Réponses ordinaires pour les outils locaux, jamais pour les messages du modèle."""
        return {key: copy.deepcopy(value) for key, value in self.answers.items() if key in self.fields and self.fields[key]["kind"] != "secret"}

    def display_value(self, field):
        if field["kind"] == "secret":
            return "Renseigné — valeur masquée" if self.value(field) else "À renseigner"
        value = self.value(field)
        if field["kind"] == "choice":
            return next((o["label"] for o in self.options(field) if o["value"] == value), "À choisir")
        return value or "À renseigner"

    def edit(self, field_id):
        self.editing_review = self.current
        self.current = next(i for i, s in enumerate(self.steps) if s.get("field", {}).get("id") == field_id)
        self.error = ""

    def back(self):
        if self.editing_review is not None:
            self.current, self.editing_review = self.editing_review, None
        elif self.current > 0:
            # A committed stage cannot be edited through Back.
            previous = self.steps[self.current - 1]
            if previous.get("kind") != "review" or previous["stage"]["id"] not in self.completed:
                self.current -= 1
        self.error = ""

    def advance(self):
        if self.step["kind"] == "field":
            field = self.step["field"]
            self.error = self.validate(field)
            if self.error:
                return
            if self.editing_review is not None:
                fields = self.steps[self.editing_review]["stage"]["fields"]
                dependent = next((f for f in fields if f.get("depends_on") == field["id"] and self.validate(f)), None)
                if dependent:
                    self.current = next(i for i, s in enumerate(self.steps) if s.get("field", {}).get("id") == dependent["id"])
                else:
                    self.current, self.editing_review = self.editing_review, None
            else:
                self.current += 1
        elif self.step["kind"] == "review":
            stage = self.step["stage"]
            for field in stage["fields"]:
                message = self.validate(field)
                if message:
                    self.edit(field["id"])
                    self.error = message
                    return
            self.completed.add(stage["id"])
            for field in stage["fields"]:
                if field["kind"] == "secret":
                    self.secrets.pop(field["id"], None)
            self.current += 1
