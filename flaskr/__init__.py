
import os

from flask import Flask
from .db import db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///flaskr.sqlite",
        UPLOAD_FOLDER=os.path.join(
            app.root_path, "static", "uploads"
        )
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    db.init_app(app)

    from . import models

    with app.app_context():
        db.create_all()

    from . import auth
    from . import blog
    from . import calculos

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(calculos.bp)

    app.add_url_rule("/", endpoint="index")

    return app
