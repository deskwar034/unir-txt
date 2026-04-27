import io
import os
import zipfile
import streamlit as st


st.set_page_config(
    page_title="Unir arquivos TXT",
    page_icon="📄",
    layout="centered"
)

st.title("Unir arquivos .txt de um ZIP")
st.write("Faça upload de um arquivo `.zip` contendo vários `.txt`. O app vai gerar um único arquivo para download.")


def ler_txt_com_fallback(bytes_conteudo: bytes) -> str:
    """
    Tenta ler o conteúdo usando encodings comuns.
    Útil quando alguns arquivos estão em UTF-8 e outros em Windows/Latin-1.
    """
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]

    for enc in encodings:
        try:
            return bytes_conteudo.decode(enc)
        except UnicodeDecodeError:
            pass

    return bytes_conteudo.decode("utf-8", errors="replace")


def unir_txts_do_zip(zip_file) -> tuple[str, int]:
    partes = []

    with zipfile.ZipFile(zip_file, "r") as z:
        nomes_txt = [
            nome for nome in z.namelist()
            if nome.lower().endswith(".txt")
            and not nome.endswith("/")
            and not nome.startswith("__MACOSX/")
        ]

        nomes_txt.sort()

        for nome in nomes_txt:
            with z.open(nome) as arquivo:
                conteudo_bytes = arquivo.read()
                conteudo = ler_txt_com_fallback(conteudo_bytes)

            nome_arquivo = os.path.basename(nome)

            bloco = f"""
============================================================
ARQUIVO: {nome_arquivo}
CAMINHO NO ZIP: {nome}
============================================================

{conteudo.strip()}

"""
            partes.append(bloco)

    texto_final = "\n".join(partes)
    return texto_final, len(nomes_txt)


arquivo_zip = st.file_uploader(
    "Envie o arquivo ZIP",
    type=["zip"]
)

if arquivo_zip is not None:
    try:
        texto_unido, total_txt = unir_txts_do_zip(arquivo_zip)

        if total_txt == 0:
            st.warning("Nenhum arquivo .txt foi encontrado dentro do ZIP.")
        else:
            st.success(f"{total_txt} arquivos .txt encontrados e unidos com sucesso.")

            nome_saida = "arquivos_unidos.txt"

            st.download_button(
                label="Baixar arquivo TXT unido",
                data=texto_unido.encode("utf-8"),
                file_name=nome_saida,
                mime="text/plain"
            )

            with st.expander("Prévia do arquivo gerado"):
                st.text_area(
                    "Conteúdo",
                    texto_unido[:10000],
                    height=400
                )

                if len(texto_unido) > 10000:
                    st.info("A prévia mostra apenas os primeiros 10.000 caracteres.")

    except zipfile.BadZipFile:
        st.error("O arquivo enviado não parece ser um ZIP válido.")
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o ZIP: {e}")
