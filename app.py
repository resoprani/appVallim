import streamlit as st
import xml.etree.ElementTree as ET
import zipfile
import io

st.set_page_config(page_title="Método Amyrton Vallim - Oficial", layout="wide")

# --- DICIONÁRIO DE TRADUÇÃO VALLIM ---
# Mapeia a nota e a oitava para a posição na sua grade
mapeamento_vallim = {
    "C": "1", "D": "2", "E": "3", "F": "4", "G": "5", "A": "6", "B": "7"
}

# --- CONFIGURAÇÃO VISUAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    tamanho_fonte = st.select_slider("Tamanho da Grade", options=["Pequeno", "Médio", "Grande", "Extra"], value="Médio")
    tema = st.radio("Tema de Cor", ["Clássico (Branco)", "Sépia (Conforto)", "Noite (Escuro)"])
    st.divider()
    bpm = st.number_input("BPM Metrônomo", 40, 220, 100)

estilos = {
    "Clássico (Branco)": {"bg": "#ffffff", "txt": "#000000", "border": "#000000"},
    "Sépia (Conforto)": {"bg": "#f4ecd8", "txt": "#5b4636", "border": "#5b4636"},
    "Noite (Escuro)": {"bg": "#1e1e1e", "txt": "#ffffff", "border": "#ffffff"}
}
cor = estilos[tema]
mapa_tamanhos = {"Pequeno": "16px", "Médio": "24px", "Grande": "32px", "Extra": "45px"}
fz = mapa_tamanhos[tamanho_fonte]

st.title("🎼 Método Amyrton Vallim")

arquivo = st.file_uploader("Carregue a partitura (.mxml ou .xml)", type=None)

def processar_xml_vallim(xml_data):
    try:
        root = ET.fromstring(xml_data)
        notas_grade = []
        # Percorre o XML buscando a nota (step) e a oitava (octave)
        for measure in root.findall(".//measure"):
            for note in measure.findall(".//note"):
                step = note.find(".//step")
                octave = note.find(".//octave")
                if step is not None:
                    # Aqui fazemos a tradução para os números do método (1 a 7)
                    num_vallim = mapeamento_vallim.get(step.text, "?")
                    oitava = octave.text if octave is not None else ""
                    notas_grade.append(f"{num_vallim}^{oitava}" if oitava else num_vallim)
        return notas_grade
    except:
        return []

if arquivo:
    try:
        dados = arquivo.read()
        if zipfile.is_zipfile(io.BytesIO(dados)):
            with zipfile.ZipFile(io.BytesIO(dados)) as z:
                xml_path = [n for n in z.namelist() if n.endswith('.xml') and not n.startswith('META-INF')][0]
                conteudo = z.open(xml_path).read().decode("utf-8")
        else:
            conteudo = dados.decode("utf-8")
        
        notas_traduzidas = processar_xml_vallim(conteudo)

        if notas_traduzidas:
            # DESENHO DA GRADE ORIGINAL DO MÉTODO
            st.markdown(f"""
                <style>
                .tabela-vallim {{
                    width: 100%;
                    border-collapse: collapse;
                    background-color: {cor['bg']};
                    color: {cor['txt']};
                }}
                .tabela-vallim td {{
                    border: 1px solid {cor['border']};
                    padding: 10px;
                    text-align: center;
                    font-size: {fz};
                    font-family: serif;
                    font-weight: bold;
                }}
                </style>
            """, unsafe_allow_html=True)

            # Criamos a visualização em linhas (ex: 8 notas por linha)
            colunas_por_linha = 8
            html_tabela = '<table class="tabela-vallim"><tr>'
            
            for i, nota in enumerate(notas_traduzidas):
                if i > 0 and i % colunas_por_linha == 0:
                    html_tabela += '</tr><tr>'
                html_tabela += f'<td>{nota}</td>'
            
            html_tabela += '</tr></table>'
            st.markdown(html_tabela, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Erro: {e}")
