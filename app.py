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
# Removemos a restrição de 'type' para evitar que o Streamlit bloqueie o MIME type do MusicXML
arquivo = st.file_uploader("Carregue o seu arquivo de partitura", type=None)

def extrair_notas(xml_data):
    try:
        # Tentamos ler o conteúdo independente da extensão
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        notas_extraidas = []
        # Buscamos tanto 'step' quanto o nome da nota em diferentes níveis do XML
        for note in root.findall(".//step"):
            notas_extraidas.append(note.text)
        return notas_extraidas
    except Exception as e:
        st.error(f"O arquivo não parece ser um XML válido: {e}")
        return []

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

import zipfile
import io

if arquivo:
    try:
        # Lemos o arquivo como bytes (binário) para não dar erro de decode
        dados_binarios = arquivo.read()
        conteudo_xml = ""

        # Testamos se o arquivo é um ZIP (como são os .mxml do MuseScore)
        if zipfile.is_zipfile(io.BytesIO(dados_binarios)):
            with zipfile.ZipFile(io.BytesIO(dados_binarios)) as z:
                # Procuramos o arquivo XML real dentro do pacote comprimido
                xml_files = [name for name in z.namelist() if name.endswith('.xml') and not name.startswith('META-INF')]
                if xml_files:
                    with z.open(xml_files[0]) as f:
                        conteudo_xml = f.read().decode("utf-8")
                else:
                    st.error("Arquivo comprimido lido, mas nenhum XML encontrado lá dentro.")
        else:
            # Se não for ZIP, tratamos como texto simples (.musicxml ou .xml)
            conteudo_xml = dados_binarios.decode("utf-8")
            
        if conteudo_xml:
            notas = extrair_notas(conteudo_xml)
            
            if notas:
                st.subheader(f"📍 Partitura: {arquivo.name}")
                
                # Gerar a grade visual com os estilos de zoom e tema escolhidos
                html_grade = '<div class="grade-container">'
                for nota in notas:
                    html_grade += f'<div class="celula-nota">{nota}</div>'
                html_grade += '</div>'
                
                st.markdown(html_grade, unsafe_allow_html=True)
            else:
                st.warning("O arquivo foi lido, mas não encontrámos notas nas tags <step>.")
                
    except Exception as e:
        st.error(f"Erro crítico no processamento: {e}")
