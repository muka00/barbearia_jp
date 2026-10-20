<div align="center">
   <img src="http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=RED&style=for-the-badge" alt="Status: Em Desenvolvimento"/>
</div>

# 💈 Barbearia JP - MVP de Agendamento Online

> Aplicação web mobile-first desenvolvida em Flask para simplificar e automatizar o processo de agendamento de serviços em barbearias, com integração direta para envio de confirmações via WhatsApp.

---

## 📌 Sobre o Projeto

O **Barbearia JP** é um protótipo funcional (MVP) focado na experiência do usuário (UX) e acessibilidade. O sistema permite que clientes naveguem pelos serviços oferecidos, escolham horários disponíveis em tempo real e finalizem o agendamento de forma rápida e intuitiva em dispositivos móveis e desktops.

### 🎯 Funcionalidades Principais
- **Visualização de Serviços e Valores:** Apresentação clara de cortes e pacotes com preços, tempos estimados e descrições detalhadas.
- **Agendamento Interativo:** Seleção simples de data, grade de horários dinâmica (que oculta horários já ocupados) e prevenção de conflitos de agendamento.
- **Confirmação via WhatsApp:** Redirecionamento automático com mensagem formatada para confirmação direta com o estabelecimento.
- **Interface Responsiva & Acessível:** Layout moderno e sofisticado (Tema *Premium* em Cinza Carvão e Dourado), botões otimizados para toque (touch-friendly) e botão de alto contraste visual.

---

## 🎨 Identidade Visual & Design System

O projeto abandonou o visual genérico de "app de tecnologia" e adotou uma estética **Premium de Barbearia Clássica**:
- **Cores:** Fundo em Carvão Profundo (`#121212`), Cards em Grafite (`#1c1c1e`) e Destaques em Dourado/Latão (`#d4af37`).
- **Tipografia:** *Plus Jakarta Sans* (Google Fonts) para um toque moderno e legível.
- **CSS Modular:** Todo o estilo está centralizado em `static/css/style.css`, facilitando a manutenção e a troca de temas.
- **Micro-interações:** Efeitos de *hover* suaves, brilho dourado e animações de escala na logo e nos botões.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.12
- **Framework Web:** Flask (Arquitetura MVC)
- **Front-end:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Banco de Dados:** SQLite & SQLAlchemy
- **Controle de Versão:** Git & GitHub CLI (`gh`)


## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
- Python instalado
- Git instalado

### Passo a Passo

1. **Clonar o repositório:**
 ```bash
  git clone [https://github.com/muka00/barbearia_jp.git](https://github.com/muka00/barbearia_jp.git)
  cd barbearia_jp
```
2. **Criar e ativar o ambiente virtual (Recomendado):**

```bash
# Windows
python -m venv venv
venv\Scripts\activate
# Linux / macOS
python3 -m venv venv
source venv/bin/activate 
```
3. **Instalar as dependências:**

 ```bash
pip install -r requirements.txt
```
(Caso o arquivo não exista, instale manualmente: pip install Flask Flask-SQLAlchemy pytest)

4. **Executar a aplicação:**

```bash
python app.py
```
5. **Acessar no navegador:**

Abra o seu navegador e acesse: http://127.0.0.1:5000

## Desenvolvedores

[![Samuel Fernandes](https://avatars.githubusercontent.com/u/212030742?v=4)](https://github.com/muka00)  
[**Samuel Fernandes**](https://github.com/muka00)
