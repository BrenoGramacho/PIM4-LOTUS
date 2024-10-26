import pyodbc
import secrets
from flask import Flask, render_template, request, redirect, flash, jsonify

app = Flask(__name__)

app.secret_key = secrets.token_urlsafe(32)

def get_db_connection():
    conn_string = (
        r'DRIVER={SQL Server};'
        r'SERVER=JOAOHERMENEGILD;'
        r'DATABASE=FazendaUrbanaLotus;'
    )
    conn = pyodbc.connect(conn_string)
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Aqui você executará as consultas SQL e passará os dados para o template
    cursor.execute('SELECT * FROM Colaboradores')
    colaboradores = cursor.fetchall()

    # Imprimir os dados para verificar o conteúdo
    print(colaboradores)

    conn.close()
    return render_template('index.html', colaboradores=colaboradores)


@app.route('/adicionar_colaborador', methods=['POST'])
def adicionar_colaborador():
    nome = request.form['nome']
    email = request.form['email']

    # Validação básica
    if not nome or not email:
        flash('Por favor, preencha todos os campos.')
        return redirect('/')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Inserir os dados no banco de dados
    cursor.execute("INSERT INTO Colaboradores (nome_Colaboradores, email_Colaboradores) VALUES (?, ?)", (nome, email))
    conn.commit()
    conn.close()

    flash('Colaborador adicionado com sucesso!')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)