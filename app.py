import streamlit as st
import xml.etree.ElementTree as ET
import zipfile
import io

st.set_page_config(layout="wide")
st.title("Passo 1: A Planilha Bruta")
st.write("Objetivo: Separar as notas lidas entre Mão Direita (MD) e Mão Esquerda (ME) em compassos.")

# O nosso tradutor
mapa_notas = {"C": "Do", "D": "Re", "E": "Mi", "F": "Fa", "G": "Sol", "A": "La", "B": "Si"}

arquivo = st.file_uploader("Suba a partitura", type=None)

if arquivo:
    st.success("Arquivo recebido com sucesso!")
    try:
        # 1. A FECHADURA SEGURA (Que já provámos que funciona)
        dados = arquivo.read()
        if zipfile.is_zipfile(io.BytesIO(dados)):
            with zipfile.ZipFile(io.BytesIO(dados)) as z:
                xml_nome = [n for n in z.namelist() if n.endswith('.xml') and 'META-INF' not in n][0]
                xml_texto = z.read(xml_nome).decode('utf-8')
        else:
            xml_texto = dados.decode('utf-8')

        root = ET.fromstring(xml_texto)
        
        # 2. O ORGANIZADOR DE PLANILHA
        st.write("--- Desenhando a Planilha Amyrton Vallim ---")
        
        compassos_html = ""
        
        for measure in root.findall(".//measure"):
            numero = measure.get('number', '0')
            md_notas = []
            me_notas = []
            
            for note in measure.findall(".//note"):
                # Ignora as pausas e notas de enfeite por agora para não quebrar a grelha
                if note.find("rest") is not None or note.find("grace") is not None:
                    continue
                    
                step = note.find(".//step")
                staff = note.find(".//staff")
                
                if step is not None:
                    nome_traduzido = mapa_notas.get(step.text, "?")
                    # staff 1 = mão direita, staff 2 = mão esquerda
                    mao = staff.text if staff is not None else "1"
                    
                    if mao == "1":
                        md_notas.append(nome_traduzido)
                    else:
                        me_notas.append(nome_traduzido)
            
            # Só desenha a tabela se o compasso tiver alguma nota
            if md_notas or me_notas:
                compassos_html += f"""
                <div style="display: inline-block; margin: 10px; border: 2px solid black;">
                    <div style="background-color: #f0f0f0; padding: 2px 5px; font-size: 12px; border-bottom: 1px solid black;">Compasso {numero}</div>
                    <table style="border-collapse: collapse; width: 150px; text-align: center; font-family: Arial; font-weight: bold;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid black; min-height: 40px;">{' '.join(md_notas)}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; background-color: #fafafa; min-height: 40px; color: #555;">{' '.join(me_notas)}</td>
                        </tr>
                    </table>
                </div>
                """

        # Mostra tudo no ecrã
        if compassos_html:
            st.markdown(compassos_html, unsafe_allow_html=True)
        else:
            st.warning("Não encontrei notas válidas para desenhar a planilha.")

    except Exception as e:
        st.error(f"Erro: {e}")
