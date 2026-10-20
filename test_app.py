import pytest
from app import app, db, Servico, Agendamento
from datetime import datetime

@pytest.fixture
def client():
    # Configura o app para modo de teste
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Usa banco em memória para não sujar o real
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Cria um serviço de teste
            s1 = Servico(nome="Corte de Teste", preco=50.0, duracao_min=30, descricao="Teste")
            db.session.add(s1)
            db.session.commit()
            
            yield client
            
            # Limpa o banco após os testes
            db.session.remove()
            db.drop_all()

# --- TESTES ---

def test_pagina_inicial_carrega(client):
    """Testa se a Landing Page (index) abre com status 200"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Barbearia JP" in response.data

def test_pagina_servicos_carrega(client):
    """Testa se a Tela 1 (seleção de serviço) abre corretamente"""
    response = client.get('/servicos')
    assert response.status_code == 200
    assert b"Corte de Teste" in response.data

def test_agendamento_sem_dados_falha(client):
    """Testa se o formulário rejeita envios com nome/whatsapp vazios"""
    # Pega o ID do serviço criado no banco em memória
    with app.app_context():
        servico = Servico.query.first()
        servico_id = servico.id

    # Envia os dados obrigatórios da URL, mas deixa nome e whatsapp vazios
    response = client.post('/agendar', data={
        'servico_id': servico_id,
        'data': '2024-12-20',
        'horario': '10:00',
        'nome': '',
        'whatsapp': ''
    }, follow_redirects=True)

    assert response.status_code == 200
    # Verifica se a mensagem de erro (flash) apareceu
    assert b"Preencha todos os campos" in response.data

def test_fluxo_agendamento_completo(client):
    """Testa se um agendamento válido é concluído e redireciona para a Tela 3"""
    # Pega o ID do serviço criado no banco em memória
    with app.app_context():
        servico = Servico.query.first()
        servico_id = servico.id

    # Simula o envio do formulário da Tela 2
    response = client.post('/agendar', data={
        'servico_id': servico_id,
        'data': '2024-12-20',
        'horario': '10:00',
        'nome': 'Cliente de Teste',
        'whatsapp': '12999998888'
    }, follow_redirects=True)

    assert response.status_code == 200
    # Verifica se a tela de sucesso abriu e tem o nome do cliente
    assert b"Tudo Certo" in response.data
    assert b"Cliente de Teste" in response.data