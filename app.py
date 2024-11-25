
#region: Requirements

from flask import Flask, render_template, request, redirect, flash, url_for, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from functools import wraps
import webview
import tkinter as tk  # Para pegar o tamanho da tela
import os

# Instalação de bibliotecas necessárias:
# Execute 'pip install -r requirements.txt' para instalar todas as bibliotecas listadas no arquivo.
# Execute 'pip freeze' para verificar as bibliotecas instaladas. Caso alguma esteja faltando, instale-a com 'pip install <nome_da_biblioteca>'.

#endregion

#region: Configuração inicial do aplicativo


# Configura o caminho estático para servir arquivos corretamente
static_folder_path = os.path.join(os.getcwd(), 'static')
app = Flask(__name__, static_folder=static_folder_path)

# Servir arquivos estáticos diretamente no modo desktop
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(static_folder_path, filename)

# Configuração da chave secreta para sessões e criptografia
app.config['SECRET_KEY'] = 'secreto'

# Configurando a conexão com o banco para o SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://sqlserver:sqlserver@fazendaurbanalotusdb.c7wqk0i0qbea.us-east-1.rds.amazonaws.com/lotus?driver=ODBC+Driver+17+for+SQL+Server'
)
print("Conexão bem-sucedida!")

# Inicializando o banco de dados e Bcrypt
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


# Lista de rotas que não exigem login (acesso livre)
rotas_livres = ['/', '/login']

# Função que é executada antes de cada requisição para verificar o login
@app.before_request
def check_login():
    # Verifica se a rota atual exige login e se o usuário não está autenticado
    if request.path not in rotas_livres and 'user_id' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))  # Redireciona para a página de login se o usuário não estiver logado

# Rota principal do aplicativo (homepage)
@app.route('/')
def index():
    # Renderiza a página inicial
    return render_template('index.html')

# Decorador para verificar o acesso do usuário a áreas restritas com base em setores permitidos
def verificar_acesso(setores_permitidos):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            usuario_setor = session.get('setor')  # Obtém o setor do usuário da sessão
            if usuario_setor not in setores_permitidos:
                flash("Você não tem acesso a essa área, contate seu administrador", "danger")
                # Redireciona para uma página de erro ou página inicial caso o setor não esteja autorizado
                return redirect(url_for('pagina_erro'))  
            return func(*args, **kwargs)
        return wrapper
    return decorator

#endregion

#region: Test

@app.route('/saudacao/<nome>')
def saudacao(nome):
    """
    Função que retorna uma saudação personalizada.
    Exemplo de URL: /saudacao/Joao
    """
    return jsonify(mensagem=f"Olá, {nome}!")

#endregion:

#region: Colaboradores

class Colaborador(db.Model):
    __tablename__ = 'Colaborador'  # Define o nome da tabela no banco de dados como 'Colaborador'
    
    # Campos da tabela Colaborador, com tipos e restrições
    id = db.Column('id_Colaborador', db.Integer, primary_key=True, nullable=False)  # ID único de cada colaborador
    nome = db.Column('nome_Colaborador', db.String(100), nullable=False)  # Nome do colaborador
    email = db.Column('email_Colaborador', db.String(120), unique=True, nullable=False)  # E-mail exclusivo
    setor = db.Column('setor_Colaborador', db.String(50), nullable=False)  # Setor onde o colaborador trabalha
    usuario = db.Column('usuario_Colaborador', db.String(50), unique=True, nullable=False)  # Nome de usuário exclusivo
    senha = db.Column('senha_Colaborador', db.String(128), nullable=False)  # Senha armazenada com criptografia

    # Relação de pedidos (comentada no momento)
    # pedidos = db.relationship('Pedido', backref='colaborador', lazy=True)


# Rota para exibir todos os colaboradores, restrita aos setores de RH e Administrador
@app.route('/colaborador')
@verificar_acesso(['Recursos humanos', 'Administrador'])
def colaborador():
    # Consulta todos os colaboradores no banco de dados
    colaboradores = Colaborador.query.all()
    return render_template('colaborador/Colaborador.html', colaboradores=colaboradores)


