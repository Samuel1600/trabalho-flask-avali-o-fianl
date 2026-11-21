
import functools
import os
import uuid

from flask import (
    Blueprint, flash, g, redirect, render_template,
    request, session, url_for, current_app
)

from werkzeug.utils import secure_filename
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from sqlalchemy.exc import IntegrityError

from flaskr import db
from flaskr.models import User


bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)


@bp.route("/register", methods=("GET", "POST"))
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        arquivo = request.files.get("avatar")
        nome_arquivo = None

        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:

            if arquivo and arquivo.filename:
                nome = secure_filename(arquivo.filename)

                if not nome:
                    error = "Nome de arquivo inválido."
                else:
                    extensao = os.path.splitext(nome)[1].lower()

                    if extensao not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                        error = "Formato de imagem não permitido."
                    else:
                        nome_arquivo = str(uuid.uuid4()) + extensao

                        caminho = os.path.join(
                            current_app.config["UPLOAD_FOLDER"],
                            nome_arquivo
                        )

                        arquivo.save(caminho)

        if error is None:
            usuario = User(
                username=username,
                password=generate_password_hash(password),
                avatar=nome_arquivo
            )

            try:
                db.session.add(usuario)
                db.session.commit()

            except IntegrityError:
                db.session.rollback()
                error = f"User {username} is already registered."

            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error = None

        user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()

        if user is None:
            error = "Incorrect username."

        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.id

            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("index"))
