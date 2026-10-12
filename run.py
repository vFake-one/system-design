import argparse

from app import create_app, db

app = create_app()


def init_db():
    with app.app_context():
        from app.seed import seed

        info = seed(reset=True)
        print(info["banner"])
        print()
        print("Database ready. Synthetic demo logins:")
        print("  {:<16} {}".format("Username", "Password"))
        for name, pw in info["users"].items():
            print("  {:<16} {}".format(name, pw))
        print()
        print("All records are fictitious. This prototype is not emergency services.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Elderly household welfare check-in prototype")
    parser.add_argument("--init", action="store_true", help="Create SQLite DB and seed synthetic data")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    if args.init:
        init_db()
    else:
        with app.app_context():
            db.create_all()
        app.run(host="0.0.0.0", port=args.port, debug=True)