# Rota para adicionar um novo colaborador
@app.route('/adicionar_colaborador', methods=['GET', 'POST'])
def adicionar_colaborador():
    if request.method == 'POST':
        # Coleta dados do formulário
        nome = request.form['nome']
        email = request.form['email']
        setor = request.form['setor']
        usuario = request.form['usuario']
        senha = request.form['senha']

        # Validação básica para verificar se todos os campos foram preenchidos
        if not nome or not email or not usuario or not senha:
            flash('Por favor, preencha todos os campos.')
            return redirect('/adicionar_colaborador')  # Redireciona para o formulário caso haja campos vazios

        # Criptografa a senha fornecida
        senha_criptografada = bcrypt.generate_password_hash(senha).decode('utf-8')

        # Cria um novo objeto Colaborador e adiciona ao banco de dados
        novo_colaborador = Colaborador(nome=nome, email=email, setor=setor, usuario=usuario, senha=senha_criptografada)
        db.session.add(novo_colaborador)
        db.session.commit()

        flash('Colaborador adicionado com sucesso!')
        return redirect('/colaborador')  # Redireciona para a página de colaboradores após adição


# Rota para editar um colaborador existente
@app.route('/editar_colaborador/<int:colaborador_id>', methods=['GET', 'POST'])
def editar_colaborador(colaborador_id):
    # Busca o colaborador pelo ID
    colaborador = Colaborador.query.get_or_404(colaborador_id)
    if request.method == 'POST':
        # Atualiza os dados do colaborador com as informações do formulário
        colaborador.nome = request.form['nome']
        colaborador.email = request.form['email']
        db.session.commit()  # Salva as alterações no banco de dados
        flash('Colaborador atualizado com sucesso!')  # Mensagem de sucesso
        return redirect(url_for('colaborador'))  # Redireciona para a página de colaboradores

    # Renderiza o formulário de edição com os dados atuais do colaborador
    return render_template('colaborador/item_Colaborador.html', colaborador=colaborador)


# Rota para excluir um colaborador
@app.route('/excluir_colaborador/<int:colaborador_id>', methods=['POST'])
def excluir_colaborador(colaborador_id):
    # Busca o colaborador pelo ID
    colaborador = Colaborador.query.get_or_404(colaborador_id)

    # Verifica se o colaborador é administrador, impedindo sua exclusão
    if colaborador.setor == 'Administrador':
        flash('Não é possível excluir um administrador.', 'danger')
        return redirect(url_for('colaborador'))

    # Exclui o colaborador do banco de dados
    db.session.delete(colaborador)
    db.session.commit()
    flash('Colaborador excluído com sucesso!', 'success')
    return redirect(url_for('colaborador'))  # Redireciona para a página de colaboradores


# Rota para pesquisar colaboradores pelo nome
@app.route('/pesquisar_colaborador', methods=['GET'])
def pesquisar_colaborador():
    # Obtém o nome do colaborador da barra de pesquisa
    nome = request.args.get('nome', '').strip()
    if nome:
        # Filtra colaboradores cujo nome contém a string pesquisada
        colaboradores = Colaborador.query.filter(Colaborador.nome.like(f"%{nome}%")).all()
    else:
        # Se o campo de pesquisa estiver vazio, exibe todos os colaboradores
        colaboradores = Colaborador.query.all()
    return render_template('colaborador/Colaborador.html', colaboradores=colaboradores)


