import mysql.connector
from mysql.connector import Error
from config import obter_conexao

def listar_quartos():
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return []

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM quartos ORDER BY numero")
        return cur.fetchall()
    except Error as e:
        print("Erro ao listar quartos:", e)
        return []
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def buscar_quarto(quarto_id):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return None

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM quartos WHERE id=%s", (quarto_id,))
        return cur.fetchone()
    except Error as e:
        print("Erro ao buscar quarto:", e)
        return None
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def adicionar_quarto(numero, tipo, preco):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False, "Erro de conexão com o banco de dados."

        cur = conn.cursor()
        cur.execute("SELECT id FROM quartos WHERE numero=%s", (numero,))
        if cur.fetchone():
            return False, "Número de quarto já cadastrado."

        cur.execute(
            "INSERT INTO quartos (numero, tipo, preco) VALUES (%s, %s, %s)",
            (numero, tipo, preco)
        )
        conn.commit()
        return True, "Quarto adicionado com sucesso!"
    except Error as e:
        print("Erro ao adicionar quarto:", e)
        return False, f"Erro ao adicionar quarto: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def atualizar_quarto(quarto_id, numero, tipo, preco, status):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False, "Erro de conexão com o banco de dados."

        cur = conn.cursor()
        cur.execute("SELECT id FROM quartos WHERE numero=%s AND id!=%s", (numero, quarto_id))
        if cur.fetchone():
            return False, "Número de quarto já cadastrado para outro quarto."

        cur.execute(
            "UPDATE quartos SET numero=%s, tipo=%s, preco=%s, status=%s WHERE id=%s",
            (numero, tipo, preco, status, quarto_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            return False, "Quarto não encontrado."
        return True, "Quarto atualizado com sucesso!"
    except Error as e:
        print("Erro ao atualizar quarto:", e)
        return False, f"Erro ao atualizar quarto: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def excluir_quarto(quarto_id):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False, "Erro de conexão com o banco de dados."

        cur = conn.cursor()
        cur.execute("DELETE FROM quartos WHERE id=%s", (quarto_id,))
        conn.commit()
        if cur.rowcount == 0:
            return False, "Quarto não encontrado."
        return True, "Quarto excluído com sucesso!"
    except Error as e:
        print("Erro ao excluir quarto:", e)
        return False, f"Erro ao excluir quarto: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
