"""Wrapper so `python -m scripts.seed_demo_data` also works from the project root."""

from app import create_app
from app.seed import seed


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        info = seed(reset=True)
        print(info["banner"])
        print("Demo logins:")
        for name, pw in info["users"].items():
            print("  {} / {}".format(name, pw))
