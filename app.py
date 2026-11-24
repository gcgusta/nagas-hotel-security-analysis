
from flask import Flask, render_template, request, redirect, session, flash, send_from_directory, url_for
from functools import wraps
from urllib.parse import urljoin
import os
import secrets
from dotenv import load_dotenv

from models import usuario_model
from controllers import cliente_controller
from controllers import quarto_controller
from controllers import reserva_controller

from flask_mail import Mail, Message

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__, template_folder="views")

app.register_blueprint(cliente_controller.bp, url_prefix='/clientes')
app.register_blueprint(quarto_controller.bp, url_prefix='/quartos')
app.register_blueprint(reserva_controller.bp, url_prefix='/reservas')

# Chave secreta carregada do ambiente
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Endereço público confiável da aplicação
app.config["PUBLIC_BASE_URL"] = os.getenv(
    "PUBLIC_BASE_URL",
    "http://127.0.0.1:5000"
).rstrip("/")

# Configurações de e-mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

# Utiliza MAIL_USERNAME como alternativa ao remetente padrão
app.config['MAIL_DEFAULT_SENDER'] = (
    os.getenv("MAIL_DEFAULT_SENDER")
    or app.config['MAIL_USERNAME']
)

mail = Mail(app)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def requer_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect('/login')

        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/contato", methods=["GET", "POST"])
def contato():
    if request.method == "POST":
        email = request.form["email"]
        mensagem = request.form["mensagem"]

        print("\n📩 NOVA MENSAGEM DE CONTATO 📩")
        print(f"Email: {email}")
        print(f"Mensagem: {mensagem}\n")

        flash("Mensagem enviada com sucesso!", "success")
        return redirect(url_for("contato"))

    return render_template("contato.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = usuario_model.autenticar_usuario(email, senha)

        if usuario:
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]

            flash("Login realizado com sucesso!", "success")
            return redirect("/")

        else:
            flash("E-mail ou senha incorretos!", "error")

    return render_template("login.html")


@app.route("/esqueci-senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email")
        usuario = usuario_model.buscar_usuario_por_email(email)

        if usuario:
            token = secrets.token_urlsafe(16)
            usuario_model.salvar_token_reset(usuario["id"], token)

            # Gera o caminho sem confiar no cabeçalho Host da requisição
            caminho_reset = url_for("reset_senha", token=token)

            # Monta o link usando o endereço confiável configurado no ambiente
            link = urljoin(
                app.config["PUBLIC_BASE_URL"] + "/",
                caminho_reset.lstrip("/")
            )

            msg = Message(
                subject="Redefinição de Senha - Hotel App",
                sender=app.config["MAIL_DEFAULT_SENDER"],
                recipients=[email]
            )

            msg.body = (
                f"Olá {usuario['nome']},\n\n"
                f"Use este link para redefinir sua senha:\n{link}\n\n"
                f"O link expira em 1 hora."
            )

            try:
                mail.send(msg)

                flash(
                    "Um link de redefinição foi enviado para seu email.",
                    "success"
                )

            except Exception:
                app.logger.exception("ERRO DETALHADO AO ENVIAR EMAIL")

                flash(
                    "Não foi possível enviar o email. Verifique a configuração.",
                    "error"
                )

        else:
            flash("Email não encontrado.", "error")

    return render_template("esqueci_senha.html")


@app.route("/reset-senha/<token>", methods=["GET", "POST"])
def reset_senha(token):
    usuario = usuario_model.buscar_usuario_por_token(token)

    if not usuario:
        flash("Token inválido ou expirado.", "error")
        return redirect("/login")

    if request.method == "POST":
        senha = request.form.get("senha")
        senha_confirma = request.form.get("senha_confirma")

        if senha != senha_confirma:
            flash("As senhas não coincidem.", "error")
            return render_template("reset_senha.html", token=token)

        usuario_model.redefinir_senha(usuario["id"], senha)

        flash("Senha atualizada com sucesso!", "success")
        return redirect("/login")

    return render_template("reset_senha.html", token=token)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        sucesso = usuario_model.registrar_usuario(nome, email, senha)

        if sucesso:
            flash("Conta criada com sucesso!", "success")
            return redirect("/login")

        else:
            flash("Erro: E-mail já cadastrado!", "error")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.", "success")
    return redirect("/")


@app.route("/upload", methods=["POST"])
@requer_login
def upload():
    if "arquivo" not in request.files:
        flash("Nenhum arquivo enviado!", "error")
        return redirect("/")

    arquivo = request.files["arquivo"]

    if arquivo.filename == "":
        flash("Nome de arquivo inválido!", "error")
        return redirect("/")

    caminho = os.path.join(
        app.config["UPLOAD_FOLDER"],
        arquivo.filename
    )

    arquivo.save(caminho)

    flash("Arquivo enviado com sucesso!", "success")
    return redirect("/")


@app.route("/download/<nome_arquivo>")
@requer_login
def download(nome_arquivo):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        nome_arquivo,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=False)
