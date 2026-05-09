import streamlit as st
import xml.etree.ElementTree as ET
import time

st.set_page_config(page_title="Método Amyrton Vallim - Pro", layout="wide")

# --- ESTILOS E PERSONALIZAÇÃO ---
with st.sidebar:
    st.header("⚙️ Ferramentas")
    bpm = st.slider("Batidas por Minuto (BPM)", 40, 220, 100)
    metronomo_ativo = st.toggle("Ativar Metrônomo Visual")
    st.divider()
    tamanho_fonte = st.select_slider("Tamanho da Grade", options=["Pequeno", "Médio", "Grande", "Extra"], value="Médio")
    tema = st.radio("Tema de Cor", ["Clássico (Branco)", "Sépia (Conforto)", "Noite (Escuro)"])

estilos = {
    "Clássico (Branco)": {"bg": "#ffffff", "txt": "#000000", "border": "#dddddd", "header": "#f8f9fa"},
    "Sépia (Conforto)": {"bg": "#f4ecd8", "txt": "#5b4636", "border": "#d3c1a5", "header": "#e9dfc4"},
    "Noite (Escuro)": {"bg": "#1e1e1e", "txt": "#ffffff", "border": "#444444", "header": "#2d2d2d"}
}
cor = estilos[tema]
mapa_tamanhos = {"Pequeno": "14px", "Médio": "20px", "Grande": "28px", "Extra": "36px"}
fz = mapa_tamanhos[tamanho_fonte]

# Aplicação do CSS Global baseado na sua escolha
st.markdown(f"""
    <style>
    .stApp {{ background-color: {cor['bg']}; color: {cor['txt']}; }}
    .grade-container {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
        gap: 10px;
        padding: 20px;
        background-color: {cor['bg']};
    }}
    .celula-nota {{
        border: 2px solid {cor['border']};
        border-radius: 8px;
        padding: 15px 5px;
        text-align: center;
        font-size: {fz};
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("🎼 Conversor Amyrton Vallim")

# --- LÓGICA DO METRÔNOMO VISUAL ---
if metronomo_ativo:
    placeholder_luz = st.empty()
    # No Streamlit, para o metrônomo não travar o app, mostramos apenas o estado
    placeholder_luz.markdown(f"### 🎵 {bpm} BPM")

# --- PROCESSAMENTO DO ARQUIVO ---
arquivo = st.file_uploader("Carregue o seu arquivo MusicXML", type=['xml', 'mxml', 'musicxml'])

def extrair_notas(xml_data):
    try:
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        notas_extraidas = []
        for step in root.findall(".//step"):
            notas_extraidas.append(step.text)
        return notas_extraidas
    except Exception as e:
        st.error(f"Erro ao ler o XML: {e}")
        return []

if arquivo:
    conteudo = arquivo.read().decode("utf-8")
    notas = extrair_notas(conteudo)
    
    if notas:
        st.subheader(f"Partitura: {arquivo.name}")
        
        # Gerar a grade visual
        html_grade = '<div class="grade-container">'
        for nota in notas:
            html_grade += f'<div class="celula-nota">{nota}</div>'
        html_grade += '</div>'
        
        st.markdown(html_grade, unsafe_allow_html=True)
        
        # Feedback do Metrônomo se ativo
        if metronomo_ativo:
            if st.button("Iniciar Pulsação Visual (Teste)"):
                for _ in range(8):
                    placeholder_luz.markdown("🟢 **PUM**")
                    time.sleep(60/bpm * 0.5)
                    placeholder_luz.markdown("⚪ **...**")
                    time.sleep(60/bpm * 0.5)
    else:
        st.warning("O arquivo foi carregado, mas não encontrámos notas musicais válidas.")
