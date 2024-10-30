####################################################################
#Programação requirements

#region: Requirements

from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

#endregion

####################################################################
#Programação inicio

#region: Inicio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secreto'  # Defina uma chave secreta única

app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://JOAOHERMENEGILD/FazendaUrbanaLotus?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    
    return render_template('index.html')

#endregion

####################################################################
#Programação colaboradores
#region: Colaboradores

class Colaborador(db.Model):
    __tablename__ = 'Colaboradores'
    id = db.Column('id_Colaboradores', db.Integer, primary_key=True, nullable=False)
    nome = db.Column('nome_Colaboradores', db.String(100), nullable=True)
    email = db.Column('email_Colaboradores', db.String(100), nullable=True)
    setor = db.Column('setor_Colaboradores', db.String(100), nullable=True)


@app.route('/colaborador')
def colaborador():
    colaboradores = Colaborador.query.all()
    return render_template('colaborador/Colaborador.html',colaboradores=colaboradores)

@app.route('/adicionar_colaborador', methods=['GET', 'POST'])
def adicionar_colaborador():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        setor = request.form['setor']

        # Validação básica
        if not nome or not email:
            flash('Por favor, preencha todos os campos.')
            return redirect('/adicionar_colaborador')  # Redireciona para o formulário

        novo_colaborador = Colaborador(nome=nome, email=email, setor=setor)
        db.session.add(novo_colaborador)
        db.session.commit()

        flash('Colaborador adicionado com sucesso!')
        return redirect('/colaborador')  # Redireciona para a página inicial



@app.route('/editar_colaborador/<int:colaborador_id>', methods=['GET', 'POST'])
def editar_colaborador(colaborador_id):
    colaborador = Colaborador.query.get_or_404(colaborador_id)
    if request.method == 'POST':
        colaborador.nome = request.form['nome']
        colaborador.email = request.form['email']
        colaborador.setor = request.form['setor']   
        db.session.commit()
        return redirect(url_for('colaborador', colaborador_id=colaborador.id)) 
        
    return render_template('colaborador/item_Colaborador.html', colaborador=colaborador)

@app.route('/excluir_colaborador/<int:colaborador_id>', methods=['POST'])
def excluir_colaborador(colaborador_id):
    colaborador = Colaborador.query.get_or_404(colaborador_id)
    db.session.delete(colaborador)
    db.session.commit()
    flash('Colaborador excluído com sucesso!')  # Adicione uma mensagem de sucesso
    return redirect(url_for('colaborador'))  # Redireciona para a página de colaboradores

@app.route('/pesquisar_colaborador', methods=['GET'])
def pesquisar_colaborador():
    nome = request.args.get('nome', '').strip()
    if nome:
        colaboradores = Colaborador.query.filter(Colaborador.nome.like(f"%{nome}%")).all()
    else:
        colaboradores = Colaborador.query.all()
    return render_template('colaborador/Colaborador.html', colaboradores=colaboradores)


#endregion

####################################################################
#PROGRAMAÇÃO producao
#region: Producao


class Producao(db.Model):
    __tablename__ = 'Producao'
    id = db.Column('id_Producao', db.Integer, primary_key=True, nullable=False)
    nome = db.Column('nome_Producao', db.String(100), nullable=True)
    fornecedor = db.Column('fornecedor_Producao', db.String(100), nullable=True)  # Novo campo
    quantidade = db.Column('quantidade_Producao', db.Integer, nullable=True)       # Novo campo
    data = db.Column('data_Producao', db.Date, nullable=True)                      # Novo campo
    preco = db.Column('preco_Producao', db.Float, nullable=True)                    # Novo campo

@app.route('/producao')  # Atualizando a rota
def producao():
    producoes = Producao.query.all()  # Atualizando a consulta para 'Produção'
    return render_template('producao/Producao.html', producoes=producoes)  # Atualizando o template

