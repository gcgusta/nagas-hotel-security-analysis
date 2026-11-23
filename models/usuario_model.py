import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from config import obter_conexao
from datetime import datetime, timedelta


def registrar_usuario(nome, email, senha):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        existente = cur.fetchone()
        if existente:
            return False
        senha_hash = generate_password_hash(senha)
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
            (nome, email, senha_hash)
        )
        conn.commit()
        return True
    except Error as e:
        print("Erro ao registrar usuário:", e)
        return False
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def autenticar_usuario(email, senha):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return None
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        if usuario and check_password_hash(usuario["senha"], senha):
            return usuario
        return None
    except Error as e:
        print("Erro ao autenticar usuário:", e)
        return None
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()


def buscar_usuario_por_email(email):
    """
    Retorna o usuário pelo email
    """
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return None
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        return cur.fetchone()
    except Error as e:
        print("Erro ao buscar usuário por email:", e)
        return None
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def salvar_token_reset(usuario_id, token):
    """
    Salva o token de reset de senha e o tempo de expiração (1 hora)
    """
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False
        cur = conn.cursor()
        expira = datetime.now() + timedelta(hours=1)
        cur.execute(
            "UPDATE usuarios SET reset_token=%s, token_expira=%s WHERE id=%s",
            (token, expira, usuario_id)
        )
        conn.commit()
        return True
    except Error as e:
        print("Erro ao salvar token de reset:", e)
        return False
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def buscar_usuario_por_token(token):
    """
    Retorna o usuário pelo token de reset válido
    """
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return None
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM usuarios WHERE reset_token=%s AND token_expira > NOW()",
            (token,)
        )
        return cur.fetchone()
    except Error as e:
        print("Erro ao buscar usuário por token:", e)
        return None
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def redefinir_senha(usuario_id, nova_senha):
    """
    Atualiza a senha do usuário e remove token/expiração
    """
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False
        cur = conn.cursor()
        senha_hash = generate_password_hash(nova_senha)
        cur.execute(
            "UPDATE usuarios SET senha=%s, reset_token=NULL, token_expira=NULL WHERE id=%s",
            (senha_hash, usuario_id)
        )
        conn.commit()
        return True
    except Error as e:
        print("Erro ao redefinir senha:", e)
        return False
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
