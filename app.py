from app import create_app, init_db_on_startup

app = create_app()

if __name__ == "__main__":
    init_db_on_startup()
    app.run(debug=True, port=5000)