# Rota para alteração de senha do colaborador logado
@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    usuario_id = session.get('user_id')  # Obtém o ID do usuário logado
    colaborador = Colaborador.query.get(usuario_id)  # Busca o colaborador pelo ID

    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']

        # Verifica se a senha atual está correta
        if bcrypt.check_password_hash(colaborador.senha, senha_atual):
            # Criptografa a nova senha e atualiza no banco de dados
            nova_senha_criptografada = bcrypt.generate_password_hash(nova_senha).decode('utf-8')
            colaborador.senha = nova_senha_criptografada
            db.session.commit()  # Salva as alterações
            flash('Senha alterada com sucesso!', 'success_alterar_senha')  # Mensagem de sucesso
        else:
            flash('Senha atual incorreta. Tente novamente.', 'danger_alterar_senha')  # Mensagem de erro

    # Renderiza a página de alteração de senha
    return render_template('configuracoes/alterarSenha.html', colaborador=colaborador)




#endregion

#region: Producao


# Define a classe 'Producao' representando a tabela de produção no banco de dados
class Producao(db.Model):
    __tablename__ = 'Producao'
    id = db.Column('id_Producao', db.Integer, primary_key=True, nullable=False)  # Chave primária da produção
    nome = db.Column('nome_Producao', db.String(100), nullable=True)  # Nome do item produzido
    fornecedor = db.Column('fornecedor_Producao', db.String(100), nullable=True)  # Nome do fornecedor do item
    quantidade = db.Column('quantidade_Producao', db.Integer, nullable=True)  # Quantidade do item
    data = db.Column('data_Producao', db.Date, nullable=True)  # Data de produção
    preco = db.Column('preco_Producao', db.Float, nullable=True)  # Preço por unidade do item produzido

    # Define uma relação com a tabela 'Pedido', caso necessário (atualmente comentado)
    #pedidos = db.relationship('Pedido', backref='produto', lazy=True)    


# Rota para exibir a página de produção com lista de itens
@app.route('/producao')  
@verificar_acesso(['Producao', 'Administrador'])  # Verifica o acesso de setores específicos
def producao():
    producoes = Producao.query.all()  # Consulta todos os itens de produção
    return render_template('producao/Producao.html', producoes=producoes)  # Renderiza a página com os itens


# Rota para adicionar um novo item à produção
@app.route('/adicionar_producao', methods=['GET', 'POST'])  
def adicionar_producao():  
    if request.method == 'POST':
        # Coleta os dados do formulário
        nome = request.form['nome']
        fornecedor = request.form['fornecedor']
        quantidade = request.form['quantidade']
        data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()  # Converte a data para o formato Date
        preco = request.form['preco']

        # Verifica se todos os campos foram preenchidos
        if not nome or not fornecedor or not quantidade or not data or not preco:
            flash('Por favor, preencha todos os campos.')  # Alerta para preencher todos os campos
            return redirect('/adicionar_producao')  # Redireciona para o formulário

        # Cria uma nova instância de 'Producao' com os dados informados
        nova_producao = Producao(
            nome=nome,
            fornecedor=fornecedor,
            quantidade=quantidade,
            data=data,
            preco=preco
        )
        db.session.add(nova_producao)  # Adiciona o item ao banco de dados
        db.session.commit()  # Salva as alterações

        flash('Produção adicionada com sucesso!')  # Mensagem de sucesso
        return redirect('/producao')  # Redireciona para a lista de produções


# Rota para editar um item de produção existente
@app.route('/editar_producao/<int:producao_id>', methods=['POST'])
def editar_producao(producao_id):
    producao = Producao.query.get_or_404(producao_id)  # Busca o item de produção pelo ID
    if request.method == 'POST':
        # Atualiza os campos com os novos dados do formulário
        producao.nome = request.form['nome']
        producao.fornecedor = request.form['fornecedor']
        producao.quantidade = request.form['quantidade']
        producao.data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
        producao.preco = request.form['preco']
        db.session.commit()  # Salva as alterações
        return redirect(url_for('producao', producao_id=producao.id))  # Redireciona para a lista de produções


