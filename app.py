from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv
import os

from models import Usuario, Categoria, Produto, Movimento
from utils import validar_campos_obrigatorios, validar_email, verificar_enviar_alertas

load_dotenv()
app = Flask(__name__)
CORS(app, origins=['http://localhost:3000'])

SECRET_KEY = os.getenv("SECRET_KEY", "chave_padrao")

# ------------------------
# AUTENTICAÇÃO JWT
# ------------------------
def token_requerido(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'erro': 'Token ausente'}), 401
        try:
            token = token.replace("Bearer ", "")
            dados = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            usuario = Usuario.obter_por_id(dados['id'])
            if not usuario:
                raise Exception("Usuário não encontrado")
            return f(usuario, *args, **kwargs)
        except Exception as e:
            return jsonify({'erro': 'Token inválido', 'detalhes': str(e)}), 401
    return decorator

# ------------------------
# USUÁRIOS
# ------------------------
@app.route("/usuarios", methods=["POST"])
def criar_usuario():
    try:
        dados = request.json
        campos_obrigatorios = ["nome", "email", "senha"]
        valido, msg = validar_campos_obrigatorios(dados, campos_obrigatorios)
        if not valido:
            return jsonify({"erro": msg}), 400
        
        if not validar_email(dados['email']):
            return jsonify({"erro": "Email inválido"}), 400

        usuario = Usuario(nome=dados['nome'], email=dados['email'], senha=dados['senha'])
        usuario_id = usuario.salvar()
        return jsonify({"mensagem": "Usuário criado", "id": usuario_id}), 201
    except Exception as e:
        return jsonify({"erro": "Erro ao criar usuário", "detalhes": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        dados = request.json
        usuario = Usuario.autenticar(dados.get("email"), dados.get("senha"))
        if usuario:
            payload = {
                "id": usuario.id,
                "email": usuario.email,
                "nome": usuario.nome,
                "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return jsonify({"token": token})
        return jsonify({"erro": "Credenciais inválidas"}), 401
    except Exception as e:
        return jsonify({"erro": "Erro no login", "detalhes": str(e)}), 500

@app.route("/categorias", methods=["GET"])
@token_requerido
def listar_categorias(usuario):
    try:
        return jsonify(Categoria.listar())
    except Exception as e:
        return jsonify({"erro": "Erro ao listar categorias", "detalhes": str(e)}), 500

@app.route("/categorias", methods=["POST"])
@token_requerido
def criar_categoria(usuario):
    try:
        dados = request.json
        valido, msg = validar_campos_obrigatorios(dados, ["nome"])
        if not valido:
            return jsonify({"erro": msg}), 400
        
        categoria = Categoria(nome=dados['nome'], descricao=dados.get('descricao'))
        id_categoria = categoria.salvar()
        return jsonify({"mensagem": "Categoria criada", "id": id_categoria}), 201
    except Exception as e:
        return jsonify({"erro": "Erro ao criar categoria", "detalhes": str(e)}), 500

@app.route("/categorias/<int:id>", methods=["GET"])
@token_requerido
def obter_categoria(usuario, id):
    try:
        categoria = Categoria.obter_por_id(id)
        if not categoria:
            return jsonify({"erro": "Categoria não encontrada"}), 404
        return jsonify(vars(categoria))
    except Exception as e:
        return jsonify({"erro": "Erro ao obter categoria", "detalhes": str(e)}), 500

@app.route("/categorias/<int:id>", methods=["PUT"])
@token_requerido
def atualizar_categoria(usuario, id):
    try:
        dados = request.json
        categoria = Categoria.obter_por_id(id)
        if not categoria:
            return jsonify({"erro": "Categoria não encontrada"}), 404
        
        categoria.nome = dados.get("nome", categoria.nome)
        categoria.descricao = dados.get("descricao", categoria.descricao)
        categoria.salvar()
        return jsonify({"mensagem": "Categoria atualizada"})
    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar categoria", "detalhes": str(e)}), 500

@app.route("/categorias/<int:id>", methods=["DELETE"])
@token_requerido
def excluir_categoria(usuario, id):
    try:
        Categoria.excluir(id)
        return jsonify({"mensagem": "Categoria excluída"})
    except Exception as e:
        return jsonify({"erro": "Erro ao excluir categoria", "detalhes": str(e)}), 500

@app.route("/produtos", methods=["GET"])
@token_requerido
def listar_produtos(usuario):
    try:
        return jsonify(Produto.listar())
    except Exception as e:
        return jsonify({"erro": "Erro ao listar produtos", "detalhes": str(e)}), 500

@app.route("/produtos", methods=["POST"])
@token_requerido
def criar_produto(usuario):
    try:
        dados = request.json
        campos = ["nome", "descricao", "preco", "quantidade", "quantidade_minima", "categoria_id"]
        valido, msg = validar_campos_obrigatorios(dados, campos)
        if not valido:
            return jsonify({"erro": msg}), 400

        produto = Produto(**dados)
        id_produto = produto.salvar()
        return jsonify({"mensagem": "Produto criado", "id": id_produto}), 201
    except Exception as e:
        return jsonify({"erro": "Erro ao criar produto", "detalhes": str(e)}), 500

@app.route("/produtos/<int:id>", methods=["GET"])
@token_requerido
def obter_produto(usuario, id):
    try:
        produto = Produto.obter_por_id(id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404
        return jsonify(vars(produto))
    except Exception as e:
        return jsonify({"erro": "Erro ao obter produto", "detalhes": str(e)}), 500

@app.route("/produtos/<int:id>", methods=["PUT"])
@token_requerido
def atualizar_produto(usuario, id):
    try:
        produto = Produto.obter_por_id(id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404

        dados = request.json
        for campo in ["nome", "descricao", "preco", "quantidade", "quantidade_minima", "categoria_id"]:
            if campo in dados:
                setattr(produto, campo, dados[campo])
        
        produto.salvar()
        return jsonify({"mensagem": "Produto atualizado"})
    except Exception as e:
        return jsonify({"erro": "Erro ao atualizar produto", "detalhes": str(e)}), 500

@app.route("/produtos/<int:id>", methods=["DELETE"])
@token_requerido
def excluir_produto(usuario, id):
    try:
        Produto.excluir(id)
        return jsonify({"mensagem": "Produto excluído"})
    except Exception as e:
        return jsonify({"erro": "Erro ao excluir produto", "detalhes": str(e)}), 500

@app.route("/movimentos", methods=["POST"])
@token_requerido
def registrar_movimento(usuario):
    try:
        dados = request.json
        campos = ["produto_id", "tipo_movimento", "quantidade"]
        valido, msg = validar_campos_obrigatorios(dados, campos)
        if not valido:
            return jsonify({"erro": msg}), 400

        movimento = Movimento(
            produto_id=dados['produto_id'],
            usuario_id=usuario.id,
            tipo_movimento=dados['tipo_movimento'],
            quantidade=dados['quantidade'],
            observacao=dados.get('observacao')
        )

        movimento_id = movimento.salvar()

        if dados['tipo_movimento'] in ["saida", "ajuste"]:
            verificar_enviar_alertas(usuario.email)

        return jsonify({"mensagem": "Movimento registrado", "id": movimento_id}), 201
    except Exception as e:
        return jsonify({"erro": "Erro ao registrar movimento", "detalhes": str(e)}), 500
    
@app.route("/movimentos", methods=["GET"])
@token_requerido
def listar_todas_movimentacoes(usuario):
    try:
        tipo = request.args.get('tipo')       
        categoria_id = request.args.get('categoria_id') 
        data = request.args.get('data')                  
        
        movimentos = Movimento.listar_com_filtros(tipo_movimento=tipo, categoria_id=categoria_id, data=data)
        return jsonify(movimentos)
    except Exception as e:
        return jsonify({"erro": "Erro ao listar movimentações", "detalhes": str(e)}), 500


@app.route("/produtos/<int:id>/movimentos", methods=["GET"])
@token_requerido
def listar_movimentos(usuario, id):
    try:
        movimentos = Movimento.listar_por_produto(id)
        return jsonify(movimentos)
    except Exception as e:
        return jsonify({"erro": "Erro ao listar movimentos", "detalhes": str(e)}), 500


# ------------------------
# INICIAR A API
# ------------------------
if __name__ == "__main__":
    porta = int(os.getenv("API_PORT", 5000))
    app.run(debug=True, port=porta)
