import streamlit as st
import xml.etree.ElementTree as ET
import zipfile
import io

st.title("Rascunho Zero: Leitura de Compasso")
st.write("Objetivo: Encontrar e listar as notas do 1º compasso de qualquer partitura.")

arquivo = st.file_uploader("Suba o arquivo .mxml ou .xml", type=None)

if arquivo:
    st.write("Arquivo recebido. A tentar ler...")
    try:
        dados = arquivo.read()
        
        # 1. Abre a fechadura (Verifica se é ZIP ou Texto puro)
        if zipfile.is_zipfile(io.BytesIO(dados)):
            with zipfile.ZipFile(io.BytesIO(dados)) as z:
                xml_nome = [n for n in z.namelist() if n.endswith('.xml') and 'META-INF' not in n][0]
                xml_texto = z.read(xml_nome).decode('utf-8')
                st.write("Formato detetado: MusicXML Comprimido (.mxml)")
        else:
            xml_texto = dados.decode('utf-8')
            st.write("Formato detetado: Texto Puro (.xml)")

        # 2. Transforma o texto em algo que o Python entende
        root = ET.fromstring(xml_texto)
        
        # 3. Pega O PRIMEIRO COMPASSO que aparecer no arquivo (seja qual for a música)
        primeiro_compasso = root.find(".//measure")
        
        if primeiro_compasso is not None:
            numero = primeiro_compasso.get('number', 'Desconhecido')
            st.write(f"--- Sucesso! Compasso número {numero} encontrado ---")
            
            # 4. Procura as notas apenas dentro deste compasso
            notas_encontradas = []
            for note in primeiro_compasso.findall(".//note"):
                step = note.find(".//step")
                if step is not None:
                    notas_encontradas.append(step.text)
            
            st.success(f"Notas identificadas: {notas_encontradas}")
        else:
            st.error("Não encontrei a tag <measure> neste arquivo.")

    except Exception as e:
        st.error(f"Ocorreu um erro no motor de leitura: {e}")
