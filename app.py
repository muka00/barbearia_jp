from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import urllib.parse
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_para_desenvolvimento_dev_123'

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# Busca a URL do banco no Render (Variável de Ambiente)
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # O Render fornece a URL com 'postgres://', mas o SQLAlchemy exige 'postgresql://'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace("postgres://", "postgresql://", 1)
else:
    # Se não encontrar (rodando local), usa o SQLite para testes
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barbearia.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS DE DADOS (MVC) ---
class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    duracao_min = db.Column(db.Integer, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_whatsapp = db.Column(db.String(20), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Confirmado')
    
    servico = db.relationship('Servico', backref='agendamentos')

# Inicialização e popular dados
with app.app_context():
    try:
        db.create_all()
        if not Servico.query.first():
            s1 = Servico(nome="Corte Social", preco=35.00, duracao_min=30,
                         descricao="Corte clássico e bem estruturado, com acabamento limpo e moderno para realçar o estilo masculino.")
            s2 = Servico(nome="Barba Completa", preco=25.00, duracao_min=20,
                         descricao="Aparar, alinhar e desenhar a barba, com hidratação e finalização para um visual elegante.")
            s3 = Servico(nome="Combo Corte + Barba", preco=55.00, duracao_min=50,
                         descricao="Pacote completo: corte social e barba bem definida, garantindo um visual renovado e sofisticado.")
            db.session.add_all([s1, s2, s3])
            db.session.commit()
            print("✅ Banco de dados criado e serviços cadastrados com sucesso!")
    except Exception as e:
        print("❌ ERRO AO CRIAR O BANCO:", e)

# --- ROTAS ---
@app.route('/')
def index():
    servicos = Servico.query.all()
    return render_template('index.html', servicos=servicos)

@app.route('/health')
def health_check():
    """Rota para monitoramento externo (UptimeRobot)"""
    return {"status": "ok", "servico": "Barbearia JP"}, 200

@app.route('/servicos', methods=['GET', 'POST'])
def tela1_menu():
    if request.method == 'POST':
        servico_id = request.form.get('servico_id')
        data_selecionada = request.form.get('data_agendamento')
        if not servico_id or not data_selecionada:
            flash("Por favor, selecione um serviço e uma data válida.", "danger")
            return redirect(url_for('tela1_menu'))
        return redirect(url_for('tela2_grade', servico_id=servico_id, data=data_selecionada))
    servicos = Servico.query.all()
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    return render_template('tela1_menu.html', servicos=servicos, data_hoje=data_hoje)

@app.route('/agendar', methods=['GET', 'POST'])
def tela2_grade():
    if request.method == 'POST':
        servico_id = request.form.get('servico_id')
        data_str = request.form.get('data')
        horario_str = request.form.get('horario')
        nome = request.form.get('nome', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        
        # Validação estrita dos campos
        if not nome or len(nome) < 3 or not whatsapp or len(whatsapp) < 10 or not horario_str:
            flash("Preencha todos os campos corretamente.", "danger")
            return redirect(url_for('tela2_grade', servico_id=servico_id, data=data_str))
        
        data_hora_obj = datetime.strptime(f"{data_str} {horario_str}", '%Y-%m-%d %H:%M')

        # BLOQUEIO DE DOMINGO (weekday() == 6 é Domingo)
        if data_hora_obj.weekday() == 6:
            flash("A barbearia está fechada aos Domingos. Por favor, escolha outra data.", "danger")
            return redirect(url_for('tela2_grade', servico_id=servico_id, data=data_str))
        
        # Verifica se o horário já está ocupado
        conflito = Agendamento.query.filter_by(data_hora=data_hora_obj).first()
        if conflito:
            flash("Ops! Este horário acabou de ser reservado. Escolha outro.", "danger")
            return redirect(url_for('tela2_grade', servico_id=servico_id, data=data_str))
        
        # Gravação no Banco
        novo = Agendamento(cliente_nome=nome, cliente_whatsapp=whatsapp,
                           servico_id=int(servico_id), data_hora=data_hora_obj)
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('tela3_resultado', agendamento_id=novo.id))
    
    # Método GET (Exibe a tela)
    servico_id = request.args.get('servico_id')
    data_str = request.args.get('data')
    servico = db.get_or_404(Servico, servico_id)
    
    # Formata a data para exibição
    try:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        data_fmt = data_obj.strftime('%d/%m/%Y')
        data_busca = data_obj.date()
    except (ValueError, TypeError):
        data_fmt = data_str
        data_busca = datetime.now().date()

    # --- GRADE DE HORÁRIOS: 30 em 30 min, com almoço das 12h às 13h ---
    horarios_manha = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30"]
    horarios_tarde = ["13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
                      "16:00", "16:30", "17:00", "17:30", "18:00", "18:30"]
    horarios_base = horarios_manha + horarios_tarde

    # SE A DATA FOR DOMINGO, A GRADE FICA VAZIA (Agenda Lotada)
    if data_busca.weekday() == 6:
        horarios_disponiveis = []
    else:
        # Busca os agendamentos do dia e filtra os horários vagos
        agendamentos_do_dia = Agendamento.query.filter(
            db.func.date(Agendamento.data_hora) == data_busca
        ).all()
        horarios_ocupados = [ag.data_hora.strftime('%H:%M') for ag in agendamentos_do_dia]
        horarios_disponiveis = [h for h in horarios_base if h not in horarios_ocupados]
    
    return render_template('tela2_grade.html', servico=servico, data=data_str, data_fmt=data_fmt, horarios=horarios_disponiveis)

@app.route('/confirmacao/<int:agendamento_id>')
def tela3_resultado(agendamento_id):
    agendamento = db.get_or_404(Agendamento, agendamento_id)
    telefone = "5512992194940"
    data_fmt = agendamento.data_hora.strftime('%d/%m/%Y')
    hora_fmt = agendamento.data_hora.strftime('%H:%M')
    texto = (f"Olá, João! Confirmo meu agendamento (#JP-{agendamento.id}):\n"
             f"• *Cliente:* {agendamento.cliente_nome}\n"
             f"• *Serviço:* {agendamento.servico.nome}\n"
             f"• *Data/Hora:* {data_fmt} às {hora_fmt}\n"
             f"• *Valor:* R$ {agendamento.servico.preco:.2f}")
    link = f"https://wa.me/{telefone}?text={urllib.parse.quote(texto)}"
    return render_template('tela3_resultado.html', agendamento=agendamento, link_whatsapp=link)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)