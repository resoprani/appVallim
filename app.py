import streamlit as st
import xml.etree.ElementTree as ET
import zipfile
import io

st.set_page_config(page_title="Método Amyrton Vallim - Grelha Oficial", layout="wide")

# --- DICIONÁRIO DE MAPEAMENTO (SOLFEJO PORTUGUÊS) ---
mapa_notas_solfejo = {
    "C": "Do", "D": "Re", "E": "Mi", "F": "Fa", "G": "Sol", "A": "La", "B": "Si"
}

# --- ESTILOS E PERSONALIZAÇÃO ---
with st.sidebar:
    st.header("⚙️ Ferramentas")
    st.caption("Ajuste o visual para o seu piano")
    tamanho_fonte = st.select_slider("Tamanho da Grade", options=["Pequeno", "Médio", "Grande", "Extra"], value="Médio")
    tema = st.radio("Tema de Cor", ["Clássico (Branco)", "Sépia (Conforto)", "Noite (Escuro)"])
    st.divider()
    bpm = st.slider("BPM Metrônomo (Visual)", 40, 220, 100)
    metronomo_ativo = st.toggle("Ativar Batida Visual")

estilos = {
    "Clássico (Branco)": {"bg": "#ffffff", "txt": "#000000", "border": "#dddddd", "nota_bg": "#f9f9f9"},
    "Sépia (Conforto)": {"bg": "#f4ecd8", "txt": "#5b4636", "border": "#d3c1a5", "nota_bg": "#e9dfc4"},
    "Noite (Escuro)": {"bg": "#1e1e1e", "txt": "#ffffff", "border": "#444444", "nota_bg": "#2d2d2d"}
}
cor = estilos[tema]
mapa_tamanhos = {"Pequeno": "16px", "Médio": "22px", "Grande": "30px", "Extra": "42px"}
mapa_sub_tamanhos = {"Pequeno": "12px", "Médio": "16px", "Grande": "22px", "Extra": "30px"}
fz = mapa_tamanhos[tamanho_fonte]
fz_sub = mapa_sub_tamanhos[tamanho_fonte]

st.title("🎼 Método Amyrton Vallim (Grelha)")

arquivo = st.file_uploader("Carregue a sua partitura (.mxml ou .xml)", type=None)

# --- FUNÇÃO DE PROCESSAMENTO XML PROFISSIONAL (ME_SURE-BY-MEASURE) ---
def extrair_estruturado_vallim(xml_data):
    try:
        tree = ET.ElementTree(ET.fromstring(xml_data))
        root = tree.getroot()
        measures_data = []

        # Vamos percorrer compasso a compasso
        for measure in root.findall(".//measure"):
            measure_content = {'top': [], 'bottom': []}
            
            # Dentro do compasso, pegamos todas as notas
            for note in measure.findall(".//note"):
                rest = note.find(".//rest")
                # É uma nota com som (não uma pausa)
                if rest is None:
                    step = note.find(".//step")
                    # octave = note.find(".//octave") # Opcional usar oitava
                    staff = note.find(".//staff") # Mão Direita vs Mão Esquerda

                    if step is not None:
                        # Mapeamos para Do, Re, Mi...
                        nome_nota = mapa_notas_solfejo.get(step.text, "?")
                        
                        # Identificamos a mão baseada no staff (xml geralmente usa 1 para topo, 2 para baixo)
                        staff_num = staff.text if staff is not None else "1"
                        
                        if staff_num == "1": # Melodia (Mão Direita) -> Topo da Célula
                            measure_content['top'].append(nome_nota)
                        elif staff_num == "2": # Harmonia (Mão Esquerda) -> Baixo da Célula
                            measure_content['bottom'].append(nome_nota)

            # Estruturamos o compasso para exibição
            if measure_content['top'] or measure_content['bottom']:
                measures_data.append(measure_content)
        
        return measures_data
    except Exception as e:
        st.error(f"Erro ao ler XML: {e}")
        return []

# --- EXIBIÇÃO ---
if arquivo:
    try:
        dados_binarios = arquivo.read()
        conteudo_xml = ""

        # Lógica inteligente para ZIP vs Texto
        if zipfile.is_zipfile(io.BytesIO(dados_binarios)):
            with zipfile.ZipFile(io.BytesIO(dados_binarios)) as z:
                xml_path = [name for name in z.namelist() if name.endswith('.xml') and not name.startswith('META-INF')][0]
                conteudo_xml = z.open(xml_path).read().decode("utf-8")
        else:
            conteudo_xml = dados_binarios.decode("utf-8")
            
        if conteudo_xml:
            # Pegamos os compassos estruturados
            grelha_musical = extrair_estruturado_vallim(conteudo_xml)
            
            if grelha_musical:
                st.subheader(f"📍 Partitura: {arquivo.name}")
                
                # --- CSS Dinâmico baseado na Personalização ---
                st.markdown(f"""
                    <style>
                    .sistema-container {{ display: flex; flex-direction: column; gap: 15px; background-color: {cor['bg']}; padding: 10px; }}
                    .sistema {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; border-top: 2px solid {cor['txt']}; border-bottom: 2px solid {cor['txt']}; padding: 15px 0; }}
                    
                    .compasso-vallim {{ border: 2px solid {cor['txt']}; padding: 10px; display: flex; flex-direction: column; gap: 5px; }}
                    .row-vallim {{ display: flex; justify-content: space-around; gap: 3px; font-weight: bold; }}
                    
                    .nota-vallim {{ background-color: {cor['nota_bg']}; color: {cor['txt']}; border: 1px solid {cor['border']}; padding: 10px 5px; text-align: center; border-radius: 4px; font-family: serif; }}
                    
                    .harmonia-vallim {{ color: {cor['txt']}; text-align: center; font-size: {fz_sub}; font-family: serif; }}
                    
                    .nota-vallim.top {{ font-size: {fz}; }}
                    </style>
                """, unsafe_allow_html=True)

                # --- GERAÇÃO DO HTML VISUAL (RESPEITANDO A REFERÊNCIA) ---
                compassos_por_sistema = 4
                html_final = '<div class="sistema-container">'
                
                # Agrupamos em sistemas (linhas)
                for i in range(0, len(grelha_musical), compassos_por_sistema):
                    sistema_compassos = grelha_musical[i:i + compassos_por_sistema]
                    html_final += '<div class="sistema">'
                    
                    for compasso in sistema_compassos:
                        # Criamos a célula do compasso
                        html_final += '<div class="compasso-vallim">'
                        
                        # Linha de Notas da Melodia (Topo)
                        html_final += '<div class="row-vallim top">'
                        if compasso['top']:
                            for nota in compasso['top']:
                                html_final += f'<div class="nota-vallim top">{nota}</div>'
                        html_final += '</div>'
                        
                        # Linha de Acordes/Harmonia (Baixo)
                        if compasso['bottom']:
                            html_final += '<div class="harmonia-vallim">'
                            # Pegamos a primeira nota da harmonia para simular o acorde principal
                            html_final += f" {compasso['bottom'][0]} " 
                            html_final += '</div>'
                            
                        html_final += '</div>' # Fecha compasso-vallim
                    
                    html_final += '</div>' # Fecha sistema
                    
                html_final += '</div>' # Fecha sistema-container
                st.markdown(html_final, unsafe_allow_html=True)
            else:
                st.warning("O arquivo foi lido, mas a estrutura musical parece ser complexa demais para este extrator inicial.")
                
    except Exception as e:
        st.error(f"Erro crítico no processamento: {e}")
