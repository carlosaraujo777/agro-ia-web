# --- IMPORTAÇÕES ---
# Importa a biblioteca do Streamlit, que é a nossa "mágica" pra criar a interface web.
import streamlit as st 

# Importa a biblioteca nova do Google pra usar a IA.
from google import genai
# Importa a parte de configuração (onde a gente define o "prompt de sistema").
from google.genai import types 

# --- CONFIGURAÇÃO DA PÁGINA ---
# set_page_config define o título da aba do navegador, o ícone e o layout (centralizado).
st.set_page_config(page_title="AgroIA", page_icon="🌱", layout="centered")

# --- CSS CUSTOMIZADO (A "Maquiagem") ---
# st.markdown permite injetar HTML e CSS dentro do Streamlit.
# Aqui a gente tá criando o design das mensagens e do fundo escuro.
st.markdown("""
    <style>
    /* Muda a cor de fundo de toda a aplicação */
    .stApp {
        background-color: #0d1117; /* Fundo escuro estilo GitHub */
        color: #c9d1d9; /* Cor do texto padrão */
    }
    /* Estilo das mensagens do USUÁRIO (alinhadas à direita, fundo azul) */
    .user-msg {
        background-color: #1f6feb; /* Azul */
        color: white;
        padding: 10px 15px; /* Espaçamento interno */
        border-radius: 15px 15px 0 15px; /* Bordas arredondadas (menos no canto inferior direito) */
        margin-bottom: 10px; /* Espaço entre as mensagens */
        text-align: right;
        margin-left: 20%; /* Empurra a bolha pra direita */
    }
    /* Estilo das mensagens da IA (alinhadas à esquerda, fundo cinza escuro) */
    .ia-msg {
        background-color: #161b22; /* Cinza escuro */
        border: 1px solid #30363d; /* Borda sutil */
        color: #c9d1d9;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0; /* Bordas arredondadas (menos no canto inferior esquerdo) */
        margin-bottom: 10px;
        text-align: left;
        margin-right: 20%; /* Empurra a bolha pra esquerda */
    }
    /* Estilo do campo de texto (input) */
    .stTextInput input {
        background-color: #0d1117;
        color: white;
        border: 1px solid #30363d;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True) # unsafe_allow_html=True permite rodar o HTML/CSS

# --- TÍTULOS ---
st.title("🌱 AgroIA - Assistente Agrícola")
st.caption("Pergunte sobre plantio, pragas, clima e mercado agrícola.")

# --- CONFIGURAÇÃO DA API ---
# Aqui você cola a sua chave de API.
# (Dica: em produção, a gente não coloca a chave no código, mas sim em variáveis de ambiente).
API_KEY = API_KEY = st.secrets["GEMINI_API_KEY"] # Substitua pela sua chave de API do Google GenAI
# Cria o cliente que vai se conectar com o Google.
client = genai.Client(api_key=API_KEY)

# --- GERENCIAMENTO DE ESTADO DO CHAT ---
# st.session_state é como uma "memória" do Streamlit. 
# Ele guarda o histórico da conversa enquanto a página não for recarregada.
if "messages" not in st.session_state:
    st.session_state.messages = [] # Se não existir histórico, cria uma lista vazia.

# --- RENDERIZAÇÃO DO HISTÓRICO ---
# Aqui a gente percorre a lista de mensagens e desenha na tela.
for message in st.session_state.messages:
    # Se a mensagem for do usuário, usa a div com a classe "user-msg"
    if message["role"] == "user":
        st.markdown(f'<div class="user-msg">{message["content"]}</div>', unsafe_allow_html=True)
    # Se for da IA, usa a div com a classe "ia-msg"
    else:
        st.markdown(f'<div class="ia-msg">{message["content"]}</div>', unsafe_allow_html=True)

# --- INPUT DO USUÁRIO ---
# st.chat_input cria aquela caixa de texto fixa no rodapé da tela.
# O "if prompt :=" significa "se o usuário digitou algo e apertou Enter, guarde na variável prompt".
if prompt := st.chat_input("Qual a sua dúvida sobre a safra?"):
    
    # 1. Adiciona a mensagem do usuário no histórico e desenha na tela.
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)

    # 2. Chama a IA (mostrando um aviso de "pensando").
    # O st.spinner cria uma animação de carregamento enquanto a resposta não chega.
    with st.spinner("AgroIA está pensando..."):
        try:
            # Faz a chamada pra API do Google com o modelo rápido (flash-lite).
            response = client.models.generate_content(
                model='gemini-3.5-flash-lite', # O modelo que descobrimos que é rápido
                contents=prompt, # A pergunta do usuário
                config=types.GenerateContentConfig( # A configuração da "personalidade"
                    system_instruction="Você é o AgroIA, um assistente virtual especialista em agronegócio brasileiro. Responda de forma clara, técnica e amigável."
                )
            )
            resposta_ia = response.text # Pega só o texto da resposta.
        except Exception as e:
            # Se der erro, mostra a mensagem de erro na tela (sem travar o app).
            resposta_ia = f"❌ Erro: {e}"

    # 3. Adiciona a resposta da IA no histórico e desenha na tela.
    st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
    st.markdown(f'<div class="ia-msg">{resposta_ia}</div>', unsafe_allow_html=True)