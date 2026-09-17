@echo off
setlocal
pushd "%~dp0.."
set "DEMO_BUILD=0"
set "DEMO_FULL=0"
if /I "%~1"=="--build" set "DEMO_BUILD=1"
if /I "%~2"=="--build" set "DEMO_BUILD=1"
if /I "%~1"=="--full" set "DEMO_FULL=1"
if /I "%~2"=="--full" set "DEMO_FULL=1"
docker info --format "{{.ServerVersion}}"
if errorlevel 1 goto failed
if not exist ".env.bedrock" (
  echo Configuration .env.bedrock manquante.
  goto failed
)
if "%DEMO_BUILD%"=="1" (
  docker compose build
  if errorlevel 1 goto failed
)
docker compose up -d --no-build --wait --wait-timeout 90
if errorlevel 1 goto failed
docker compose exec -T maquette python -m scripts.check_readiness
if errorlevel 1 goto failed
if "%DEMO_FULL%"=="1" (
  echo Parcours reel : creation de donnees fictives et enregistrement de videos.
  docker run --rm --mount "type=bind,source=%CD%,target=/app" -e RECORD_DEMO=1 hackathon-aubay-2026-maquette python scripts/check_connected.py
  if errorlevel 1 goto failed
)
echo PRET : http://127.0.0.1:8000/ - deconnecter le precedent compte avant de commencer.
echo Utiliser une adresse fictive encore inutilisee. Mot de passe fictif : AtelierDemo2026!
popd
exit /b 0
:failed
echo ECHEC : verifier Docker, Internet et Bedrock. Aucun feu vert pour la demonstration.
popd
exit /b 1
