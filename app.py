import streamlit as st
import xml.etree.ElementTree as ET
import zipfile
import io

st.set_page_config(layout="wide")
st.title("Passo 2: O Excel Sincronizado")
st.write("Objetivo: Distribuir as notas pelas colunas do tempo. As pausas geram espaços vazios e as mãos alinham-se verticalmente.")

mapa_notas = {"C": "Do", "D": "Re", "E": "Mi", "F": "Fa", "G": "Sol", "A": "La", "B": "Si"}

arquivo = st.file_uploader("Suba a partitura", type=None)

if arquivo:
    try:
        dados = arquivo.read()
        if zipfile.is_zipfile(io.BytesIO(dados)):
            with zipfile.ZipFile(io.BytesIO(dados)) as z:
                xml_nome = [n for n in z.namelist() if n.endswith('.xml') and 'META-INF' not in n][0]
                xml_texto = z.read(xml_nome).decode('utf-8')
        else:
            xml_texto = dados.decode('utf-8')

        root = ET.fromstring(xml_texto)
        
        # --- O RELÓGIO DO MUSICXML ---
        # A tag 'divisions' diz-nos em quantas fatias minúsculas se divide 1 batida (tempo)
        div_tag = root.find(".//divisions")
        divisions = int(div_tag.text) if div_tag is not None else 1
        
        compassos_html = '<div style="display: flex; flex-wrap: wrap; gap: 15px;">'
        
        beats_globais = 4 # Assumimos 4/4 (4 colunas) por padrão, como na Ode to Joy
        
        for measure in root.findall(".//measure"):
            numero = measure.get('number', '0')
            
            # Atualiza o número de colunas se a música mudar o ritmo
            beats_tag = measure.find(".//beats")
            if beats_tag is not None:
                beats_globais = int(beats_tag.text)
            
            # Cria a planilha vazia para este compasso (linhas e colunas)
            md_linha = [""] * beats_globais
            me_linha = [""] * beats_globais
            
            cursor_tempo = 0 # O nosso "ponteiro" que varre o compasso
            
            for elem in measure:
                # O MuseScore usa 'backup' para voltar o cursor ao zero e escrever a Mão Esquerda
                if elem.tag == "backup":
                    dur = int(elem.find("duration").text)
                    cursor_tempo -= dur
                elif elem.tag == "forward":
                    dur = int(elem.find("duration").text)
                    cursor_tempo += dur
                elif elem.tag == "note":
                    # Ignora notas de enfeite miudinhas para não estragar a formatação
                    if elem.find("grace") is not None:
                        continue
                        
                    dur_tag = elem.find("duration")
                    dur = int(dur_tag.text) if dur_tag is not None else 0
                    
                    staff_tag = elem.find("staff")
                    mao = staff_tag.text if staff_tag is not None else "1"
                    
                    # CÁLCULO MESTRE: Em que coluna estamos? (Ponteiro a dividir pela unidade de tempo)
                    batida_atual = int(cursor_tempo / divisions)
                    
                    # Se NÃO for uma pausa, vamos escrever a nota na célula correta
                    if elem.find("rest") is None:
                        step = elem.find(".//step")
                        if step is not None and 0 <= batida_atual < beats_globais:
                            nome_nota = mapa_notas.get(step.text, "?")
                            if mao == "1":
                                # Se já houver uma nota na célula (um acorde), junta. Se não, escreve a nota.
                                md_linha[batida_atual] = nome_nota if not md_linha[batida_atual] else f"{md_linha[batida_atual]}<br>{nome_nota}"
                            else:
                                me_linha[batida_atual] = nome_nota if not me_linha[batida_atual] else f"{me_linha[batida_atual]}<br>{nome_nota}"
                    
                    # Avançamos o ponteiro de tempo (mesmo se for pausa, o ponteiro avança, deixando a célula vazia)
                    cursor_tempo += dur
            
            # --- DESENHO DO COMPASSO (EXCEL) ---
            compassos_html += f"""
            <div style="border: 2px solid #000; background-color: white; width: {beats_globais * 70}px;">
                <div style="background-color: #e0e0e0; text-align: center; font-size: 11px; font-weight: bold; border-bottom: 1px solid #000;">Comp {numero}</div>
                <table style="width: 100%; border-collapse: collapse; text-align: center; font-family: Arial; font-weight: bold; font-size: 18px;">
                    <tr style="height: 50px;">
            """
            # Preenche a Mão Direita
            for celula in md_linha:
                compassos_html += f'<td style="border: 1px solid #bbb; border-bottom: 3px solid #000; width: {100/beats_globais}%;">{celula}</td>'
            compassos_html += '</tr><tr style="height: 50px; background-color: #fafafa;">'
            # Preenche a Mão Esquerda
            for celula in me_linha:
                compassos_html += f'<td style="border: 1px solid #bbb; color: #666;">{celula}</td>'
            
            compassos_html += '</tr></table></div>'
            
        compassos_html += '</div>'
        st.markdown(compassos_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Erro no processamento de tempo: {e}")