@app.route('/adicionar_producao', methods=['GET', 'POST'])  # Atualizando a rota
def adicionar_producao():  # Atualizando a função
    if request.method == 'POST':
        nome = request.form['nome']
        fornecedor = request.form['fornecedor']
        quantidade = request.form['quantidade']
        data = datetime.strptime(request.form['data'],'%Y-%m-%d').date()
        preco = request.form['preco']

        # Validação básica
        if not nome or not fornecedor or not quantidade or not data or not preco:
            flash('Por favor, preencha todos os campos.')
            return redirect('/adicionar_producao')  # Atualizando o redirecionamento

        nova_producao = Producao(
            nome=nome,
            fornecedor=fornecedor,
            quantidade=quantidade,
            data=data,
            preco=preco
        )  # Atualizando para 'Produção'
        db.session.add(nova_producao)
        db.session.commit()

        flash('Produção adicionada com sucesso!')  # Atualizando a mensagem
        return redirect('/producao')  # Atualizando o redirecionamento


@app.route('/editar_producao/<int:producao_id>', methods=['POST'])
def editar_producao(producao_id):
    producao = Producao.query.get_or_404(producao_id)
    if request.method == 'POST':
        producao.nome = request.form['nome']
        producao.fornecedor = request.form['fornecedor']
        producao.quantidade = request.form['quantidade']
        producao.data = datetime.strptime(request.form['data'],'%Y-%m-%d').date()
        producao.preco = request.form['preco']
        db.session.commit()
        return redirect(url_for('producao', producao_id = producao.id))  # Redireciona para a lista de produções


@app.route('/excluir_producao/<int:producao_id>', methods=['POST'])
def excluir_producao(producao_id):
    try:
        producao = Producao.query.get_or_404(producao_id)
        print(f'Tentando excluir a produção: {producao}')
        db.session.delete(producao)
        db.session.commit()
        flash('Produção excluída com sucesso!', 'success')
    except Exception as e:
        print(f'Erro ao excluir produção: {e}')  # Imprime o erro no console
        flash(f'Ocorreu um erro ao excluir a produção: {e}', 'danger')
    return redirect(url_for('producao'))

@app.route('/pesquisar_producao', methods=['GET'])
def pesquisar_producao():
    nome = request.args.get('nome', '').strip()
    if nome:
        producoes = Producao.query.filter(Producao.nome.like(f"%{nome}%")).all()
    else:
        producoes = Producao.query.all()
    return render_template('producao/Producao.html', producoes=producoes)


#endregion

####################################################################
#PROGRAMAÇÃO fornecedor
#region: Fornecedor

class Fornecedor(db.Model):
    __tablename__ = 'Fornecedor'
    id = db.Column('id_Fornecedor', db.Integer, primary_key=True, nullable=False)
    nome = db.Column('nome_Fornecedor', db.String(100), nullable=False)
    endereco = db.Column('endereco_Fornecedor', db.String(200), nullable=True)
    cnpj_pf = db.Column('cnpj_pf_Fornecedor', db.String(18), nullable=True)
    contato = db.Column('contato_Fornecedor', db.String(100), nullable=True)
    email = db.Column('email_Fornecedor', db.String(100), nullable=True)

@app.route('/fornecedores')
def fornecedores():
    fornecedores = Fornecedor.query.all()
    return render_template('fornecedor/Fornecedor.html', fornecedores=fornecedores)

@app.route('/adicionar_fornecedor', methods=['GET', 'POST'])
def adicionar_fornecedor():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        cnpj_pf = request.form['cnpj_pf']
        contato = request.form['contato']
        email = request.form['email']

        if not nome:
            flash('Por favor, preencha o nome do fornecedor.')
            return redirect('/adicionar_fornecedor')

        novo_fornecedor = Fornecedor(
            nome=nome,
            endereco=endereco,
            cnpj_pf=cnpj_pf,
            contato=contato,
            email=email
        )
        db.session.add(novo_fornecedor)
        db.session.commit()
        flash('Fornecedor adicionado com sucesso!')
        return redirect('/fornecedores')

@app.route('/editar_fornecedor/<int:fornecedor_id>', methods=['POST'])
def editar_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
    if request.method == 'POST':
        fornecedor.nome = request.form['nome']
        fornecedor.endereco = request.form['endereco']
        fornecedor.cnpj_pf = request.form['cnpj_pf']
        fornecedor.contato = request.form['contato']
        fornecedor.email = request.form['email']
        db.session.commit()
        flash('Fornecedor atualizado com sucesso!')
        return redirect(url_for('fornecedores', fornecedor_id=fornecedor.id))

