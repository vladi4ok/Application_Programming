from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/api/v1/hello-world-1")
    def hello_world():
        return "<p>Hello World 1</p>"

    return app


# waitress-serve --host 127.0.0.1 --port=5000 --call "main:create_app"
# http://127.0.0.1:5000/api/v1/hello-world-1
# venv\Scripts\activate
# curl -v -XGET http://localhost:5000/api/v1/hello-world-1
