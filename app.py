import streamlit as st
import subprocess
import os
import tempfile

st.set_page_config(page_title="App Amyrton Vallim - Extrator de IA", layout="centered")
st.title("🤖 Extrator de Partituras (Laboratório IA)")
st.caption("Fase de Testes - Extração de PDF para MusicXML")

arquivo_pdf = st.file_uploader("Selecione a partitura em PDF", type=["pdf"])

if arquivo_pdf is not None:
    if st.button("Iniciar Leitura com Inteligência Artificial"):
        with st.spinner("A IA Oemer está a ler as notas. Isto pode demorar alguns minutos. Não feche a página..."):
            # O sistema guarda o PDF temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(arquivo_pdf.getvalue())
                pdf_path = tmp_pdf.name

            try:
                # O comando mágico que acorda a IA
                resultado = subprocess.run(["oemer", pdf_path], capture_output=True, text=True)
                
                # A IA cria um arquivo novo com o mesmo nome, mas terminando em .musicxml
                base_name = os.path.splitext(pdf_path)[0]
                xml_path = base_name + ".musicxml"
                
                if os.path.exists(xml_path):
                    st.success("Sucesso! A Inteligência Artificial decifrou a partitura.")
                    with open(xml_path, "rb") as file:
                        st.download_button(
                            label="💾 Baixar Arquivo MusicXML",
                            data=file,
                            file_name="partitura_extraida.musicxml",
                            mime="application/vnd.recordare.musicxml+xml"
                        )
                else:
                    st.error("A IA teve dificuldade em ler esta imagem.")
                    with st.expander("Ver registo de erros técnicos"):
                        st.code(resultado.stderr)
            except Exception as e:
                st.error(f"Houve um problema de sistema: {e}")