# Rota para excluir um item de produção
@app.route('/excluir_producao/<int:producao_id>', methods=['POST'])
def excluir_producao(producao_id):
    try:
        producao = Producao.query.get_or_404(producao_id)  # Busca o item de produção pelo ID
        print(f'Tentando excluir a produção: {producao}')  # Mensagem de debug para o console
        db.session.delete(producao)  # Exclui o item do banco de dados
        db.session.commit()  # Salva as alterações
        flash('Produção excluída com sucesso!', 'success')  # Mensagem de sucesso ao excluir
    except Exception as e:
        print(f'Erro ao excluir produção: {e}')  # Exibe o erro no console para debug
        flash(f'Ocorreu um erro ao excluir a produção: {e}', 'danger')  # Exibe mensagem de erro ao usuário
    return redirect(url_for('producao'))  # Redireciona para a lista de produções


# Rota para pesquisar itens de produção pelo nome
@app.route('/pesquisar_producao', methods=['GET'])
def pesquisar_producao():
    nome = request.args.get('nome', '').strip()  # Obtém o termo de busca e remove espaços extras
    if nome:
        # Filtra os itens de produção que contêm o termo de busca no nome
        producoes = Producao.query.filter(Producao.nome.like(f"%{nome}%")).all()
    else:
        producoes = Producao.query.all()  # Se não houver busca, exibe todos os itens
    return render_template('producao/Producao.html', producoes=producoes)  # Renderiza a página com os resultados


#endregion

#region: Fornecedor

# Definindo a classe Fornecedor que representa a tabela 'Fornecedor' no banco de dados
class Fornecedor(db.Model):
    __tablename__ = 'Fornecedor'  # Nome da tabela no banco de dados
    id = db.Column('id_Fornecedor', db.Integer, primary_key=True, nullable=False)  # Coluna ID como chave primária
    nome = db.Column('nome_Fornecedor', db.String(100), nullable=False)  # Nome do fornecedor, campo obrigatório
    endereco = db.Column('endereco_Fornecedor', db.String(200), nullable=True)  # Endereço do fornecedor, opcional
    cnpj_pf = db.Column('cnpj_pf_Fornecedor', db.String(18), nullable=True)  # CNPJ ou CPF, opcional
    contato = db.Column('contato_Fornecedor', db.String(100), nullable=True)  # Informações de contato, opcional
    email = db.Column('email_Fornecedor', db.String(100), nullable=True)  # Email do fornecedor, opcional

    # Relacionamento com pedidos (comentado por enquanto)
    # pedidos = db.relationship('Pedido', backref='fornecedor', lazy=True)

# Rota para listar fornecedores, acessível para setores específicos
@app.route('/fornecedores')
@verificar_acesso(['Vendas', 'Administrador'])
def fornecedores():
    fornecedores = Fornecedor.query.all()  # Consulta todos os fornecedores
    return render_template('fornecedor/Fornecedor.html', fornecedores=fornecedores)  # Renderiza o template

# Rota para adicionar um novo fornecedor
@app.route('/adicionar_fornecedor', methods=['GET', 'POST'])
def adicionar_fornecedor():
    if request.method == 'POST':  # Verifica se o método é POST para receber dados do formulário
        nome = request.form['nome']  # Captura o nome do formulário
        endereco = request.form['endereco']
        cnpj_pf = request.form['cnpj_pf']
        contato = request.form['contato']
        email = request.form['email']

        # Validação para garantir que o nome foi preenchido
        if not nome:
            flash('Por favor, preencha o nome do fornecedor.')
            return redirect('/adicionar_fornecedor')

        # Cria uma nova instância de fornecedor com os dados recebidos
        novo_fornecedor = Fornecedor(
            nome=nome,
            endereco=endereco,
            cnpj_pf=cnpj_pf,
            contato=contato,
            email=email
        )
        db.session.add(novo_fornecedor)  # Adiciona o novo fornecedor à sessão do banco de dados
        db.session.commit()  # Confirma a inclusão no banco
        flash('Fornecedor adicionado com sucesso!')
        return redirect('/fornecedores')  # Redireciona para a lista de fornecedores

