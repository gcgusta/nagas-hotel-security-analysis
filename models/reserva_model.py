import mysql.connector
from mysql.connector import Error
from config import obter_conexao

def listar_reservas():
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return []
            
        cur = conn.cursor(dictionary=True)
        cur.execute('''
            SELECT r.*, c.nome AS cliente_nome, q.numero AS quarto_numero
            FROM reservas r
            JOIN clientes c ON r.cliente_id = c.id
            JOIN quartos q ON r.quarto_id = q.id
            ORDER BY r.data_inicio DESC
        ''')
        reservas = cur.fetchall()
        return reservas
    except Error as e:
        print("Erro ao listar reservas:", e)
        return []
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def buscar_reserva(reserva_id):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return None
            
        cur = conn.cursor(dictionary=True)
        cur.execute('''
            SELECT r.*, c.nome AS cliente_nome, q.numero AS quarto_numero
            FROM reservas r
            JOIN clientes c ON r.cliente_id = c.id
            JOIN quartos q ON r.quarto_id = q.id
            WHERE r.id=%s
        ''', (reserva_id,))
        reserva = cur.fetchone()
        return reserva
    except Error as e:
        print("Erro ao buscar reserva:", e)
        return None
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def adicionar_reserva(cliente_id, quarto_id, data_inicio, data_fim, adultos, criancas):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False, "Erro de conexão com o banco de dados."
            
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO reservas (cliente_id, quarto_id, data_inicio, data_fim, adultos, criancas) VALUES (%s, %s, %s, %s, %s, %s)",
            (cliente_id, quarto_id, data_inicio, data_fim, adultos, criancas)
        )
        conn.commit()
        return True, "Reserva adicionada com sucesso!"
    except Error as e:
        print("Erro ao adicionar reserva:", e)
        return False, f"Erro ao adicionar reserva: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def atualizar_reserva(reserva_id, cliente_id, quarto_id, data_inicio, data_fim, status, adultos, criancas):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False, "Erro de conexão com o banco de dados."
            
        cur = conn.cursor()
        cur.execute(
            "UPDATE reservas SET cliente_id=%s, quarto_id=%s, data_inicio=%s, data_fim=%s, status=%s, adultos=%s, criancas=%s WHERE id=%s",
            (cliente_id, quarto_id, data_inicio, data_fim, status, adultos, criancas, reserva_id)
        )
        conn.commit()
        affected = cur.rowcount
        if affected == 0:
            return False, "Reserva não encontrada."
        return True, "Reserva atualizada com sucesso!"
    except Error as e:
        print("Erro ao atualizar reserva:", e)
        return False, f"Erro ao atualizar reserva: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def excluir_reserva(reserva_id):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False, "Erro de conexão com o banco de dados."
            
        cur = conn.cursor()
        cur.execute("DELETE FROM reservas WHERE id=%s", (reserva_id,))
        conn.commit()
        affected = cur.rowcount
        if affected == 0:
            return False, "Reserva não encontrada."
        return True, "Reserva excluída com sucesso!"
    except Error as e:
        print("Erro ao excluir reserva:", e)
        return False, f"Erro ao excluir reserva: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
