# utils.py
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Funções de validação
def validar_email(email):
    """Valida se o email está em formato correto"""
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(padrao, email))

def validar_preco(preco):
    """Valida se o preço é um valor positivo"""
    try:
        valor = float(preco)
        return valor >= 0
    except:
        return False

def validar_quantidade(quantidade):
    """Valida se a quantidade é um número inteiro positivo"""
    try:
        valor = int(quantidade)
        return valor >= 0
    except:
        return False

def validar_campos_obrigatorios(dados, campos):
    """
    Valida se todos os campos obrigatórios estão preenchidos
    
    Args:
        dados (dict): Dicionário com os dados a serem validados
        campos (list): Lista de campos obrigatórios
        
    Returns:
        tuple: (válido, mensagem de erro)
    """
    for campo in campos:
        if campo not in dados or dados[campo] is None or dados[campo] == "":
            return False, f"Campo obrigatório não preenchido: {campo}"
    
    return True, "Dados válidos"

# Funções para envio de email
def enviar_email(destinatario, assunto, mensagem):
    """
    Envia um email usando as configurações do arquivo .env
    
    Args:
        destinatario (str): Email do destinatário
        assunto (str): Assunto do email
        mensagem (str): Corpo do email (pode conter HTML)
        
    Returns:
        bool: True se o email foi enviado com sucesso, False caso contrário
    """
    # Verificar se as configurações de email estão disponíveis
    email_host = os.getenv("EMAIL_HOST")
    email_port = os.getenv("EMAIL_PORT")
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")

    print('pqp', {email_host, email_port, email_user, email_password})
    
    if not all([email_host, email_port, email_user, email_password]):
        print("Configurações de email incompletas. Verifique o arquivo .env")
        return False
    
    # Criar mensagem
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = destinatario
    msg['Subject'] = assunto
    
    # Adicionar corpo da mensagem
    msg.attach(MIMEText(mensagem, 'html'))
    
    try:
        # Conectar ao servidor SMTP
        server = smtplib.SMTP(email_host, int(email_port))
        server.starttls()  # Iniciar conexão segura
        server.login(email_user, email_password)
        
        # Enviar email
        server.send_message(msg)
        server.quit()
        print(f"Email enviado com sucesso para {destinatario}")
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

def alertar_estoque_baixo(produto, usuario_email):
    """
    Envia um email de alerta quando o estoque está abaixo do mínimo
    
    Args:
        produto (dict): Dados do produto com estoque baixo
        usuario_email (str): Email do usuário que receberá o alerta
    """
    assunto = f"ALERTA: Estoque baixo do produto {produto['nome']}"
    
    mensagem = f"""
    <html>
    <body>
        <h2>Alerta de Estoque Baixo</h2>
        <p>O produto <strong>{produto['nome']}</strong> está com estoque baixo!</p>
        
        <h3>Detalhes do Produto:</h3>
        <ul>
            <li><strong>ID:</strong> {produto['id']}</li>
            <li><strong>Nome:</strong> {produto['nome']}</li>
            <li><strong>Categoria:</strong> {produto.get('categoria_nome', 'N/A')}</li>
            <li><strong>Quantidade Atual:</strong> {produto['quantidade']}</li>
            <li><strong>Quantidade Mínima:</strong> {produto['quantidade_minima']}</li>
        </ul>
        
        <p>Por favor, verifique e reponha o estoque quando possível.</p>
    </body>
    </html>
    """
    
    return enviar_email(usuario_email, assunto, mensagem)

def verificar_enviar_alertas(usuario_email):
    """
    Verifica produtos com estoque baixo e envia alertas
    
    Args:
        usuario_email (str): Email do usuário que receberá os alertas
    """
    from models import Produto
    
    produtos_baixos = Produto.produtos_com_estoque_baixo()
    
    if not produtos_baixos:
        print("Nenhum produto com estoque baixo encontrado")
        return
    
    for produto in produtos_baixos:
        alertar_estoque_baixo(produto, usuario_email)