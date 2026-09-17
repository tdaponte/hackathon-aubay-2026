"""Navigation and real UI rendering, with a local fixture only inside tests."""
import json
import unittest
from pathlib import Path
from unittest.mock import Mock
from streamlit.testing.v1 import AppTest
from aide.model import Journey
from aide.connected import ConnectedJourney

APP = Path(__file__).resolve().parents[1] / "app.py"


def description():
    data = json.loads((Path(__file__).parent / "fixtures/journey.json").read_text(encoding="utf-8"))
    for stage in data["stages"]:
        for field in stage["fields"]:
            field["ui_label"] = field["label"]
    return data


def app_fixture(data=None):
    model = Mock()
    model.bind_tools.return_value = model
    j = ConnectedJourney(Mock(), model)
    Journey.__init__(j, data or description())
    j.status = "ready"
    j.homepage = {"title": "Association de test", "paragraphs": ["Description observée."], "facts": ["Gratuit."],
                  "actions": [{"purpose": "account", "label": "Créer", "link_id": "test"}]}
    app = AppTest.from_file(str(APP))
    app.session_state["journey"] = j
    app.session_state["linked"] = True
    app.session_state["view"] = "conversation"
    return app.run()


class JourneyTests(unittest.TestCase):
    def test_secret_projection(self):
        j = Journey(description())
        j.set_answer("password", "NeverExpose123")
        self.assertNotIn("NeverExpose123", json.dumps(j.public_answers()))
        self.assertNotIn("password", j.public_answers())

    def test_edit_dependency_and_return(self):
        j = Journey(description())
        j.set_answer("activity", "photo")
        j.set_answer("slot", "photo-10")
        j.current = 6
        j.edit("activity")
        j.set_answer("activity", "peinture")
        j.advance()
        self.assertEqual(j.step["field"]["id"], "slot")
        self.assertEqual(j.value(j.fields["slot"]), "")
        j.advance()
        self.assertTrue(j.error)
        j.set_answer("slot", "peinture-03")
        j.advance()
        self.assertEqual(j.current, 6)

    def test_changed_questions_and_choices_render(self):
        data = description()
        data["stages"][0]["fields"][0]["question"] = "Comment veux-tu être appelé ?"
        data["stages"][1]["fields"][0]["options"][0]["label"] = "Dessin"
        app = app_fixture(data)
        self.assertIn("Comment veux-tu être appelé ?", [m.value for m in app.markdown])
        app.session_state.journey.current = 4
        app.run()
        self.assertIn("Dessin", app.radio[0].options)
        self.assertFalse(app.exception)

    def test_connected_ui_validation_back_and_edit(self):
        app = app_fixture()
        def click(label):
            next(b for b in app.button if b.label == label).click().run()
            self.assertFalse(app.exception)
        app.text_input[0].set_value("Alex").run()
        click("Envoyer ma réponse")
        app.text_input[0].set_value("alexexample.test").run()
        click("Envoyer ma réponse")
        self.assertIn("@", app.error[0].value)
        click("Retour")
        self.assertEqual(app.text_input[0].value, "Alex")
        click("Envoyer ma réponse")
        self.assertEqual(app.text_input[0].value, "alexexample.test")
        app.text_input[0].set_value("alex@example.test").run()
        click("Envoyer ma réponse")
        app.text_input[0].set_value("AtelierDemo2026!").run()
        click("Envoyer ma réponse")
        self.assertNotIn("AtelierDemo2026!", "".join(t.value for t in app.text))
        app.button(key="edit_email").click().run()
        app.text_input[0].set_value("autre@example.test").run()
        click("Enregistrer ma modification")
        self.assertEqual(app.session_state.journey.current, 3)
        click("Retour aux actions")
        self.assertEqual(app.session_state.journey.secrets, {})
        self.assertNotIn("input_password", app.session_state)

    def test_direct_access_requests_source_link(self):
        app = AppTest.from_file(str(APP)).run()
        self.assertFalse(app.exception)
        self.assertIn("Commence sur le site", app.info[0].value)
