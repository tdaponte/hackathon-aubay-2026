import argparse

from .database import reset, default_path

parser = argparse.ArgumentParser(description="Les ateliers du quartier — site fictif local")
parser.add_argument("command", choices=["serve", "reset"], nargs="?", default="serve")
parser.add_argument("--port", type=int, default=8000)
parser.add_argument("--yes", action="store_true", help="Confirmer la remise à zéro des données fictives")
args = parser.parse_args()
if args.command == "reset":
    if not args.yes:
        parser.error("La remise à zéro nécessite --yes (comptes, inscriptions et sessions de démonstration).")
    path = default_path()
    reset(path)
    print("Données de démonstration réinitialisées. Rechargez le navigateur.")
else:
    import uvicorn
    uvicorn.run("ateliers.app:app", host="127.0.0.1", port=args.port, access_log=False)
