# Installation and Configuration Instructions

These steps assume a laptop with Python 3.10 or newer. The prototype was developed as a Year 2 academic project and is intended to run **locally**.

## 1. What you need

- Python 3.10, 3.11, or 3.12
- `pip` and `venv`
- A modern browser (Firefox, Chrome, Edge, or Safari)
- Optional: Git, Visual Studio Code

You do **not** need MySQL, Redis, Node.js, or a cloud account for the prototype.

## 2. Install (Windows, macOS, or Linux)

```bash
git clone <your-repo-url> system-design
cd system-design

python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate

pip install -r requirements.txt
```

Copy the example environment file and set a secret key:

```bash
cp .env.example .env
```

Edit `.env` and change `SECRET_KEY` to a long random string if you ever expose the app beyond your own machine.

## 3. Create the database and synthetic demo data

```bash
python run.py --init
```

This command:

1. Creates `instance/welfare.db` (SQLite).
2. Creates tables.
3. Inserts **synthetic demonstration users, households, check-ins, alerts, and visits**.
4. Prints the demo login table.

You can also seed from Python:

```bash
python -c "from app import create_app; from scripts.seed_demo_data import seed; app=create_app(); app.app_context().push(); seed()"
```

## 4. Run the application

```bash
python run.py
```

Open `http://127.0.0.1:5000` in your browser.

Demo accounts (all passwords follow the pattern below):

| Username | Password | Role |
| --- | --- | --- |
| admin | Admin@123 | Administrator |
| amina | Care@123 | Caregiver (primary for most households) |
| david | Care@123 | Caregiver |
| margaret | Elder@123 | Elderly person |
| john | Elder@123 | Elderly person |
| grace.family | Family@123 | Family member |

All people and events in the database are **fictitious**.

## 5. Run tests

```bash
pytest -q
```

## 6. Optional: MySQL later

1. Create an empty MySQL database.
2. Run `database/schema_mysql.sql`.
3. Set `DATABASE_URL=mysql+pymysql://user:pass@localhost/welfare` in `.env`.
4. You would also add `PyMySQL` to requirements. This is **not** required for the assessed prototype.

## 7. Backup

Administrators can download a copy of the SQLite file from **Settings → Download backup**.  
Or copy `instance/welfare.db` while the app is stopped.

## 8. Common errors

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: flask` | Virtual environment not active | `source venv/bin/activate` then `pip install -r requirements.txt` |
| `Address already in use` | Port 5000 busy | `python run.py --port 5001` |
| Login fails after re-clone | Database not seeded | `python run.py --init` |
| `database is locked` | Two writers on SQLite | Stop extra `run.py` processes |
| CSS looks unstyled | No network for CDN fonts | The layout still works; Bootstrap CSS is also vendored in `app/static` as a fallback where possible. The prototype uses CDN Bootstrap; if offline, download Bootstrap locally. |
| Missed alerts not appearing | App was not running at due time | Open any staff page; the scanner also runs on request. Or use the admin “Run missed-check scan now” button. |
| `csrf token missing` | Stale tab after restart | Refresh the login page |

## 9. Stopping and resetting

Stop the server with `Ctrl+C`.  
To reset demonstration data, delete `instance/welfare.db` and run `python run.py --init` again.