@app.route('/excluir_fornecedor/<int:fornecedor_id>', methods=['POST'])
def excluir_fornecedor(fornecedor_id):
    try:
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
        db.session.delete(fornecedor)
        db.session.commit()
        flash('Fornecedor excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Ocorreu um erro ao excluir o fornecedor: {e}', 'danger')
    return redirect(url_for('fornecedores'))

@app.route('/pesquisar_fornecedor', methods=['GET'])
def pesquisar_fornecedor():
    nome = request.args.get('nome', '').strip()
    if nome:
        fornecedores = Fornecedor.query.filter(Fornecedor.nome.like(f"%{nome}%")).all()
    else:
        fornecedores = Fornecedor.query.all()
    return render_template('fornecedor/Fornecedor.html', fornecedores=fornecedores)


#endregion

####################################################################
#PROGRAMAÇÃO cliente
#region: Cliente
class Cliente(db.Model):
    __tablename__ = 'Cliente'
    id = db.Column('id_Cliente', db.Integer, primary_key=True, nullable=False)
    nome = db.Column('nome_Cliente', db.String(100), nullable=False)
    endereco = db.Column('endereco_Cliente', db.String(200), nullable=True)
    cnpj_pf = db.Column('cnpj_pf_Cliente', db.String(18), nullable=True)
    contato = db.Column('contato_Cliente', db.String(100), nullable=True)
    email = db.Column('email_Cliente', db.String(100), nullable=True)

@app.route('/clientes')
def clientes():
    clientes = Cliente.query.all()
    return render_template('clientes/Clientes.html', clientes=clientes)

@app.route('/adicionar_cliente', methods=['GET', 'POST'])
def adicionar_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        cnpj_pf = request.form['cnpj_pf']
        contato = request.form['contato']
        email = request.form['email']

        if not nome:
            flash('Por favor, preencha o nome do cliente.')
            return redirect('/adicionar_cliente')

        novo_cliente = Cliente(
            nome=nome,
            endereco=endereco,
            cnpj_pf=cnpj_pf,
            contato=contato,
            email=email
        )
        db.session.add(novo_cliente)
        db.session.commit()
        flash('Cliente adicionado com sucesso!')
        return redirect('/clientes')

@app.route('/editar_cliente/<int:cliente_id>', methods=['POST'])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.endereco = request.form['endereco']
        cliente.cnpj_pf = request.form['cnpj_pf']
        cliente.contato = request.form['contato']
        cliente.email = request.form['email']
        db.session.commit()
        flash('Cliente atualizado com sucesso!')
        return redirect(url_for('clientes', cliente_id=cliente.id))

@app.route('/excluir_cliente/<int:cliente_id>', methods=['POST'])
def excluir_cliente(cliente_id):
    try:
        cliente = Cliente.query.get_or_404(cliente_id)
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Ocorreu um erro ao excluir o cliente: {e}', 'danger')
    return redirect(url_for('clientes'))

@app.route('/pesquisar_cliente', methods=['GET'])
def pesquisar_cliente():
    nome = request.args.get('nome', '').strip()
    if nome:
        clientes = Cliente.query.filter(Cliente.nome.like(f"%{nome}%")).all()
    else:
        clientes = Cliente.query.all()
    return render_template('clientes/Clientes.html', clientes=clientes)


#endregion

####################################################################
#PROGRAMAÇÃO login
#region: Login

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("Rota /register acessada")  # Linha para debug
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash da senha
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Cria um novo usuário
        novo_usuario = Usuario(username=username, password=hashed_password)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Usuário registrado com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('cripto/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Busca o usuário no banco de dados
        usuario = Usuario.query.filter_by(username=username).first()
        print(f"Usuário encontrado: {usuario}")  # Debug

        # Verifica se o usuário existe e se a senha está correta
        if usuario and bcrypt.check_password_hash(usuario.password, password):
            session['user_id'] = usuario.id  # Armazena o ID do usuário na sessão
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('home'))  # Redireciona para a rota "home"
        else:
            flash('Usuário ou senha incorretos.', 'danger')
            print("Usuário ou senha incorretos.")  # Debug

    return render_template('cripto/login.html')


#endregion

#####################################################################
#Programação home

#region: Home

@app.route('/home')
def home():
    return render_template('home.html')

#endregion

#####################################################################
#Programação main

#region: Main


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas do banco de dados
    app.run(debug=True)

#endregion
