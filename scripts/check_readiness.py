"""Read-only functional preflight. No account or reservation is created."""
import json
import os
import sys
import time
from urllib.request import urlopen
from aide.agent_browser import AgentBrowser
from aide.connected import ConnectedJourney


def main():
    started = time.perf_counter()
    stage = "services"
    try:
        base = os.environ.get("SITE_BASE_URL", "http://site:8000")
        for url in (base + "/health", "http://127.0.0.1:8501/_stcore/health"):
            with urlopen(url, timeout=5) as response:
                if response.status != 200:
                    raise RuntimeError("Service unavailable")
        stage = "agent_playwright_bedrock"
        j = ConnectedJourney(AgentBrowser(base))
        j.discover_home()
        purposes = {a["purpose"] for a in (j.homepage or {}).get("actions", [])}
        if j.status != "ready" or purposes != {"account", "login", "reservation"}:
            print(json.dumps({"status": "not_ready", "stage": stage, "message": j.error or "Actions attendues non découvertes.", "trace": j.trace}, ensure_ascii=False))
            return 1
        print(json.dumps({"status": "ready", "checked": ["site", "streamlit", "playwright", "bedrock_tool_calls", "observed_actions"],
                          "model_calls": len(j.metrics), "seconds": round(time.perf_counter() - started, 2),
                          "accounts_created": 0, "reservations_created": 0}, ensure_ascii=False))
        return 0
    except Exception as error:
        print(json.dumps({"status": "not_ready", "stage": stage, "error_type": type(error).__name__,
                          "message": "Vérifier Docker, Internet et la validité de la clé Bedrock. Aucun secret affiché."}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
