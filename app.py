from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_para_desenvolvimento_dev_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barbearia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS DE DADOS (MVC) ---
class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    duracao_min = db.Column(db.Integer, nullable=False)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_whatsapp = db.Column(db.String(20), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Confirmado')
    
    servico = db.relationship('Servico', backref='agendamentos')

# Inicialização e popular dados fictícios de teste
with app.app_context():
    db.create_all()
    if not Servico.query.first():
        s1 = Servico(nome="Corte Social", preco=35.00, duracao_min=30)
        s2 = Servico(nome="Barba Completa", preco=25.00, duracao_min=20)
        s3 = Servico(nome="Combo Corte + Barba", preco=55.00, duracao_min=50)
        db.session.add_all([s1, s2, s3])
        db.session.commit()

# --- ROTAS DA APLICAÇÃO ---

# TELA 1: Entrada Principal e Seleção de Serviços
@app.route('/', methods=['GET', 'POST'])
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

# TELA 2: Grade de Horários e Formulário de Identificação
@app.route('/agendar', methods=['GET', 'POST'])
def tela2_grade():
    if request.method == 'POST':
        servico_id = request.form.get('servico_id')
        data_str = request.form.get('data')
        horario_str = request.form.get('horario')
        nome = request.form.get('nome', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        
        # Validação estrita no servidor (RNF02)
        if not nome or len(nome) < 3 or not whatsapp or len(whatsapp) < 10 or not horario_str:
            flash("Preencha todos os campos corretamente. Nome deve ter ao menos 3 caracteres e WhatsApp válido.", "danger")
            return redirect(url_for('tela2_grade', servico_id=servico_id, data=data_str))
        
        data_hora_obj = datetime.strptime(f"{data_str} {horario_str}", '%Y-%m-%d %H:%M')
        
        # Gravação no Banco
        novo_agendamento = Agendamento(
            cliente_nome=nome,
            cliente_whatsapp=whatsapp,
            servico_id=int(servico_id),
            data_hora=data_hora_obj
        )
        db.session.add(novo_agendamento)
        db.session.commit()
        
        return redirect(url_for('tela3_resultado', agendamento_id=novo_agendamento.id))
    
    servico_id = request.args.get('servico_id')
    data_str = request.args.get('data')
    servico = Servico.query.get_or_404(servico_id)
    
    # Grade estática simulação de horários vagos (RF01)
    horarios_simulados = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:30"]
    
    return render_template('tela2_grade.html', servico=servico, data=data_str, horarios=horarios_simulados)

# TELA 3: Confirmação e Envio via WhatsApp
@app.route('/confirmacao/<int:agendamento_id>')
def tela3_resultado(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    # Formatação do Link wa.me (RF04)
    telefone_barbeiro = "5512999998888" # Número fictício
    data_fmt = agendamento.data_hora.strftime('%d/%m/%Y')
    hora_fmt = agendamento.data_hora.strftime('%H:%M')
    
    texto_mensagem = (
        f"Olá, João Paulo! Confirmo meu agendamento (#JP-{agendamento.id}):\n"
        f"• *Cliente:* {agendamento.cliente_nome}\n"
        f"• *Serviço:* {agendamento.servico.nome}\n"
        f"• *Data/Hora:* {data_fmt} às {hora_fmt}\n"
        f"• *Valor:* R$ {agendamento.servico.preco:.2f}"
    )
    
    link_whatsapp = f"https://wa.me/{telefone_barbeiro}?text={urllib.parse.quote(texto_mensagem)}"
    
    return render_template('tela3_resultado.html', agendamento=agendamento, link_whatsapp=link_whatsapp)

if __name__ == '__main__':
    app.run(debug=True)