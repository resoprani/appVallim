import streamlit as st
import subprocess
import os
import tempfile
import fitz  # A nossa lente fotográfica

st.set_page_config(page_title="App Amyrton Vallim - Extrator de IA", layout="centered")
st.title("🤖 Extrator de Partituras (Laboratório IA)")
st.caption("Fase de Testes - Extração de PDF para MusicXML")

arquivo_pdf = st.file_uploader("Selecione a partitura em PDF", type=["pdf"])

if arquivo_pdf is not None:
    if st.button("Iniciar Leitura com Inteligência Artificial"):
        
        with st.spinner("Passo 1: A converter PDF para Fotografia (Ajustando DPI para evitar alucinações)..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(arquivo_pdf.getvalue())
                pdf_path = tmp_pdf.name

            doc = fitz.open(pdf_path)
            pagina = doc.load_page(0) 
            
            # REDUÇÃO ESTRATÉGICA DO DPI PARA 200
            pix = pagina.get_pixmap(dpi=200) 
            
            img_path = pdf_path.replace(".pdf", ".png")
            pix.save(img_path)
            doc.close()

        # AUDITORIA VISUAL: Mostra na tela o que a IA vai ler
        st.success("Imagem gerada com sucesso! Esta é a visão exata que a IA terá:")
        st.image(img_path, caption="Imagem enviada para o motor de IA")

        with st.spinner("Passo 2: A IA Oemer está a decifrar as notas. Aguarde..."):
            try:
                resultado = subprocess.run(["oemer", img_path], capture_output=True, text=True)
                
                base_name = os.path.splitext(img_path)[0]
                xml_path = base_name + ".musicxml"
                
                if os.path.exists(xml_path):
                    st.success("Sucesso absoluto! A IA conseguiu escrever a partitura.")
                    with open(xml_path, "rb") as file:
                        st.download_button(
                            label="💾 Baixar Arquivo MusicXML",
                            data=file,
                            file_name="partitura_extraida.musicxml",
                            mime="application/vnd.recordare.musicxml+xml"
                        )
                else:
                    st.error("A IA tropeçou na matemática musical no último segundo.")
                    with st.expander("Ver registo de erros técnicos"):
                        st.code(resultado.stderr)
            except Exception as e:
                st.error(f"Houve um problema de sistema: {e}")
