# coding: utf-8

# todos os imports
from contextlib import closing
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# configuração
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# criar nossa pequena aplicação :)
app = Flask(__name__)
app.config.from_object(__name__)
"""
Também se pode adicionar uma variável de ambiente
apontando para um arquivo:
    export CONFIG_FLASKR=caminhoparaoarquivodeconfigs
e utilizar da seguinte manteira:
app.config.from_envvar('CONFIG_FLASKR', silent=True)
silent = true é utilizado para o flask
não reclame caso não exista o arquivo
"""
###########rotinas de inicialização do banco:############
#metodo para conectar ao banco (para simplificar um pouco)
def conectar_bd():
    return sqlite3.connect(app.config['DATABASE'])

#metodo que cria o banco
def criar_bd():
    with closing(conectar_bd()) as db:
        with app.open_resource('esquema.sql') as sql:
            db.cursor().executescript(sql.read())
        db.commit()

#####################requisições:#########################

#conecta ao db antes de atender a requisição:
@app.before_request
def pre_requisicao():
    g.db = conectar_bd()

#fecha a conexão com o DB após a requisição terminar
@app.teardown_request
def encerrar_requisicao(exception): #envia a exception caso ocorra ou null
    g.db.close()


####################rotas da URL###########################

#caminho inicial renderiza os valores lidos no db no template
@app.route('/')
def exibir_entradas():
    sql = '''select titulo, texto from entradas order by id desc'''
    curl = g.db.execute(sql)
    entradas = [dict(titulo=titulo, texto=texto)
                    for titulo, texto in curl.fetchall()]
    return render_template('exibir_entradas.html', entradas=entradas)

#possibilita que o usuário insira dados no db
@app.route('/inserir', methods=['POST'])
def inserir_entrada():
    if not session.get('logado'):
        abort(401)
    #os ?? aqui são importantes, eles protegem
    #nossa aplicação flask contra sql injection
    sql = '''insert into entradas (titulo, texto) values (?, ?)'''
    g.db.execute(sql, [request.form['titulo'], request.form['texto']])
    g.db.commit()
    flash('Nova entrada registrada com sucesso')
    return redirect(url_for('exibir_entradas'))

#login:
@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Usuário inválido'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Senha inválida'
        else:
            session['logado'] = True
            flash('Login OK')
            return redirect(url_for('exibir_entradas'))
    return render_template('login.html', erro=erro)

#logout:
@app.route('/logout')
def logout():
    session.pop('logado', None)
    flash('Logout Ok')
    return redirect(url_for('exibir_entradas'))


#caso este arquivo seja chamado (não importado) inicia
if __name__ == '__main__':
    app.run()
