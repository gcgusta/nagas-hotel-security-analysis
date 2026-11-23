from config import obter_conexao

def get_connection():
    """Retorna uma conexão ativa com o banco de dados."""
    return obter_conexao()
