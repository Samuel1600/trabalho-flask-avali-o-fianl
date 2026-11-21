
import os
import uuid

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    current_app,
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from . import db
from .auth import login_required
from .models import Post


bp = Blueprint("blog", __name__)

EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def salvar_imagem(arquivo):
    if not arquivo or not arquivo.filename:
        return None

    nome = secure_filename(arquivo.filename)
    extensao = os.path.splitext(nome)[1].lower()

    if extensao not in EXTENSOES_PERMITIDAS:
        raise ValueError("Formato de imagem não permitido.")

    nome_arquivo = str(uuid.uuid4()) + extensao
    caminho = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        nome_arquivo
    )

    arquivo.save(caminho)
    return nome_arquivo


@bp.route("/")
def index():
    posts = db.session.execute(
        db.select(Post).order_by(Post.created.desc())
    ).scalars().all()

    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    post = db.session.get(Post, id)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        arquivo = request.files.get("imagem_post")

        error = None
        nome_imagem = None

        if not title:
            error = "Title is required."

        if error is None and arquivo and arquivo.filename:
            try:
                nome_imagem = salvar_imagem(arquivo)
            except ValueError as e:
                error = str(e)

        if error is not None:
            flash(error)
        else:
            post = Post(
                title=title,
                body=body,
                author_id=g.user.id,
                imagem_post=nome_imagem
            )

            db.session.add(post)
            db.session.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        arquivo = request.files.get("imagem_post")

        error = None
        nome_imagem = None

        if not title:
            error = "Title is required."

        if error is None and arquivo and arquivo.filename:
            try:
                nome_imagem = salvar_imagem(arquivo)
            except ValueError as e:
                error = str(e)

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body

            if nome_imagem:
                post.imagem_post = nome_imagem

            db.session.commit()

            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for("blog.index"))
