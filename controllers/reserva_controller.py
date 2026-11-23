from flask import Blueprint, render_template, request, redirect, session, flash, jsonify, current_app
from flask_mail import Message, Mail
from models import reserva_model, cliente_model, quarto_model
from datetime import datetime
from functools import wraps

bp = Blueprint('reserva', __name__, url_prefix='/reservas')

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
    reservas = reserva_model.listar_reservas()
    return render_template('reservas.html', reservas=reservas)

@bp.route('/novo', methods=['GET', 'POST'])
@requer_login
def novo():
    clientes = cliente_model.listar_clientes()
    quartos = quarto_model.listar_quartos()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        quarto_id = request.form['quarto_id']
        data_inicio_str = request.form['data_checkin']
        data_fim_str = request.form['data_checkout']
        adultos = request.form.get('adultos')
        criancas = request.form.get('criancas')
        if not cliente_id or not quarto_id or not data_inicio_str or not data_fim_str or not adultos or not criancas:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('reservas_form.html', reserva=None, clientes=clientes, quartos=quartos)
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
        except ValueError:
            flash('Formato de data inválido.', 'error')
            return render_template('reservas_form.html', reserva=None, clientes=clientes, quartos=quartos)
        if data_inicio >= data_fim:
            flash('Check-in deve ser antes do check-out.', 'error')
            return render_template('reservas_form.html', reserva=None, clientes=clientes, quartos=quartos)
        sucesso, mensagem = reserva_model.adicionar_reserva(cliente_id, quarto_id, data_inicio, data_fim, adultos, criancas)
        if sucesso:
            flash(mensagem, 'success')
            return redirect('/reservas')
        else:
            flash(mensagem, 'error')
    return render_template('reservas_form.html', reserva=None, clientes=clientes, quartos=quartos)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@requer_login
def editar(id):
    reserva = reserva_model.buscar_reserva(id)
    clientes = cliente_model.listar_clientes()
    quartos = quarto_model.listar_quartos()
    if not reserva:
        flash('Reserva não encontrada.', 'error')
        return redirect('/reservas')
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        quarto_id = request.form['quarto_id']
        data_inicio_str = request.form['data_checkin']
        data_fim_str = request.form['data_checkout']
        status = request.form['status']
        adultos = request.form.get("adultos", reserva.get("adultos"))
        criancas = request.form.get("criancas", reserva.get("criancas"))
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
        except ValueError:
            flash('Formato de data inválido.', 'error')
            return render_template('reservas_form.html', reserva=reserva, clientes=clientes, quartos=quartos)
        sucesso, mensagem = reserva_model.atualizar_reserva(id, cliente_id, quarto_id, data_inicio, data_fim, status, adultos, criancas)
        if sucesso:
            flash(mensagem, 'success')
            return redirect('/reservas')
        else:
            flash(mensagem, 'error')
    return render_template('reservas_form.html', reserva=reserva, clientes=clientes, quartos=quartos)

@bp.route('/excluir/<int:id>', methods=['POST'])
@requer_login
def excluir(id):
    sucesso, mensagem = reserva_model.excluir_reserva(id)
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    return redirect('/reservas')

@bp.route('/api', methods=['GET'])
def api_listar():
    reservas = reserva_model.listar_reservas()
    return jsonify(reservas)

@bp.route('/api/<int:id>', methods=['GET'])
def api_buscar(id):
    reserva = reserva_model.buscar_reserva(id)
    if reserva:
        return jsonify(reserva)
    return jsonify({'erro': 'Reserva não encontrada'}), 404

@bp.route('/api', methods=['POST'])
def api_novo():
    dados = request.get_json()
    cliente_id = dados.get('cliente_id')
    quarto_id = dados.get('quarto_id')
    data_inicio_str = dados.get('data_inicio')
    data_fim_str = dados.get('data_fim')
    adultos = dados.get('adultos')
    criancas = dados.get('criancas')
    if not cliente_id or not quarto_id or not data_inicio_str or not data_fim_str or not adultos or not criancas:
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'erro': 'Formato de data inválido'}), 400
    sucesso, mensagem = reserva_model.adicionar_reserva(cliente_id, quarto_id, data_inicio, data_fim, adultos, criancas)
    if sucesso:
        return jsonify({'mensagem': mensagem})
    return jsonify({'erro': mensagem}), 400

@bp.route('/api/<int:id>', methods=['PUT'])
def api_editar(id):
    dados = request.get_json()
    cliente_id = dados.get('cliente_id')
    quarto_id = dados.get('quarto_id')
    data_inicio_str = dados.get('data_inicio')
    data_fim_str = dados.get('data_fim')
    status = dados.get('status')
    adultos = dados.get('adultos')
    criancas = dados.get('criancas')
    if not cliente_id or not quarto_id or not data_inicio_str or not data_fim_str or not status:
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'erro': 'Formato de data inválido'}), 400
    sucesso, mensagem = reserva_model.atualizar_reserva(id, cliente_id, quarto_id, data_inicio, data_fim, status, adultos, criancas)
    if sucesso:
        return jsonify({'mensagem': mensagem})
    return jsonify({'erro': mensagem}), 400

@bp.route('/api/<int:id>', methods=['DELETE'])
def api_excluir(id):
    sucesso, mensagem = reserva_model.excluir_reserva(id)
    if sucesso:
        return jsonify({'mensagem': mensagem})
    return jsonify({'erro': mensagem}), 400
