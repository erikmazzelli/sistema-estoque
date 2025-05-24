# models.py
from database import Database
import bcrypt
import datetime

class Usuario:
    def __init__(self, id=None, nome=None, email=None, senha=None, nivel_acesso='usuario'):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.nivel_acesso = nivel_acesso
    
    def salvar(self):
        """Cria ou atualiza um usuário no banco de dados"""
        # Criptografar a senha
        senha_hash = bcrypt.hashpw(self.senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if self.id:
            # Atualizar usuário existente
            query = """
                UPDATE usuarios 
                SET nome = %s, email = %s, senha = %s, nivel_acesso = %s 
                WHERE id = %s
            """
            params = (self.nome, self.email, senha_hash, self.nivel_acesso, self.id)
        else:
            # Criar novo usuário
            query = """
                INSERT INTO usuarios (nome, email, senha, nivel_acesso)
                VALUES (%s, %s, %s, %s)
            """
            params = (self.nome, self.email, senha_hash, self.nivel_acesso)
        
        return Database.execute_query(query, params)
    
    @staticmethod
    def autenticar(email, senha):
        """Autentica um usuário"""
        query = "SELECT * FROM usuarios WHERE email = %s"
        result = Database.execute_query(query, (email,), fetch=True)
        
        if result and len(result) > 0:
            usuario = result[0]
            if bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
                return Usuario(
                    id=usuario['id'],
                    nome=usuario['nome'],
                    email=usuario['email'],
                    nivel_acesso=usuario['nivel_acesso']
                )
        return None
    
    @staticmethod
    def obter_por_id(id):
        """Retorna um usuário pelo ID"""
        query = "SELECT * FROM usuarios WHERE id = %s"
        result = Database.execute_query(query, (id,), fetch=True)
        if result and len(result) > 0:
            u = result[0]
            return Usuario(id=u['id'], nome=u['nome'], email=u['email'], nivel_acesso=u['nivel_acesso'])
        return None


class Categoria:
    def __init__(self, id=None, nome=None, descricao=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
    
    def salvar(self):
        """Cria ou atualiza uma categoria no banco de dados"""
        if self.id:
            # Atualizar categoria existente
            query = """
                UPDATE categorias 
                SET nome = %s, descricao = %s 
                WHERE id = %s
            """
            params = (self.nome, self.descricao, self.id)
        else:
            # Criar nova categoria
            query = """
                INSERT INTO categorias (nome, descricao)
                VALUES (%s, %s)
            """
            params = (self.nome, self.descricao)
        
        return Database.execute_query(query, params)
    
    @staticmethod
    def listar():
        """Retorna todas as categorias"""
        query = "SELECT * FROM categorias ORDER BY nome"
        return Database.execute_query(query, fetch=True)
    
    @staticmethod
    def obter_por_id(id):
        """Retorna uma categoria pelo ID"""
        query = "SELECT * FROM categorias WHERE id = %s"
        result = Database.execute_query(query, (id,), fetch=True)
        if result and len(result) > 0:
            c = result[0]
            return Categoria(id=c['id'], nome=c['nome'], descricao=c['descricao'])
        return None
    
    @staticmethod
    def excluir(id):
        """Exclui uma categoria pelo ID"""
        query = "DELETE FROM categorias WHERE id = %s"
        return Database.execute_query(query, (id,))


class Produto:
    def __init__(self, id=None, nome=None, descricao=None, preco=0, quantidade=0, 
                 quantidade_minima=5, categoria_id=None):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.preco = preco
        self.quantidade = quantidade
        self.quantidade_minima = quantidade_minima
        self.categoria_id = categoria_id
    
    def salvar(self):
        """Cria ou atualiza um produto no banco de dados"""
        if self.id:
            # Atualizar produto existente
            query = """
                UPDATE produtos 
                SET nome = %s, descricao = %s, preco = %s, quantidade = %s,
                    quantidade_minima = %s, categoria_id = %s
                WHERE id = %s
            """
            params = (self.nome, self.descricao, self.preco, self.quantidade,
                     self.quantidade_minima, self.categoria_id, self.id)
        else:
            # Criar novo produto
            query = """
                INSERT INTO produtos (nome, descricao, preco, quantidade, 
                                     quantidade_minima, categoria_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (self.nome, self.descricao, self.preco, self.quantidade,
                     self.quantidade_minima, self.categoria_id)
        
        return Database.execute_query(query, params)
    
    @staticmethod
    def listar():
        """Retorna todos os produtos"""
        query = """
            SELECT p.*, c.nome as categoria_nome
            FROM produtos p
            JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.nome
        """
        return Database.execute_query(query, fetch=True)
    
    @staticmethod
    def obter_por_id(id):
        """Retorna um produto pelo ID"""
        query = """
            SELECT p.*, c.nome as categoria_nome
            FROM produtos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE p.id = %s
        """
        result = Database.execute_query(query, (id,), fetch=True)
        if result and len(result) > 0:
            p = result[0]
            return Produto(
                id=p['id'], 
                nome=p['nome'], 
                descricao=p['descricao'],
                preco=p['preco'],
                quantidade=p['quantidade'],
                quantidade_minima=p['quantidade_minima'],
                categoria_id=p['categoria_id']
            )
        return None
    
    @staticmethod
    def excluir(id):
        """Exclui um produto pelo ID"""
        query = "DELETE FROM produtos WHERE id = %s"
        return Database.execute_query(query, (id,))
    
    @staticmethod
    def produtos_com_estoque_baixo():
        """Retorna produtos com estoque abaixo do mínimo"""
        query = """
            SELECT p.*, c.nome as categoria_nome
            FROM produtos p
            JOIN categorias c ON p.categoria_id = c.id
            WHERE p.quantidade < p.quantidade_minima
        """
        return Database.execute_query(query, fetch=True)


class Movimento:
    def __init__(self, id=None, produto_id=None, usuario_id=None, 
                 tipo_movimento=None, quantidade=0, observacao=None):
        self.id = id
        self.produto_id = produto_id
        self.usuario_id = usuario_id
        self.tipo_movimento = tipo_movimento
        self.quantidade = quantidade
        self.observacao = observacao
    
    def salvar(self):
        """Registra um movimento de estoque e atualiza o produto"""
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Inicia uma transação
            conn.start_transaction()
            
            # 1. Registra o movimento
            query = """
                INSERT INTO movimentos_estoque 
                (produto_id, usuario_id, tipo_movimento, quantidade, observacao)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (self.produto_id, self.usuario_id, self.tipo_movimento, 
                     self.quantidade, self.observacao)
            
            cursor.execute(query, params)
            
            # 2. Atualiza o estoque do produto
            if self.tipo_movimento == 'entrada':
                query = """
                    UPDATE produtos
                    SET quantidade = quantidade + %s
                    WHERE id = %s
                """
            elif self.tipo_movimento == 'saida':
                query = """
                    UPDATE produtos
                    SET quantidade = quantidade - %s
                    WHERE id = %s
                """
            else:  # ajuste
                query = """
                    UPDATE produtos
                    SET quantidade = %s
                    WHERE id = %s
                """
            
            cursor.execute(query, (self.quantidade, self.produto_id))
            
            # Confirma a transação
            conn.commit()
            return cursor.lastrowid
            
        except Exception as e:
            conn.rollback()
            print(f"Erro ao registrar movimento: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_todos():
        query = """
            SELECT m.*, u.nome as usuario_nome, p.nome as produto_nome
            FROM movimentos_estoque m
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            LEFT JOIN produtos p ON m.produto_id = p.id
            ORDER BY m.data_movimento DESC
        """
        return Database.execute_query(query, fetch=True)

    @staticmethod
    def listar_com_filtros(tipo_movimento=None, categoria_id=None, data=None):
        query = """
            SELECT m.*, u.nome as usuario_nome, p.nome as produto_nome, p.categoria_id
            FROM movimentos_estoque m
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            LEFT JOIN produtos p ON m.produto_id = p.id
            WHERE 1=1
        """
        params = []

        if tipo_movimento:
            query += " AND m.tipo_movimento = %s"
            params.append(tipo_movimento)

        if categoria_id:
            query += " AND p.categoria_id = %s"
            params.append(categoria_id)

        if data:
            # Aqui usamos DATE(m.data_movimento) para comparar só a parte da data, ignorando hora
            query += " AND DATE(m.data_movimento) = %s"
            params.append(data)  # Espera string no formato 'YYYY-MM-DD'

        query += " ORDER BY m.data_movimento DESC"

        return Database.execute_query(query, tuple(params), fetch=True)


    
    @staticmethod
    def listar_por_produto(produto_id):
        """Retorna todos os movimentos de um produto"""
        query = """
            SELECT m.*, u.nome as usuario_nome
            FROM movimentos_estoque m
            LEFT JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.produto_id = %s
            ORDER BY m.data_movimento DESC
        """
        return Database.execute_query(query, (produto_id,), fetch=True)