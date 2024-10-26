from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secreto'  # Defina uma chave secreta única

app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://JOAOHERMENEGILD/FazendaUrbanaLotus?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    
    return render_template('index.html')

#########################################################################################################
#Programação colaboradores

class Colaborador(db.Model):
    __tablename__ = 'Colaboradores'
    id = db.Column('id_Colaboradores', db.Integer, primary_key=True, nullable=False)
    nome = db.Column('nome_Colaboradores', db.String(100), nullable=True)
    email = db.Column('email_Colaboradores', db.String(100), nullable=True)

@app.route('/colaborador')
def colaborador():
    colaboradores = Colaborador.query.all()
    return render_template('colaborador/Colaborador.html',colaboradores=colaboradores)

@app.route('/adicionar_colaborador', methods=['GET', 'POST'])
def adicionar_colaborador():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']

        # Validação básica
        if not nome or not email:
            flash('Por favor, preencha todos os campos.')
            return redirect('/adicionar_colaborador')  # Redireciona para o formulário

        novo_colaborador = Colaborador(nome=nome, email=email)
        db.session.add(novo_colaborador)
        db.session.commit()

        flash('Colaborador adicionado com sucesso!')
        return redirect('/colaborador')  # Redireciona para a página inicial

    # Se o método for GET, renderiza o formulário
    return render_template('colaborador/forms_Colaborador.html')


@app.route('/editar/<int:colaborador_id>', methods=['GET', 'POST'])
def editar_colaborador(colaborador_id):
    colaborador = Colaborador.query.get_or_404(colaborador_id)
    if request.method == 'POST':
        colaborador.nome = request.form['nome']
        colaborador.email = request.form['email']
        db.session.commit()
        return redirect(url_for('colaborador', colaborador_id=colaborador.id)) 
        
    return render_template('colaborador/item_Colaborador.html', colaborador=colaborador)

@app.route('/excluir/<int:colaborador_id>', methods=['POST'])
def excluir_colaborador(colaborador_id):
    colaborador = Colaborador.query.get_or_404(colaborador_id)
    db.session.delete(colaborador)
    db.session.commit()
    flash('Colaborador excluído com sucesso!')  # Adicione uma mensagem de sucesso
    return redirect(url_for('colaborador'))  # Redireciona para a página de colaboradores

@app.route('/confirmar_colaborador/<int:colaborador_id>', methods=['GET', 'POST'])
def confirmar_exclusao(colaborador_id):
    colaborador = Colaborador.query.get_or_404(colaborador_id)
    if request.method == 'POST':
        # Se o usuário confirmar a exclusão, deletamos o colaborador
        db.session.delete(colaborador)
        db.session.commit()
        flash('Colaborador excluído com sucesso!', 'success')  # Mensagem de sucesso
        return redirect(url_for('colaborador'))  # Redireciona para a página de colaboradores
    
    # Renderiza a página de confirmação
    return render_template('colaborador/confirmar_colaborador.html', colaborador=colaborador)
####################################################################
#PROGRAMAÇÃO DO PRODUCAO#

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
        data = request.form['data']
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

    return render_template('producao/forms_Producao.html')  # Atualizando o template

@app.route('/editar/<int:producao_id>', methods=['GET', 'POST'])
def editar_producao(producao_id):
    producao = Producao.query.get_or_404(producao_id)
    if request.method == 'POST':
        producao.nome = request.form['nome']
        producao.fornecedor = request.form['fornecedor']
        producao.quantidade = request.form['quantidade']
        producao.data = request.form['data']
        producao.preco = request.form['preco']
        db.session.commit()
        flash('Produção editada com sucesso!')  # Adicionando mensagem de sucesso
        return redirect(url_for('producao'))  # Redireciona para a lista de produções
    return render_template('producao/item_Producao.html', producao=producao)


@app.route('/excluir/<int:producao_id>', methods=['POST'])  # Atualizando a rota
def excluir_producao(producao_id):  # Atualizando a função
    producao = Producao.query.get_or_404(producao_id)  # Atualizando para 'Produção'
    db.session.delete(producao)
    db.session.commit()
    flash('Produção excluída com sucesso!')  # Atualizando a mensagem
    return redirect(url_for('producao'))  # Atualizando o redirecionamento


####################################################################
#PROGRAMAÇÃO DO LOGIN#

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




###################################################################################################
#Programação da home

@app.route('/home')
def home():
    return render_template('home.html')


###################################################################################################
#Programação da main

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria as tabelas do banco de dados
    app.run(debug=True)