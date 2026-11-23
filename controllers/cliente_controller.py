from flask import Blueprint, render_template, request, redirect, session, flash, jsonify
from models import cliente_model
from functools import wraps
import os
import uuid

bp = Blueprint('cliente', __name__, url_prefix='/clientes')

UPLOAD_DIR = "static/uploads/clientes"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def requer_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@requer_login
def listar():
    clientes = cliente_model.listar_clientes()
    return render_template('clientes.html', clientes=clientes)

@bp.route('/novo', methods=['GET', 'POST'])
@requer_login
def novo():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']

        documento = None
        arquivo = request.files.get("documento")

        if arquivo and arquivo.filename != "":
            ext = arquivo.filename.split(".")[-1]
            nome_arq = f"{uuid.uuid4()}.{ext}"
            caminho = os.path.join(UPLOAD_DIR, nome_arq)
            arquivo.save(caminho)
            documento = nome_arq

        sucesso, mensagem = cliente_model.adicionar_cliente(nome, email, telefone, documento)

        if sucesso:
            flash(mensagem, 'success')
            return redirect('/clientes')
        else:
            flash(mensagem, 'error')

    return render_template('clientes_form.html', cliente=None)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@requer_login
def editar(id):
    cliente = cliente_model.buscar_cliente(id)
    if not cliente:
        flash('Cliente não encontrado.', 'error')
        return redirect('/clientes')

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']

        documento = None
        arquivo = request.files.get("documento")

        if arquivo and arquivo.filename != "":
            ext = arquivo.filename.split(".")[-1]
            nome_arq = f"{uuid.uuid4()}.{ext}"
            caminho = os.path.join(UPLOAD_DIR, nome_arq)
            arquivo.save(caminho)
            documento = nome_arq

        sucesso, mensagem = cliente_model.atualizar_cliente(id, nome, email, telefone, documento)

        if sucesso:
            flash(mensagem, 'success')
            return redirect('/clientes')
        else:
            flash(mensagem, 'error')

    return render_template('clientes_form.html', cliente=cliente)

@bp.route('/excluir/<int:id>', methods=['POST'])
@requer_login
def excluir(id):
    sucesso, mensagem = cliente_model.excluir_cliente(id)
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    return redirect('/clientes')


@bp.route('/api', methods=['GET'])
def api_listar():
    clientes = cliente_model.listar_clientes()
    return jsonify(clientes)

@bp.route('/api/<int:id>', methods=['GET'])
def api_buscar(id):
    cliente = cliente_model.buscar_cliente(id)
    if cliente:
        return jsonify(cliente)
    return jsonify({'erro': 'Cliente não encontrado'}), 404

@bp.route('/api', methods=['POST'])
def api_novo():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    telefone = dados.get('telefone')

    sucesso, mensagem = cliente_model.adicionar_cliente(nome, email, telefone, None)

    if sucesso:
        return jsonify({'mensagem': mensagem})
    return jsonify({'erro': mensagem}), 400

@bp.route('/api/<int:id>', methods=['PUT'])
def api_editar(id):
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    telefone = dados.get('telefone')

    sucesso, mensagem = cliente_model.atualizar_cliente(id, nome, email, telefone)

    if sucesso:
        return jsonify({'mensagem': mensagem})
    return jsonify({'erro': mensagem}), 400

@bp.route('/api/<int:id>', methods=['DELETE'])
def api_excluir(id):
    sucesso, mensagem = cliente_model.excluir_cliente(id)
    if sucesso:
        return jsonify({'mensagem': mensagem})
    return jsonify({'erro': mensagem}), 400
