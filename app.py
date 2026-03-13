import streamlit as st
import music21 as m21
import tempfile
import os
import io
from xhtml2pdf import pisa

st.set_page_config(page_title="App Amyrton Vallim", layout="wide")
st.title("🎼 Conversor Amyrton Vallim")
st.caption("Idealizado e desenvolvido por **Renan Brito Soprani**")
st.write("Transforme as suas partituras MusicXML para a grelha do Método Amyrton Vallim.")

mapa_notas = {'C': 'Do', 'D': 'Re', 'E': 'Mi', 'F': 'Fa', 'G': 'Sol', 'A': 'La', 'B': 'Si'}

def formatar_elemento(elemento, estado_oitava):
    if isinstance(elemento, m21.note.Note):
        nome = mapa_notas.get(elemento.step, elemento.name)
        oitava = elemento.octave
        if oitava != estado_oitava['anterior']:
            resultado = f'{nome}<sup>{oitava}</sup>'
            estado_oitava['anterior'] = oitava
        else:
            resultado = f'{nome}'
        return resultado
    elif isinstance(elemento, m21.chord.Chord):
        notas_empilhadas = []
        for p in reversed(elemento.pitches):
            nome = mapa_notas.get(p.step, p.name)
            oitava = p.implicitOctave
            if oitava != estado_oitava['anterior']:
                notas_empilhadas.append(f'{nome}<sup>{oitava}</sup>')
                estado_oitava['anterior'] = oitava
            else:
                notas_empilhadas.append(f'{nome}')
        return '<br>'.join(notas_empilhadas)
    return ""

colunas_por_linha = st.slider(
    "Ajuste a largura da grelha (Colunas por linha):", 
    min_value=4, max_value=32, value=16, step=2
)

arquivo_upload = st.file_uploader("Arraste ou selecione o seu ficheiro MusicXML (.xml / .mxl)", type=["xml", "mxl"])

