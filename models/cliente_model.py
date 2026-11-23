import mysql.connector
from mysql.connector import Error
from config import obter_conexao

def listar_clientes():
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return []
            
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM clientes ORDER BY nome")
        clientes = cur.fetchall()
        return clientes
    except Error as e:
        print("Erro ao listar clientes:", e)
        return []
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def buscar_cliente(cliente_id):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return None
            
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
        cliente = cur.fetchone()
        return cliente
    except Error as e:
        print("Erro ao buscar cliente:", e)
        return None
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def adicionar_cliente(nome, email, telefone, documento):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False, "Erro de conexão com o banco de dados."
            
        cur = conn.cursor()
        cur.execute("SELECT id FROM clientes WHERE email = %s", (email,))
        if cur.fetchone():
            return False, "E-mail já cadastrado para outro cliente."
        
        cur.execute(
            "INSERT INTO clientes (nome, email, telefone, documento) VALUES (%s, %s, %s, %s)",
            (nome, email, telefone, documento)
        )
        conn.commit()
        return True, "Cliente adicionado com sucesso!"
    except Error as e:
        print("Erro ao adicionar cliente:", e)
        return False, f"Erro ao adicionar cliente: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def atualizar_cliente(cliente_id, nome, email, telefone, documento=None):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False, "Erro de conexão com o banco de dados."
            
        cur = conn.cursor()
        cur.execute("SELECT id FROM clientes WHERE email = %s AND id != %s", (email, cliente_id))
        if cur.fetchone():
            return False, "E-mail já cadastrado para outro cliente."

        if documento:  
            cur.execute(
                "UPDATE clientes SET nome=%s, email=%s, telefone=%s, documento=%s WHERE id=%s",
                (nome, email, telefone, documento, cliente_id)
            )
        else:
            cur.execute(
                "UPDATE clientes SET nome=%s, email=%s, telefone=%s WHERE id=%s",
                (nome, email, telefone, cliente_id)
            )

        conn.commit()
        return True, "Cliente atualizado com sucesso!"
    except Error as e:
        print("Erro ao atualizar cliente:", e)
        return False, f"Erro ao atualizar cliente: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

def excluir_cliente(cliente_id):
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            return False, "Erro de conexão com o banco de dados."
            
        cur = conn.cursor()
        cur.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
        conn.commit()
        affected = cur.rowcount
        if affected == 0:
            return False, "Cliente não encontrado."
        return True, "Cliente excluído com sucesso!"
    except Error as e:
        print("Erro ao excluir cliente:", e)
        return False, f"Erro ao excluir cliente: {e}"
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()
