from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'barbearia_jp_moderno_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///barbearia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELO DE DADOS ---
class Servico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    duracao_min = db.Column(db.Integer, nullable=False)
    icone = db.Column(db.String(50), default="bi-scissors")

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_whatsapp = db.Column(db.String(20), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servico.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Confirmado')
    
    servico = db.relationship('Servico', backref='agendamentos')

with app.app_context():
    db.create_all()
    if not Servico.query.first():
        s1 = Servico(nome="Low Fade / Mid Fade Moderno", preco=50.00, duracao_min=35, icone="bi-scissors")
        s2 = Servico(nome="Crop French + Acabamento Navalhado", preco=55.00, duracao_min=40, icone="bi-lightning-charge")
        s3 = Servico(nome="Barba Viking / Desenhada a Navalha", preco=40.00, duracao_min=30, icone="bi-person-badge")
        s4 = Servico(nome="Combo Urbano (Fade + Barba + Sobrancelha)", preco=90.00, duracao_min=60, icone="bi-stars")
        db.session.add_all([s1, s2, s3, s4])
        db.session.commit()

# --- ROTAS ---
@app.route('/', methods=['GET', 'POST'])
def tela1_menu():
    if request.method == 'POST':
        servico_id = request.form.get('servico_id')
        data_selecionada = request.form.get('data_agendamento')
        
        if not servico_id or not data_selecionada:
            flash("Por favor, selecione um serviço e uma data.", "danger")
            return redirect(url_for('tela1_menu'))
            
        return redirect(url_for('tela2_grade', servico_id=servico_id, data=data_selecionada))
        
    servicos = Servico.query.all()
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    return render_template('tela1_menu.html', servicos=servicos, data_hoje=data_hoje)

@app.route('/agendar', methods=['GET', 'POST'])
def tela2_grade():
    servico_id = request.args.get('servico_id') or request.form.get('servico_id')
    data_str = request.args.get('data') or request.form.get('data')
    
    if not servico_id or not data_str:
        return redirect(url_for('tela1_menu'))

    servico = Servico.query.get_or_404(servico_id)

    if request.method == 'POST':
        horario_str = request.form.get('horario')
        nome = request.form.get('nome', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        
        if not nome or len(nome) < 3 or not whatsapp or len(whatsapp) < 10 or not horario_str:
            flash("Preencha todos os campos corretamente.", "danger")
            return redirect(url_for('tela2_grade', servico_id=servico_id, data=data_str))
        
        data_hora_obj = datetime.strptime(f"{data_str} {horario_str}", '%Y-%m-%d %H:%M')
        
        # Validação de segurança: Verifica se o horário já está ocupado por outro agendamento
        conflito = Agendamento.query.filter_by(data_hora=data_hora_obj).first()
        if conflito:
            flash("Este horário acabou de ser ocupado por outro cliente. Por favor, escolha outro.", "danger")
            return redirect(url_for('tela2_grade', servico_id=servico_id, data=data_str))
        
        # Gravação no banco de dados
        novo_agendamento = Agendamento(
            cliente_nome=nome,
            cliente_whatsapp=whatsapp,
            servico_id=int(servico_id),
            data_hora=data_hora_obj
        )
        db.session.add(novo_agendamento)
        db.session.commit()
        
        return redirect(url_for('tela3_resultado', agendamento_id=novo_agendamento.id))
    
    # Grade padrão de horários do dia
    todos_horarios = ["09:30", "10:30", "11:30", "14:00", "15:00", "16:30", "18:00", "19:00"]
    
    # Busca horários já agendados no banco para esta data específica
    inicio_dia = datetime.strptime(f"{data_str} 00:00", '%Y-%m-%d %H:%M')
    fim_dia = datetime.strptime(f"{data_str} 23:59", '%Y-%m-%d %H:%M')
    
    agendamentos_existentes = Agendamento.query.filter(
        Agendamento.data_hora >= inicio_dia,
        Agendamento.data_hora <= fim_dia
    ).all()
    
    # Extrai apenas os horários (ex: "14:00") que já possuem agendamento confirmado
    horarios_ocupados = [a.data_hora.strftime('%H:%M') for a in agendamentos_existentes]
    
    # Filtra a lista removendo os horários que já estão ocupados
    horarios_disponiveis = [h for h in todos_horarios if h not in horarios_ocupados]
    
    data_fmt = datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    
    return render_template(
        'tela2_grade.html', 
        servico=servico, 
        data=data_str, 
        data_fmt=data_fmt, 
        horarios=horarios_disponiveis
    )

@app.route('/confirmacao/<int:agendamento_id>')
def tela3_resultado(agendamento_id):
    agendamento = Agendamento.query.get_or_404(agendamento_id)
    
    telefone_barbeiro = "5512999998888"
    data_fmt = agendamento.data_hora.strftime('%d/%m/%Y')
    hora_fmt = agendamento.data_hora.strftime('%H:%M')
    
    texto_mensagem = (
        f"Fala, mano! Confirmo meu agendamento na Barbearia JP (#JP-{agendamento.id}):\n"
        f"• *Cliente:* {agendamento.cliente_nome}\n"
        f"• *Serviço:* {agendamento.servico.nome}\n"
        f"• *Data/Hora:* {data_fmt} às {hora_fmt}\n"
        f"• *Valor:* R$ {agendamento.servico.preco:.2f}"
    )
    
    link_whatsapp = f"https://wa.me/{telefone_barbeiro}?text={urllib.parse.quote(texto_mensagem)}"
    
    return render_template('tela3_resultado.html', agendamento=agendamento, link_whatsapp=link_whatsapp)

if __name__ == '__main__':
    app.run(debug=True)