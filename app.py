import streamlit as st
import xml.etree.ElementTree as ET
import zipfile
import io

st.set_page_config(page_title="Método Amyrton Vallim - Excel Style", layout="wide")

mapa_notas = {"C": "Do", "D": "Re", "E": "Mi", "F": "Fa", "G": "Sol", "A": "La", "B": "Si"}

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Personalizar Planilha")
    tamanho_fonte = st.select_slider("Zoom", options=["Pequeno", "Médio", "Grande", "Extra"], value="Médio")
    tema = st.radio("Cores", ["Branco Excel", "Sépia Antigo", "Modo Escuro"])
    st.divider()
    st.info("Esta grade respeita o alinhamento vertical entre Mão Direita e Esquerda.")

# Mapeamento de estilos
estilos = {
    "Branco Excel": {"bg": "#ffffff", "txt": "#000000", "border": "#000000"},
    "Sépia Antigo": {"bg": "#f4ecd8", "txt": "#5b4636", "border": "#5b4636"},
    "Modo Escuro": {"bg": "#1e1e1e", "txt": "#ffffff", "border": "#ffffff"}
}
c = estilos[tema]
mapa_fz = {"Pequeno": "18px", "Médio": "24px", "Grande": "34px", "Extra": "48px"}
fz = mapa_fz[tamanho_fonte]

st.title("📑 Planilha Amyrton Vallim")

arquivo = st.file_uploader("Arraste o MusicXML aqui", type=None)

def extrair_compassos_excel(xml_data):
    try:
        root = ET.fromstring(xml_data)
        # Descobrir a pulsação por compasso (default 4)
        beats = int(root.find(".//beats").text) if root.find(".//beats") is not None else 4
        
        data_final = []
        for measure in root.findall(".//measure"):
            # Cada compasso tem 2 linhas (MD e ME) e 'beats' colunas
            grade_compasso = {
                "MD": [""] * beats,
                "ME": [""] * beats
            }
            
            # Controle de tempo dentro do compasso
            current_beat = 0
            
            for note in measure.findall(".//note"):
                # Ignorar notas de graça (grace notes) para não quebrar a grade
                if note.find("grace") is not None: continue
                
                step = note.find(".//step")
                staff = note.find(".//staff")
                duration = int(note.find("duration").text) if note.find("duration") is not None else 1
                
                if step is not None:
                    nome = mapa_notas.get(step.text, "?")
                    stf = staff.text if staff is not None else "1"
                    
                    # Coloca a nota no 'pulso' atual (simplificado para 1 nota por tempo)
                    idx = min(current_beat, beats - 1)
                    if stf == "1": grade_compasso["MD"][idx] = nome
                    else: grade_compasso["ME"][idx] = nome
                
                # Avança o cursor de tempo (assume-se que duration 1 = 1 beat para este MVP)
                # Em MusicXML real, isso depende da tag 'divisions', mas aqui simplificamos para a grade
                current_beat += 1
                if current_beat >= beats: current_beat = 0

            data_final.append(grade_compasso)
        return data_final
    except: return []

if arquivo:
    try:
        raw_data = arquivo.read()
        xml_content = ""
        if zipfile.is_zipfile(io.BytesIO(raw_data)):
            with zipfile.ZipFile(io.BytesIO(raw_data)) as z:
                xml_content = z.open([n for n in z.namelist() if n.endswith('.xml')][0]).read().decode("utf-8")
        else:
            xml_content = raw_data.decode("utf-8")

        compassos = extrair_compassos_excel(xml_content)

        if compassos:
            st.markdown(f"""
                <style>
                .tabela-excel {{ 
                    width: 100%; border-collapse: collapse; margin-bottom: 30px; 
                    background-color: {c['bg']}; color: {c['txt']}; 
                }}
                .tabela-excel td {{ 
                    border: 2px solid {c['border']}; width: 25%; height: 80px;
                    text-align: center; vertical-align: middle; 
                    font-size: {fz}; font-family: sans-serif; font-weight: bold;
                }}
                .label-mao {{ font-size: 12px; font-weight: normal; opacity: 0.7; }}
                </style>
            """, unsafe_allow_html=True)

            # Exibe de 2 em 2 compassos por linha para caber bem no telemóvel
            for i in range(0, len(compassos), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(compassos):
                        comp = compassos[i+j]
                        html = f'<table class="tabela-excel">'
                        # Linha Mão Direita
                        html += '<tr>'
                        for n in comp["MD"]: html += f'<td>{n}</td>'
                        html += '</tr>'
                        # Linha Mão Esquerda
                        html += '<tr>'
                        for n in comp["ME"]: html += f'<td style="background-color:rgba(0,0,0,0.05)">{n}</td>'
                        html += '</tr>'
                        html += '</table>'
                        cols[j].markdown(html, unsafe_allow_html=True)
        else:
            st.error("Não foi possível gerar a planilha com este arquivo.")
    except Exception as e:
        st.error(f"Erro: {e}")