if arquivo_upload is not None:
    with st.spinner("A traduzir a partitura e a gerar PDF, aguarde..."):
        extensao_original = os.path.splitext(arquivo_upload.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=extensao_original) as tmp_file:
            tmp_file.write(arquivo_upload.getvalue())
            caminho_temp = tmp_file.name

        try:
            partitura = m21.converter.parse(caminho_temp)
            
            # 1. CAÇA AO TÍTULO (Metadados ou Caixas de Texto Visuais)
            titulo_musica = "Minha Música"
            compositor_musica = ""
            
            # Tentativa A: Procurar nos Metadados oficiais
            if partitura.metadata is not None:
                candidato_titulo = partitura.metadata.title or partitura.metadata.movementName
                if candidato_titulo and "tmp" not in candidato_titulo.lower() and ".mxl" not in candidato_titulo.lower() and ".xml" not in candidato_titulo.lower():
                    titulo_musica = candidato_titulo
                    
                if partitura.metadata.composer:
                    compositor_musica = partitura.metadata.composer

            # Tentativa B: Se falhou e o nome ainda for genérico, procurar caixas de texto flutuantes (TextBox)
            if titulo_musica == "Minha Música":
                caixas_de_texto = partitura.flat.getElementsByClass(m21.text.TextBox)
                if caixas_de_texto:
                    # A primeira caixa de texto é frequentemente o título da música
                    candidato_texto = caixas_de_texto[0].content
                    if candidato_texto and "tmp" not in candidato_texto.lower() and ".mxl" not in candidato_texto.lower() and ".xml" not in candidato_texto.lower():
                        titulo_musica = candidato_texto

            st.markdown("---")
            st.markdown(f"<h2 style='text-align: center;'>{titulo_musica}</h2>", unsafe_allow_html=True)
            if compositor_musica:
                st.markdown(f"<h4 style='text-align: center; color: gray;'>{compositor_musica}</h4>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            if len(partitura.parts) >= 2:
                notas_dir = partitura.parts[0].flatten().notes
                notas_esq = partitura.parts[1].flatten().notes
            else:
                notas_dir = partitura.flatten().notes
                notas_esq = []

            tl_dir = {float(e.offset): e for e in notas_dir}
            tl_esq = {float(e.offset): e for e in notas_esq}

            tempos = list(tl_dir.keys()) + list(tl_esq.keys())
            ultimo_tempo = int(max(tempos)) if tempos else 0
            
            todos_os_tempos = sorted(list(set([float(i) for i in range(ultimo_tempo + 1)] + tempos)))

            html_tabelas = ""
            est_rh, est_lh = {'anterior': None}, {'anterior': None}

            for i in range(0, len(todos_os_tempos), colunas_por_linha):
                bloco = todos_os_tempos[i:i+colunas_por_linha]
                
                # Preenchimento das células finais em branco
                falta = colunas_por_linha - len(bloco)
                bloco_com_padding = bloco + [None] * falta
                
                html_tabelas += '<table style="border-collapse: collapse; border: 2px solid black; text-align: center; margin-bottom: 20px; font-family: Arial; font-size: 16px; page-break-inside: avoid; table-layout: fixed; width: auto;">'
                
                # Mão Direita
                html_tabelas += '<tr style="height: 60px;">'
                for t in bloco_com_padding:
                    if t is None:
                        # 2. CÉLULAS EM BRANCO VISÍVEIS COM BORDA
                        html_tabelas += '<td style="min-width: 50px; max-width: 50px; border: 1px solid black; padding: 5px;">&nbsp;</td>'
                    else:
                        cont = formatar_elemento(tl_dir[t], est_rh) if t in tl_dir else '&nbsp;'
                        html_tabelas += f'<td style="min-width: 50px; max-width: 50px; border: 1px solid black; padding: 5px; vertical-align: bottom;">{cont}</td>'
                html_tabelas += '</tr>'
                
                # Mão Esquerda
                html_tabelas += '<tr style="height: 60px;">'
                for t in bloco_com_padding:
                    if t is None:
                        # 2. CÉLULAS EM BRANCO VISÍVEIS COM BORDA
                        html_tabelas += '<td style="min-width: 50px; max-width: 50px; border: 1px solid black; padding: 5px;">&nbsp;</td>'
                    else:
                        cont = formatar_elemento(tl_esq[t], est_lh) if t in tl_esq else '&nbsp;'
                        html_tabelas += f'<td style="min-width: 50px; max-width: 50px; border: 1px solid black; padding: 5px; vertical-align: top;">{cont}</td>'
                html_tabelas += '</tr>'
                
                html_tabelas += '</table>'

            st.markdown(html_tabelas, unsafe_allow_html=True)

            # 3. PDF NA VERTICAL (PORTRAIT)
            html_para_pdf = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    @page {{ size: A4 portrait; margin: 1cm; }}
                    body {{ font-family: Arial, sans-serif; }}
                </style>
            </head>
            <body>
                <h1 style="text-align: center; margin-bottom: 5px;">{titulo_musica}</h1>
                <h3 style="text-align: center; margin-top: 0px; color: #555;">{compositor_musica}</h3>
                <hr>
                {html_tabelas}
                <br>
                <p style="text-align: right; font-size: 12px; color: #888;">
                    Partitura gerada pelo App Amyrton Vallim<br>
                    <strong>Idealizado e desenvolvido por Renan Brito Soprani</strong>
                </p>
            </body>
            </html>
            """

            pdf_buffer = io.BytesIO()
            pisa_status = pisa.CreatePDF(html_para_pdf, dest=pdf_buffer)

            if not pisa_status.err:
                st.download_button(
                    label="📄 Baixar Partitura em PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"{titulo_musica.replace(' ', '_')}_Vallim.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Houve um erro ao gerar o ficheiro PDF.")
            
        except Exception as e:
            st.error(f"Houve um problema ao ler a música: {e}")
        finally:
            os.remove(caminho_temp)