# Rota para editar um fornecedor existente
@app.route('/editar_fornecedor/<int:fornecedor_id>', methods=['POST'])
def editar_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get_or_404(fornecedor_id)  # Consulta o fornecedor pelo ID ou retorna 404 se não encontrado
    if request.method == 'POST':  # Recebe os dados de atualização
        fornecedor.nome = request.form['nome']
        fornecedor.endereco = request.form['endereco']
        fornecedor.cnpj_pf = request.form['cnpj_pf']
        fornecedor.contato = request.form['contato']
        fornecedor.email = request.form['email']
        db.session.commit()  # Salva as alterações no banco de dados
        flash('Fornecedor atualizado com sucesso!')
        return redirect(url_for('fornecedores', fornecedor_id=fornecedor.id))

# Rota para excluir um fornecedor existente
@app.route('/excluir_fornecedor/<int:fornecedor_id>', methods=['POST'])
def excluir_fornecedor(fornecedor_id):
    try:
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id)  # Obtém o fornecedor pelo ID
        db.session.delete(fornecedor)  # Remove o fornecedor do banco de dados
        db.session.commit()  # Confirma a exclusão
        flash('Fornecedor excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Ocorreu um erro ao excluir o fornecedor: {e}', 'danger')  # Em caso de erro, exibe uma mensagem
    return redirect(url_for('fornecedores'))  # Redireciona para a lista de fornecedores

# Rota para pesquisar fornecedores pelo nome
@app.route('/pesquisar_fornecedor', methods=['GET'])
def pesquisar_fornecedor():
    nome = request.args.get('nome', '').strip()  # Captura o nome do fornecedor da pesquisa
    if nome:
        fornecedores = Fornecedor.query.filter(Fornecedor.nome.like(f"%{nome}%")).all()  # Filtra pelo nome
    else:
        fornecedores = Fornecedor.query.all()  # Se não houver nome, retorna todos os fornecedores
    return render_template('fornecedor/Fornecedor.html', fornecedores=fornecedores)  # Renderiza a página com os resultados



#endregion

#region: Cliente
# Definindo a classe Cliente que representa a tabela 'Cliente' no banco de dados
class Cliente(db.Model):
    __tablename__ = 'Cliente'  # Define o nome da tabela no banco de dados
    id = db.Column('id_Cliente', db.Integer, primary_key=True, nullable=False)  # Coluna ID como chave primária
    nome = db.Column('nome_Cliente', db.String(100), nullable=False)  # Nome do cliente, campo obrigatório
    endereco = db.Column('endereco_Cliente', db.String(200), nullable=True)  # Endereço do cliente, opcional
    cnpj_pf = db.Column('cnpj_pf_Cliente', db.String(18), nullable=True)  # CNPJ ou CPF, opcional
    contato = db.Column('contato_Cliente', db.String(100), nullable=True)  # Informações de contato, opcional
    email = db.Column('email_Cliente', db.String(100), nullable=True)  # Email do cliente, opcional

    # Relacionamento com pedidos (comentado por enquanto)
    # pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

# Rota para listar clientes, acessível para setores específicos
@app.route('/clientes')
@verificar_acesso(['Vendas', 'Administrador'])
def clientes():
    clientes = Cliente.query.all()  # Consulta todos os clientes
    return render_template('clientes/Clientes.html', clientes=clientes)  # Renderiza o template com a lista de clientes

# Rota para adicionar um novo cliente
@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    if request.method == 'POST':  # Verifica se o método é POST para receber dados do formulário
        nome = request.form['nome']  # Captura o nome do formulário
        endereco = request.form['endereco']
        cnpj_pf = request.form['cnpj_pf']
        contato = request.form['contato']
        email = request.form['email']

        # Validação para garantir que o nome foi preenchido
        if not nome:
            flash('Por favor, preencha o nome do cliente.')
            return redirect('/adicionar_cliente')

        # Cria uma nova instância de cliente com os dados recebidos
        novo_cliente = Cliente(
            nome=nome,
            endereco=endereco,
            cnpj_pf=cnpj_pf,
            contato=contato,
            email=email
        )
        db.session.add(novo_cliente)  # Adiciona o novo cliente à sessão do banco de dados
        db.session.commit()  # Confirma a inclusão no banco
        flash('Cliente adicionado com sucesso!')
        return redirect('/clientes')  # Redireciona para a lista de clientes

