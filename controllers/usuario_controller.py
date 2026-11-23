from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import usuario_model

usuario_bp = Blueprint('usuario', __name__)


@usuario_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        sucesso, mensagem = usuario_model.registrar_usuario(nome, email, senha)
        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('usuario.login'))
        else:
            flash(mensagem, 'error')

    return render_template('register.html')


@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        usuario = usuario_model.autenticar_usuario(email, senha)
        if usuario:
            session['usuario'] = usuario
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('E-mail ou senha incorretos.', 'error')

    return render_template('login.html')


@usuario_bp.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Você saiu da conta.', 'success')
    return redirect(url_for('usuario.login'))
