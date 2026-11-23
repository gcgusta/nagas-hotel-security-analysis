from flask import Blueprint, render_template, request, redirect, session, flash, jsonify
from models import quarto_model
from functools import wraps

bp = Blueprint('quarto', __name__, url_prefix='/quartos')

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
    quartos = quarto_model.listar_quartos()
    return render_template('quartos.html', quartos=quartos)

@bp.route('/novo', methods=['GET', 'POST'])
@requer_login
def novo():
    if request.method == 'POST':
        numero = request.form['numero']
        tipo = request.form['tipo']
        preco = request.form['valor']
        if not numero or not tipo or not preco:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('quartos_form.html', quarto=None)
        try:
            preco = float(preco)
        except ValueError:
            flash('Preço deve ser um número válido.', 'error')
            return render_template('quartos_form.html', quarto=None)
        sucesso, mensagem = quarto_model.adicionar_quarto(numero, tipo, preco)
        flash(mensagem, 'success' if sucesso else 'error')
        return redirect('/quartos')
    return render_template('quartos_form.html', quarto=None)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@requer_login
def editar(id):
    quarto = quarto_model.buscar_quarto(id)
    if not quarto:
        flash('Quarto não encontrado.', 'error')
        return redirect('/quartos')
    if request.method == 'POST':
        numero = request.form['numero']
        tipo = request.form['tipo']
        preco = request.form['valor']
        status = request.form['status']
        if not numero or not tipo or not preco or not status:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('quartos_form.html', quarto=quarto)
        try:
            preco = float(preco)
        except ValueError:
            flash('Preço deve ser um número válido.', 'error')
            return render_template('quartos_form.html', quarto=quarto)
        sucesso, mensagem = quarto_model.atualizar_quarto(id, numero, tipo, preco, status)
        flash(mensagem, 'success' if sucesso else 'error')
        return redirect('/quartos')
    return render_template('quartos_form.html', quarto=quarto)

@bp.route('/excluir/<int:id>', methods=['POST'])
@requer_login
def excluir(id):
    sucesso, mensagem = quarto_model.excluir_quarto(id)
    flash(mensagem, 'success' if sucesso else 'error')
    return redirect('/quartos')

@bp.route('/api', methods=['GET'])
def api_listar_quartos():
    quartos = quarto_model.listar_quartos()
    return jsonify(quartos)

@bp.route('/api/<int:id>', methods=['GET'])
def api_buscar_quarto(id):
    quarto = quarto_model.buscar_quarto(id)
    if quarto:
        return jsonify(quarto)
    return jsonify({"erro": "Quarto não encontrado"}), 404

@bp.route('/api', methods=['POST'])
def api_criar_quarto():
    data = request.get_json()
    numero = data.get('numero')
    tipo = data.get('tipo')
    preco = data.get('preco')
    if not numero or not tipo or not preco:
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400
    try:
        preco = float(preco)
    except ValueError:
        return jsonify({"erro": "Preço inválido"}), 400
    sucesso, mensagem = quarto_model.adicionar_quarto(numero, tipo, preco)
    if sucesso:
        return jsonify({"mensagem": mensagem}), 201
    return jsonify({"erro": mensagem}), 400

@bp.route('/api/<int:id>', methods=['PUT'])
def api_atualizar_quarto(id):
    data = request.get_json()
    numero = data.get('numero')
    tipo = data.get('tipo')
    preco = data.get('preco')
    status = data.get('status')
    if not numero or not tipo or not preco or not status:
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400
    try:
        preco = float(preco)
    except ValueError:
        return jsonify({"erro": "Preço inválido"}), 400
    sucesso, mensagem = quarto_model.atualizar_quarto(id, numero, tipo, preco, status)
    if sucesso:
        return jsonify({"mensagem": mensagem})
    return jsonify({"erro": mensagem}), 404

@bp.route('/api/<int:id>', methods=['DELETE'])
def api_excluir_quarto(id):
    sucesso, mensagem = quarto_model.excluir_quarto(id)
    if sucesso:
        return jsonify({"mensagem": mensagem})
    return jsonify({"erro": mensagem}), 404