# Rota para editar um cliente existente
@app.route('/editar_cliente/<int:cliente_id>', methods=['POST'])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)  # Consulta o cliente pelo ID ou retorna 404 se não encontrado
    if request.method == 'POST':  # Recebe os dados de atualização
        cliente.nome = request.form['nome']
        cliente.endereco = request.form['endereco']
        cliente.cnpj_pf = request.form['cnpj_pf']
        cliente.contato = request.form['contato']
        cliente.email = request.form['email']
        db.session.commit()  # Salva as alterações no banco de dados
        flash('Cliente atualizado com sucesso!')
        return redirect(url_for('clientes', cliente_id=cliente.id))

# Rota para excluir um cliente existente
@app.route('/excluir_cliente/<int:cliente_id>', methods=['POST'])
def excluir_cliente(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)  # Obtém o cliente pelo ID
        db.session.delete(cliente)  # Remove o cliente do banco de dados
        db.session.commit()  # Confirma a exclusão
        flash('Cliente excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Ocorreu um erro ao excluir o cliente: {e}', 'danger')  # Em caso de erro, exibe uma mensagem
    return redirect(url_for('clientes'))  # Redireciona para a lista de clientes

# Rota para pesquisar clientes pelo nome
@app.route('/pesquisar_cliente', methods=['GET'])
def pesquisar_cliente():
    nome = request.args.get('nome', '').strip()  # Captura o nome do cliente da pesquisa
    if nome:
        clientes = Cliente.query.filter(Cliente.nome.like(f"%{nome}%")).all()  # Filtra pelo nome
    else:
        clientes = Cliente.query.all()  # Se não houver nome, retorna todos os clientes
    return render_template('clientes/Clientes.html', clientes=clientes)  # Renderiza a página com os resultados



#endregion

#region: Pedido

class Pedido(db.Model):
    __tablename__ = 'Pedido'  # Define o nome da tabela como 'Pedido'
    id = db.Column('id_Pedido', db.Integer, primary_key=True, nullable=False)  # ID do pedido, chave primária
    tipo = db.Column('tipo_Pedido', db.String(20), nullable=False)  # Tipo do pedido ('recebimento' ou 'venda')
    quantidade = db.Column('quantidade_Pedido', db.Integer, nullable=False)  # Quantidade do produto no pedido
    total = db.Column('total_Pedido', db.Float, nullable=False)  # Total do pedido, calculado no sistema
    data = db.Column('data_Pedido', db.Date, nullable=False)  # Data do pedido

    # Chaves estrangeiras
    colaborador_id = db.Column(db.Integer, db.ForeignKey('Colaborador.id_Colaborador'), nullable=False)  # ID do colaborador
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('Fornecedor.id_Fornecedor'), nullable=True)  # ID do fornecedor (para recebimento)
    cliente_id = db.Column(db.Integer, db.ForeignKey('Cliente.id_Cliente'), nullable=True)  # ID do cliente (para venda)
    produto_id = db.Column(db.Integer, db.ForeignKey('Producao.id_Producao'), nullable=False)  # ID do produto

    # Relacionamentos
    colaborador = db.relationship('Colaborador', backref='pedidos_colaborador', lazy=True)  # Relacionamento com Colaborador
    fornecedor = db.relationship('Fornecedor', backref='pedidos', lazy=True)  # Relacionamento com Fornecedor
    cliente = db.relationship('Cliente', backref='pedidos', lazy=True)  # Relacionamento com Cliente
    produto = db.relationship('Producao', backref='pedidos', lazy=True)  # Relacionamento com Produto

    def __init__(self, tipo, colaborador_id, produto_id, quantidade, data=None, fornecedor_id=None, cliente_id=None):
        # Inicializa o pedido com dados fornecidos
        self.tipo = tipo
        self.colaborador_id = colaborador_id
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.data = data if data else db.func.current_date()  # Usa a data atual se não fornecido
        self.fornecedor_id = fornecedor_id
        self.cliente_id = cliente_id

        # Verifica a quantidade disponível no estoque
        if not self.verificar_quantidade_disponivel():
            raise ValueError("Quantidade solicitada maior do que a quantidade disponível no estoque.")
        
        self.total = self.calcular_total()  # Calcula o total do pedido

    def verificar_quantidade_disponivel(self):
        # Verifica se a quantidade disponível do produto é suficiente para o pedido
        produto = Producao.query.get(self.produto_id)
        if produto and int(produto.quantidade) >= int(self.quantidade):
            return True
        return False

    def calcular_total(self):
        # Calcula o total com base no preço do produto
        produto = Producao.query.get(self.produto_id)
        if produto:
            return self.quantidade * float(produto.preco)
        return 0.0  # Retorna 0 se o produto não existir

