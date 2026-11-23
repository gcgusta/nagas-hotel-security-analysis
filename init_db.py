import mysql.connector
from config import obter_conexao
from werkzeug.security import generate_password_hash

def criar_tabelas():
    conn = None
    cur = None
    try:
        conn = obter_conexao()
        if conn is None:
            print("Não foi possível conectar ao banco de dados.")
            return
            
        cur = conn.cursor()

        print("Criando tabelas...")
        # Tabela de usuários
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                senha VARCHAR(255) NOT NULL
            )
        ''')

        # Tabela de clientes
        cur.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                telefone VARCHAR(20)
            )
        ''')

        # Tabela de quartos
        cur.execute('''
            CREATE TABLE IF NOT EXISTS quartos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero VARCHAR(10) NOT NULL UNIQUE,
                tipo VARCHAR(50) NOT NULL,
                preco FLOAT NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Disponível'
            )
        ''')

        # Tabela de reservas
        cur.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cliente_id INT NOT NULL,
                quarto_id INT NOT NULL,
                data_inicio DATETIME NOT NULL,
                data_fim DATETIME NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Confirmada',
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
                FOREIGN KEY (quarto_id) REFERENCES quartos(id) ON DELETE CASCADE
            )
        ''')
        
        # Inserir um usuário padrão para teste
        cur.execute("SELECT * FROM usuarios WHERE email = 'teste@teste.com'")
        if not cur.fetchone():
            print("Inserindo usuário padrão...")
            senha_hash = generate_password_hash('123456')
            cur.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
                ('Usuário Teste', 'teste@teste.com', senha_hash)
            )

        conn.commit()
        print('Tabelas criadas e usuário padrão inserido com sucesso.')

    except mysql.connector.Error as e:
        print(f'Erro ao criar tabelas ou inserir usuário: {e}')
    finally:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    criar_tabelas()
