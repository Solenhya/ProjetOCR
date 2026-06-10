# ProjetOCR

Application web de traitement OCR de factures (PDF et images) avec interface utilisateur, API FastAPI, stockage PostgreSQL et extraction de donnees via Tesseract.

## 1. Vue d'ensemble

Le projet permet de:
- importer une facture (fichier local ou URL),
- lancer un traitement OCR,
- visualiser et corriger les informations detectees,
- valider et enregistrer les resultats en base.

Technologies principales:
- Backend: FastAPI
- OCR: Tesseract + OpenCV
- Base de donnees: PostgreSQL
- Authentification: JWT

## 2. Prerequis

Prerequis communs:
- Python 3.12+
- PostgreSQL 12+
- Tesseract OCR installe sur la machine (si execution locale)
- Docker Desktop (optionnel, recommande pour un demarrage rapide)

## 3. Demarrage rapide avec Docker (recommande)

Cette methode est la plus simple pour lancer l'application sans configurer Python localement.

### 3.1 Construire l'image

Depuis la racine du projet:

```bash
docker build -t projet-ocr .
```

### 3.2 Lancer le conteneur

Adaptez les variables ci-dessous a votre environnement PostgreSQL.

```bash
docker run --rm -p 8000:8000 \
	-e DBUSER=postgres \
	-e DBPASSWORD=postgres \
	-e DBHOST=host.docker.internal \
	-e DBNAME=ocr_db \
	-e DBPORT=5432 \
	-e DB_SCHEMA=public \
	-e SECRET_KEY=change-me \
	-e ALGORITHM=HS256 \
	-e ACCESS_TOKEN_EXPIRE_MINUTES=30 \
	-e LIST_HOST=https://example.local \
	-e LIST_AUTH=token \
	projet-ocr
```

### 3.3 Acceder a l'application

- Interface/API: http://localhost:8000
- Documentation Swagger: http://localhost:8000/docs

## 4. Installation locale

### 4.1 Cloner le depot

```bash
git clone <url-du-repo>
cd ProjetOCR
```

### 4.2 Creer un environnement virtuel Python

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 4.3 Installer les dependances Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 Installer Tesseract OCR (obligatoire en local)

Windows:
- Installez Tesseract OCR (ex: paquet UB Mannheim).
- Ajoutez le dossier d'installation (ex: `C:\Program Files\Tesseract-OCR`) au `PATH`.
- Verifiez:

```powershell
tesseract --version
```

Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

macOS (Homebrew):

```bash
brew install tesseract
```

### 4.5 Configurer les variables d'environnement

Creez votre fichier `.env` a partir de `.env.example`.

Linux/macOS:

```bash
cp .env.example .env
```

Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

Puis adaptez les valeurs selon votre environnement.

Exemple minimal:

```env
DBUSER=postgres
DBPASSWORD=postgres
DBHOST=localhost
DBNAME=ocr_db
DBPORT=5432
DB_SCHEMA=public

SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

LIST_HOST=example.blob.core.windows.net
LIST_AUTH=sv=example&sig=example
```

Description rapide:
- DBUSER, DBPASSWORD, DBHOST, DBNAME, DBPORT, DB_SCHEMA: connexion PostgreSQL.
- SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES: generation et validite des tokens JWT.
- LIST_HOST, LIST_AUTH: acces au service externe utilise pour la recuperation de factures distantes.

Pourquoi definir LIST_HOST et LIST_AUTH ?
- Ces variables sont utilisees par le module de telechargement des factures preexistantes (mode import distant).
- `LIST_HOST` indique l'hote du stockage distant (sans `https://`).
- `LIST_AUTH` contient la signature/jeton de requete necessaire pour lister et recuperer les fichiers.
- Si vous ne telechargez pas de factures preexistantes depuis ce service externe, ces variables peuvent rester avec des valeurs d'exemple.

### 4.6 Lancer l'application

Option A (meme commande que Dockerfile):

```bash
fastapi run app/main.py --host 0.0.0.0 --port 8000
```

Option B (mode developpement avec reload):

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Puis ouvrez:
- Application: http://localhost:8000
- Swagger: http://localhost:8000/docs

## 5. Utilisation

### 5.1 Parcours interface web

1. Ouvrez la page de connexion.
2. Connectez-vous (ou creez un compte si necessaire).
3. Allez dans la page d'upload.
4. Chargez un fichier de facture (ou utilisez l'import distant selon votre configuration).
5. Lancez le traitement OCR.
6. Verifiez les informations extraites (fournisseur, date, montants, lignes, etc.).
7. Validez pour enregistrer en base.

### 5.2 Utilisation via API

- L'ensemble des endpoints est visible dans Swagger: http://localhost:8000/docs
- Endpoints courants:
	- `POST /login` : authentification
	- `POST /display-ocr` : previsualisation OCR
	- `POST /autoOCR` : traitement OCR complet
	- `POST /resultat` : validation/enregistrement

## 6. Verification rapide

Verifiez que:
- l'application repond sur http://localhost:8000,
- `/docs` est accessible,
- une facture test peut etre traitee sans erreur,
- les donnees apparaissent bien en base PostgreSQL apres validation.

## 7. Depannage

Probleme: `tesseract is not installed or it's not in your PATH`
- Cause: Tesseract absent ou non present dans `PATH`.
- Solution: installer Tesseract puis redemarrer le terminal.

Probleme: erreur de connexion PostgreSQL
- Cause: variables DB incorrectes ou serveur arrete.
- Solution: verifier `DBHOST`, `DBPORT`, `DBUSER`, `DBPASSWORD`, `DBNAME` et l'etat du service PostgreSQL.

Probleme: `401 Unauthorized`
- Cause: token absent/invalide/expire.
- Solution: se reconnecter et verifier les variables JWT (`SECRET_KEY`, `ALGORITHM`, expiration).

Probleme: certaines fonctions d'import distant ne marchent pas
- Cause: service externe indisponible ou `LIST_HOST` / `LIST_AUTH` invalides.
- Solution: verifier la disponibilite du service cible et les valeurs configurees.

## 8. Commandes utiles

Lancer les tests:

```bash
pytest test/test_ToFormat.py -v
```

Arreter le conteneur Docker en cours (si lance sans `--rm`):

```bash
docker ps
docker stop <container_id>
```