@app.route('/pedido')
def pedido():
    pedidos = Pedido.query.all()  # Obtém todos os pedidos
    return render_template('pedido/Pedido.html', pedidos=pedidos)  # Renderiza a lista de pedidos


@app.route('/adicionar_pedido', methods=['GET', 'POST'])
def adicionar_pedido():
    if request.method == 'POST':
        # Obtém os dados do formulário
        tipo_pedido = request.form['tipo_pedido']
        fornecedor_id = request.form.get('fornecedor')  # Para pedidos de recebimento
        cliente_id = request.form.get('cliente')  # Para pedidos de venda
        produto_id = request.form['produto']
        quantidade = request.form['quantidade']
        data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()

        # Validação de campos obrigatórios
        if not tipo_pedido or not produto_id or not quantidade or not data:
            flash('Por favor, preencha todos os campos obrigatórios.')
            return redirect('/adicionar_pedido')

        # Criação do pedido e salvamento no banco de dados
        novo_pedido = Pedido(
            tipo=tipo_pedido,
            fornecedor_id=fornecedor_id if tipo_pedido == 'recebimento' else None,
            cliente_id=cliente_id if tipo_pedido == 'venda' else None,
            produto_id=produto_id,
            quantidade=quantidade,
            data=data,
            colaborador_id=session['user_id']  # Colaborador logado
        )
        db.session.add(novo_pedido)
        db.session.commit()
        flash('Pedido adicionado com sucesso!')
        return redirect('/pedido')  # Redireciona para a lista de pedidos

    # Se for GET, exibe o formulário para adicionar pedido
    fornecedores = Fornecedor.query.all()
    clientes = Cliente.query.all()
    producao = Producao.query.all()
    return render_template('pedido/adicionar_pedido.html', fornecedores=fornecedores, clientes=clientes, producao=producao)


@app.route('/editar_pedido/<int:pedido_id>', methods=['GET', 'POST'])
def editar_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)  # Obtém o pedido pelo ID
    
    if request.method == 'POST':
        # Obtém e valida os dados do formulário
        tipo_pedido = request.form['tipo_pedido']
        fornecedor_id = request.form.get('fornecedor')
        cliente_id = request.form.get('cliente')
        produto_id = request.form['produto']
        quantidade = request.form['quantidade']
        data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()

        if not tipo_pedido or not produto_id or not quantidade or not data:
            flash('Por favor, preencha todos os campos obrigatórios.')
            return redirect(url_for('editar_pedido', pedido_id=pedido_id))

        # Atualiza os campos do pedido e salva no banco
        pedido.tipo = tipo_pedido
        pedido.fornecedor_id = fornecedor_id if tipo_pedido == 'recebimento' else None
        pedido.cliente_id = cliente_id if tipo_pedido == 'venda' else None
        pedido.produto_id = produto_id
        pedido.quantidade = quantidade
        pedido.data = data

        db.session.commit()
        flash('Pedido atualizado com sucesso!')
        return redirect('/pedido')  # Redireciona para a lista de pedidos
    
    # Se for GET, exibe o formulário para editar pedido
    fornecedores = Fornecedor.query.all()
    clientes = Cliente.query.all()
    producao = Producao.query.all()
    return render_template('pedido/lista_Pedido.html', pedido=pedido, fornecedores=fornecedores, clientes=clientes, producao=producao)


@app.route('/excluir_pedido/<int:pedido_id>', methods=['POST'])
def excluir_pedido(pedido_id):
    # Tenta excluir o pedido
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        db.session.delete(pedido)
        db.session.commit()
        flash('Pedido excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Ocorreu um erro ao excluir o pedido: {e}', 'danger')
    return redirect(url_for('pedido'))  # Redireciona para a lista de pedidos



#endregion

#region: Login

# Decorador para verificar login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Verificando sessão:", session.get('user_id'))  # Exibe no console o 'user_id' para depuração
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')  # Mensagem de alerta ao usuário
            return redirect(url_for('login'))  # Redireciona para a página de login se o usuário não estiver logado
        return f(*args, **kwargs)  # Executa a função original se o usuário estiver logado
    return decorated_function

# Rota para o perfil do usuário
@app.route('/perfil', methods=['GET'])
def perfil():
    # Obtém o ID do colaborador logado da sessão
    colaborador_id = session.get('user_id')

    if colaborador_id:
        colaborador = Colaborador.query.get(colaborador_id)  # Busca o colaborador pelo ID no banco
        if colaborador:
            return render_template('home.html', colaborador=colaborador)  # Renderiza a página com os dados do colaborador
        else:
            flash("Colaborador não encontrado.", "danger")  # Mensagem de erro se o colaborador não for encontrado
            return redirect(url_for('home'))
    else:
        flash("Você não está logado.", "danger")  # Mensagem de erro se o usuário não estiver logado
        return redirect(url_for('login'))  # Redireciona para o login

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']  # Obtém o nome de usuário do formulário
        senha = request.form['senha']  # Obtém a senha do formulário

        # Busca o colaborador no banco de dados com o usuário fornecido
        colaborador = Colaborador.query.filter_by(usuario=usuario).first()
        
        if colaborador:
            if bcrypt.check_password_hash(colaborador.senha, senha):  # Verifica a senha criptografada
                session['user_id'] = colaborador.id  # Armazena o ID do colaborador na sessão
                session['setor'] = colaborador.setor  # Armazena o setor na sessão
                flash('Login realizado com sucesso!', 'success')  # Mensagem de sucesso
                return redirect(url_for('perfil'))  # Redireciona para o perfil
            else:
                flash('Senha incorreta.', 'danger')  # Mensagem de erro se a senha estiver incorreta
        else:
            flash('Colaborador não encontrado.', 'danger')  # Mensagem de erro se o colaborador não for encontrado

    return render_template('cripto/login.html')  # Renderiza a página de login para GET ou falhas no POST

# Rota para Logout
@app.route('/logout')
def logout():
    session.clear()  # Limpa a sessão para encerrar a sessão do usuário
    flash('Você saiu com sucesso.', 'info')  # Mensagem de informação
    return redirect(url_for('login'))  # Redireciona para a página de login

# Rota para exibir uma página de erro
@app.route('/pagina_erro')
def pagina_erro():
    return render_template('cripto/erroAcesso.html')  # Renderiza uma página de erro customizada

#endregion

#region: Home

# Rota Home protegida com verificação direta
@app.route('/home')
def home():
    return render_template('home.html')  # Exibe a página home se o usuário estiver logado

#endregion

#region: Main


# Obtém o tamanho da tela do sistema
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Cria a janela com as dimensões da tela
window = webview.create_window('Lotus It Solutions', app, width=screen_width, height=screen_height)

# Código principal para rodar a aplicação
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas do banco de dados, se ainda não existirem
    # app.run(debug=True)  # Inicia a aplicação em modo de depuração    
    webview.start()  # Inicia a aplicação em modo de produção

#endregion
