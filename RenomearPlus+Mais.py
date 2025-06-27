import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET
from PyPDF2 import PdfReader


def extrair_nf_pdf(texto):
    """
    Extrai o número da nota fiscal de um texto de PDF, priorizando padrões específicos.

    Args:
        texto (str): O texto extraído de um PDF.

    Returns:
        tuple: Uma tupla (número da nota fiscal, nome do modelo), ou (None, None) se não for encontrado.
    """
    print("\n--- Iniciando extração de NF de PDF ---")
    # Debug de leitura de 2000 caracteres do PDF para análise
    # print(f"Texto de entrada (primeiros 2000 chars):\n{texto[:2000].replace('\\n', '\\\\n')}...")

    # NOVO CRITÉRIO: Padrão para PDFs de Marechal Cândido Rondon (PRIMEIRA PRIORIDADE)
    pattern_initial_marechal = r'PREFEITURA MUNICIPAL DE MARECHAL\s+CANDIDO RONDON'
    if re.search(pattern_initial_marechal, texto, re.IGNORECASE | re.DOTALL):
        pattern_marechal_nf = r'NOTA FISCAL ELETRÔNICA N[ºo]\s*(\d+)'
        match_marechal = re.search(
            pattern_marechal_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_marechal:
            numero_nf = match_marechal.group(1)
            return numero_nf, "Marechal Cândido Rondon"

    # NOVO CRITÉRIO: Padrão para PDFs de Londrina (SEGUNDA PRIORIDADE)
    pattern_initial_londrina = r'PREFEITURA DO MUNICÍPIO DE LONDRINA'
    if re.search(pattern_initial_londrina, texto, re.IGNORECASE | re.DOTALL):
        pattern_londrina_nf = r'Número da Nota\s*(\d+)'
        match_londrina = re.search(
            pattern_londrina_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_londrina:
            numero_nf = match_londrina.group(1)
            # Remove leading zeros if it's a long number, like 000000137121 -> 137121
            if numero_nf and len(numero_nf) > 1 and numero_nf.startswith('0'):
                numero_nf = str(int(numero_nf))
            return numero_nf, "Londrina"

    # NOVO CRITÉRIO: Padrão para PDFs de Goiânia (TERCEIRA PRIORIDADE)
    pattern_initial_goiania_1 = r'Prefeitura de Goiânia'
    pattern_initial_goiania_2 = r'Nota Fiscal de Serviços Eletrônica'
    if re.search(pattern_initial_goiania_1, texto, re.IGNORECASE) and \
            re.search(pattern_initial_goiania_2, texto, re.IGNORECASE):
        pattern_goiania_nf = r'Número da Nota\s*(\d+)'
        match_goiania = re.search(
            pattern_goiania_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_goiania:
            numero_nf = match_goiania.group(1)
            return numero_nf, "Goiânia"

    # NOVO CRITÉRIO: Padrão para PDFs de Passo Fundo (QUARTA PRIORIDADE)
    pattern_initial_passo_fundo = r'PREFEITURA MUNICIPAL DE PASSO FUNDO/RS'
    if re.search(pattern_initial_passo_fundo, texto, re.IGNORECASE | re.DOTALL):
        pattern_passo_fundo_nf = r'Número da Nota.*?(\d+)'
        match_passo_fundo = re.search(
            pattern_passo_fundo_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_passo_fundo:
            numero_nf = match_passo_fundo.group(1)
            return numero_nf, "Passo Fundo"

    # NOVO CRITÉRIO: Padrão para PDFs de Cascavel (QUINTA PRIORIDADE)
    pattern_initial_cascavel = r'MUNICÍPIO DE CASCAVEL.*?NOTA FISCAL DE SERVIÇO ELETRÔNICA'
    if re.search(pattern_initial_cascavel, texto, re.IGNORECASE | re.DOTALL):
        pattern_cascavel_nf = r'Número da NFS-e\s*(\d+)'
        match_cascavel = re.search(
            pattern_cascavel_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_cascavel:
            numero_nf = match_cascavel.group(1)
            return numero_nf, "Cascavel"

    # NOVO CRITÉRIO AJUSTADO: Padrão para PDFs de Guaraniaçu (SEXTA PRIORIDADE)
    # Busca por "Número da NFS-e" e o número, e confirma a prefeitura no resto do texto.
    pattern_guaraniacu = r'Número da NFS-e\s*(\d+).*?PREFEITURA MUNICIPAL DE GUARANIAÇU'
    match_guaraniacu = re.search(
        pattern_guaraniacu,
        texto, re.IGNORECASE | re.DOTALL)
    if match_guaraniacu:
        numero_guaraniacu = match_guaraniacu.group(1)
        return numero_guaraniacu, "Guaraniaçu"

    # NOVO CRITÉRIO: Padrão para PDFs de Ampére (SÉTIMA PRIORIDADE) - CORRIGIDO
    pattern_initial_ampere = r'PREFEITURA DA CIDADE DE AMPÉRE'
    if re.search(pattern_initial_ampere, texto, re.IGNORECASE | re.DOTALL):
        pattern_ampere_nf = r'Número da NFS-e\s*(\d+)'
        match_ampere = re.search(
            pattern_ampere_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_ampere:
            numero_nf = match_ampere.group(1)
            return numero_nf, "Ampére"

    # 1. CRITÉRIO AJUSTADO: Padrão para PDFs de Foz do Iguaçu (OITAVA PRIORIDADE ABSOLUTA) - Originalmente Sétima
    pattern_initial_foz = r'FOZ DO IGUAÇU.*?NOTA FISCAL DE SERVIÇOS ELETRÔNICA'
    if re.search(pattern_initial_foz, texto, re.IGNORECASE | re.DOTALL):
        pattern_foz_nf = r'Ativa\s*\n\s*(\d+)\s*\n\s*(\d{2}/\d{2}/(\d{4}))'
        match_foz_iguacu = re.search(
            pattern_foz_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_foz_iguacu:
            numero_nf_candidato = match_foz_iguacu.group(1)
            ano_emissao = match_foz_iguacu.group(3)

            if numero_nf_candidato.startswith(ano_emissao):
                return numero_nf_candidato, "Foz do Iguaçu"

    # 2. NOVO CRITÉRIO: Padrão para PDFs de Franca (NONA PRIORIDADE) - Originalmente Oitava
    pattern_initial_franca = r'PREFEITURA MUNICIPAL DE FRANCA.*?Nota Fiscal de Serviços Eletrônica - NFS-e'
    if re.search(pattern_initial_franca, texto, re.IGNORECASE | re.DOTALL):
        pattern_franca_nf = r'Número Nota Fiscal:\s*(\d+)\s*Data Emissão'
        match_franca = re.search(
            pattern_franca_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_franca:
            numero_nf = match_franca.group(1)
            return numero_nf, "Franca"

    # 3. NOVO CRITÉRIO: Padrão para PDFs de Garibaldi (DÉCIMA PRIORIDADE) - Originalmente Nona
    pattern_initial_garibaldi = r'MUNICÍPIO DE GARIBALDI.*?NOTA FISCAL FATURA DE SERVIÇOS ELETRÔNICA'
    if re.search(pattern_initial_garibaldi, texto, re.IGNORECASE | re.DOTALL):
        pattern_garibaldi_nf = r'Número / Série NFS-e\s*(\d+)\s*/\s*S'
        match_garibaldi = re.search(
            pattern_garibaldi_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_garibaldi:
            numero_nf = match_garibaldi.group(1)
            return numero_nf, "Garibaldi"

    # 4. Padrão para PREFEITURA MUNICIPAL DE ARARAQUARA (DÉCIMA PRIMEIRA PRIORIDADE) - Originalmente Décima
    pattern_araraquara = r'PREFEITURA MUNICIPAL DE ARARAQUARA.*?SECRETARIA MUNICIPAL DA FAZENDA\s*(\d+)'
    match_araraquara = re.search(
        pattern_araraquara,
        texto, re.IGNORECASE | re.DOTALL)
    if match_araraquara:
        numero_araraquara = match_araraquara.group(1)
        return numero_araraquara, "Araraquara"

    # 5. Padrão para PREFEITURA MUNICIPAL DE BAURU (DÉCIMA SEGUNDA PRIORIDADE) - Originalmente Décima Primeira
    pattern_bauru = r'PREFEITURA MUNICIPAL DE BAURU.*?Número Nota Fiscal:\s*(\d+)'
    match_bauru = re.search(
        pattern_bauru,
        texto, re.IGNORECASE | re.DOTALL)
    if match_bauru:
        numero_bauru = match_bauru.group(1)
        return numero_bauru, "Bauru"

    # 6. Padrão para PREFEITURA MUNICIPAL DE BELO HORIZONTE (DÉCIMA TERCEIRA PRIORIDADE) - Originalmente Décima Segunda
    pattern_bh = r'NFS-e.*?Nº:\s*\d{4}/(\d+)'
    match_bh = re.search(
        pattern_bh,
        texto, re.IGNORECASE | re.DOTALL)
    if match_bh:
        numero_bh = match_bh.group(1)
        return numero_bh, "Belo Horizonte"

    # 7. PADRÃO AJUSTADO: PREFEITURA DO MUNICIPIO DE CAMPO MAGRO (DÉCIMA QUARTA PRIORIDADE) - Originalmente Décima Terceira
    pattern_campo_magro = r'UMP5OQQBD\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2}(\d+)'
    match_campo_magro = re.search(
        pattern_campo_magro,
        texto, re.IGNORECASE | re.DOTALL)
    if match_campo_magro:
        numero_campo_magro = match_campo_magro.group(1)
        return numero_campo_magro, "Campo Magro"

    # 8. Padrão para PDFs de Capanema (DÉCIMA QUINTA PRIORIDADE) - Originalmente Décima Quarta
    pattern_initial_capanema = r'MUNICÍPIO DE CAPANEMA.*?NOTA FISCAL DE SERVIÇOS ELETRÔNICA'
    if re.search(pattern_initial_capanema, texto, re.IGNORECASE | re.DOTALL):
        pattern_capanema_nf = r'Número da Nota:\s*(\d+)'
        match_capanema = re.search(pattern_capanema_nf, texto, re.IGNORECASE)
        if match_capanema:
            numero_capanema = match_capanema.group(1)
            return numero_capanema, "Capanema"

    # 9. Padrão para DANFSe v1.0 e "Número da NFS-e" (DÉCIMA SEXTA PRIORIDADE) - Originalmente Décima Quinta
    pattern_initial_danfse = r'DANFSe v1\.0'
    if re.search(pattern_initial_danfse, texto, re.IGNORECASE | re.DOTALL):
        pattern_danfse_nf = r'N[uú]mero\s*daNFS-\s*e\s*(\d+)'
        match_nfs_e = re.search(
            pattern_danfse_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_nfs_e:
            numero_danfse = match_nfs_e.group(1)
            return numero_danfse, "DANFSe v1.0"

    # 10. Padrão para PDF da PREFEITURA MUNICIPAL DE CURITIBA (DÉCIMA SÉTIMA PRIORIDADE) - CORRIGIDO NOVAMENTE - Originalmente Décima Sexta
    pattern_curitiba = r'PREFEITURA MUNICIPAL DE CURITIBA.*?SECRETARIA MUNICIPAL DE FINANÇAS.*?NOTA FISCAL DE SERVIÇOS ELETRÔNICA - NFS-e.*?Número da Nota.*?Código de Verificação\s*(\d+)'
    match_curitiba = re.search(
        pattern_curitiba,
        texto, re.IGNORECASE | re.DOTALL)
    if match_curitiba:
        numero_curitiba = match_curitiba.group(1)
        return numero_curitiba, "Curitiba"

    # 11. Padrão para PDFs de Uberlândia (DÉCIMA OITAVA PRIORIDADE) - Originalmente Décima Sétima
    pattern_uberlandia = r'PREFEITURA DE UBERLÂNDIA.*?Número da Nota\s*(\d+)'
    match_uberlandia = re.search(
        pattern_uberlandia,
        texto, re.IGNORECASE | re.DOTALL)
    if match_uberlandia:
        numero_uberlandia = match_uberlandia.group(1)
        return numero_uberlandia, "Uberlândia"

    # 12. Padrão para PDFs de Taubaté (DÉCIMA NONA PRIORIDADE) - Originalmente Décima Oitava
    pattern_taubate = r'MUNICÍPIO DE TAUBATÉ.*?Nota N[ºo.] - S[ée]rie\s*(\d+)'
    match_taubate = re.search(
        pattern_taubate,
        texto, re.IGNORECASE | re.DOTALL)
    if match_taubate:
        numero_taubate = match_taubate.group(1)
        # REMOVE OS ZEROS DA ESQUERDA
        if numero_taubate:
            try:
                numero_taubate = str(int(numero_taubate))
            except ValueError:
                return None, "Taubaté (Inválido)"
        return numero_taubate, "Taubaté"

    # 13. NOVO CRITÉRIO: Padrão para PDFs de Realeza (VIGÉSIMA PRIORIDADE) - Originalmente Décima Nona
    pattern_realeza = r'CENTRO - Realeza - PR.*?N[UÚ]MERO\s*DA\s*NOTA\s*(\d+)'
    match_realeza = re.search(
        pattern_realeza,
        texto, re.IGNORECASE | re.DOTALL
    )
    if match_realeza:
        numero_realeza = match_realeza.group(1)
        return numero_realeza, "Realeza"

    # 14. NOVO CRITÉRIO: Padrão para PDFs de Uberaba (VIGÉSIMA PRIMEIRA PRIORIDADE)
    pattern_uberaba = r'PREFEITURA MUNICIPAL DE UBERABA'
    if re.search(pattern_uberaba, texto, re.IGNORECASE | re.DOTALL):
        return None, "Uberaba"  # Retorna None para número para não renomear

    # 15. NOVO CRITÉRIO: Padrão para PDFs de Santos (VIGÉSIMA SEGUNDA PRIORIDADE) - **AJUSTADO NOVAMENTE** - Originalmente Vigésima
    # Este padrão agora busca "NFS-e", opcionalmente "Substituída", então o número e, por fim,
    # um segundo "NFS-e" seguido por "Código de Verificação".
    pattern_initial_santos = r'PREFEITURA MUNICIPAL DE SANTOS'
    if re.search(pattern_initial_santos, texto, re.IGNORECASE | re.DOTALL):
        # PADRÃO AJUSTADO para garantir que pega o número certo, usando "Código de Verificação" como âncora
        pattern_santos_nf = r'NFS-e(?: Substituída)?\s*(\d+)\s*NFS-e\s*[\r\n]+\s*Código de Verificação'
        match_santos = re.search(
            pattern_santos_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_santos:
            numero_santos = match_santos.group(1)
            return numero_santos, "Santos"

    # 16. NOVO CRITÉRIO: Padrão para PDFs de Ubiratã (VIGÉSIMA TERCEIRA PRIORIDADE)
    # Corrigido o caractere unicode 'Ã' para 'Ã' (U+00C3)
    pattern_initial_ubirata = r'MUNICÍPIO DE UBIRATÃ'
    if re.search(pattern_initial_ubirata, texto, re.IGNORECASE | re.DOTALL):
        pattern_ubirata_nf = r'Número NFS-e:\s*(\d+)'
        match_ubirata = re.search(
            pattern_ubirata_nf,
            texto, re.IGNORECASE | re.DOTALL
        )
        if match_ubirata:
            numero_nf = match_ubirata.group(1)
            print(f"Número de NF extraído para Ubiratã: {numero_nf}") # Debug
            return numero_nf, "Ubiratã"

    # 17. Padrão genérico (fallback final):
    pattern_generico = r'N[ºo.]*\s*.*?(\d[\d\.]{5,})'
    match_generico = re.search(pattern_generico, texto, re.IGNORECASE)
    if match_generico:
        numero = match_generico.group(1).replace('.', '')
        # Adiciona uma heurística para tentar evitar CNPJs, que geralmente têm 14 dígitos
        if len(numero) == 14:
            return None, "Genérico (CNPJ-like)"
        try:
            val_numero = str(int(numero))
            return val_numero, "Genérico"
        except ValueError:
            return None, "Genérico (Inválido)"

    print("--- Extração de NF de PDF concluída: Nenhum número de nota fiscal encontrado. ---")
    return None, None


def extrair_nf_xml(caminho):
    """
    Extrai o número da nota fiscal de um arquivo XML.

    Args:
        caminho (str): O caminho completo para o arquivo XML.

    Returns:
        str: O número da nota fiscal encontrado, ou None se não for encontrado ou ocorrer um erro.
    """
    try:
        ns = {'ns': 'http://www.portalfiscal.inf.br/nfe'}
        tree = ET.parse(caminho)
        root = tree.getroot()
        nNF = root.find('.//ns:ide/ns:nNF', ns)
        return nNF.text if nNF is not None else None
    except Exception as e:
        return f"Erro ao extrair XML: {e}"


def renomear_arquivo(caminho):
    """
    Renomeia um arquivo PDF ou XML com base no número da nota fiscal extraído.

    Args:
        caminho (str): O caminho completo do arquivo a ser renomeado.

    Returns:
        dict: Um dicionário com 'message' (resultado da operação) e 'model' (modelo da nota).
    """
    ext = os.path.splitext(caminho)[1].lower()
    novo_nome = None
    modelo_nota = "Não Aplicável"  # Default para XML ou se não encontrado em PDF

    try:
        if ext == '.pdf':
            try:  # Adicionado try-except para a leitura do PDF
                with open(caminho, 'rb') as f:
                    reader = PdfReader(f)
                    texto = ''.join(p.extract_text() or '' for p in reader.pages)
                numero, modelo_nota = extrair_nf_pdf(texto)  # Agora recebe número E modelo

                # Se o modelo for Uberaba, não renomear e indicar na mensagem
                if modelo_nota == "Uberaba":
                    return {'message': f"{os.path.basename(caminho)} - Não renomeado (Modelo: Uberaba)",
                            'model': modelo_nota}

                if numero:
                    novo_nome = f"{numero}.pdf"
                else:
                    # Se o número não for encontrado, mas não for Uberaba, então é um NONE padrão
                    modelo_nota = "## NONE ##"
            except Exception as e:
                # Captura erros na leitura do PDF (e.g., PDF corrompido, protegido)
                return {'message': f"{os.path.basename(caminho)} - Erro na leitura do PDF: {e}", 'model': "## NONE ##"}

        elif ext == '.xml':
            numero = extrair_nf_xml(caminho)
            if numero:
                novo_nome = f"{numero}.xml"
            else:
                modelo_nota = "## NONE ##"  # Define como ## NONE ## se o número não for encontrado
            # Para XML, o modelo permanece "Não Aplicável" se não houver erro
            # O erro de extração já retorna "## NONE ##"

        if novo_nome:
            diretorio = os.path.dirname(caminho)
            novo_caminho = os.path.join(diretorio, novo_nome)
            if not os.path.exists(novo_caminho):
                os.rename(caminho, novo_caminho)
                return {'message': f"{os.path.basename(caminho)} ➜ {novo_nome}", 'model': modelo_nota}
            else:
                return {'message': f"{os.path.basename(caminho)} - já existe como {novo_nome}", 'model': modelo_nota}
        else:
            # Caso o número não seja encontrado e não haja erro na leitura (para PDF)
            # ou para XML onde o número não foi encontrado. Este é o caso padrão para "número não encontrado"
            # O caso Uberaba já foi tratado acima.
            return {'message': f"{os.path.basename(caminho)} - número não encontrado", 'model': modelo_nota}
    except Exception as e:
        # Captura erros gerais de renomeação ou outros
        return {'message': f"{os.path.basename(caminho)} - erro geral: {e}", 'model': "## NONE ##"}


# --- Funções da GUI ---
def selecionar_arquivos_gui():
    """
    Abre uma caixa de diálogo para o usuário selecionar múltiplos arquivos PDF ou XML.
    Atualiza o campo de entrada na GUI com os caminhos dos arquivos selecionados.
    """
    caminhos = filedialog.askopenfilenames(filetypes=[
        ("Arquivos de Nota Fiscal (PDF/XML)", "*.pdf *.xml"),
        ("Documentos PDF", "*.pdf"),
        ("Arquivos XML", "*.xml")
    ])
    if caminhos:
        # Limpa o Treeview
        for i in tree.get_children():
            tree.delete(i)
        # O entry_arquivos continua sendo usado internamente para armazenar os caminhos completos
        # Não precisamos limpar ele se a seleção for para um novo conjunto de arquivos.
        entry_arquivos.set(";".join(caminhos))  # Usando set para StringVar

        # Adiciona os nomes dos arquivos ao Treeview com status inicial e modelo vazio
        for caminho in caminhos:
            tree.insert("", "end", values=(os.path.basename(caminho), "Aguardando...", ""),
                        tags=('normal',))  # Adiciona uma tag padrão
        # Atualiza a barra de status
        status_var.set(f"{len(caminhos)} arquivo(s) selecionado(s). Clique em 'Renomear'.")


def iniciar_renomeacao_gui():
    """
    Inicia o processo de renomeação para os arquivos selecionados na GUI.
    Atualiza o Treeview e a barra de status.
    """
    caminhos_str = entry_arquivos.get()  # Obtém os caminhos da StringVar
    if not caminhos_str:
        status_var.set("Aviso: Nenhum arquivo selecionado para renomear.")
        return

    caminhos = caminhos_str.split(';')

    # Atualiza a barra de status e barra de progresso
    status_var.set("Iniciando renomeação...")
    progress_bar["maximum"] = len(caminhos)
    progress_bar["value"] = 0
    janela.update_idletasks()  # Força a atualização da GUI

    # Desabilita botões durante o processamento
    btn_selecionar.config(state=tk.DISABLED)
    btn_renomear.config(state=tk.DISABLED)

    # Limpa seleções anteriores do Treeview
    for item in tree.selection():
        tree.selection_remove(item)

    for i, caminho in enumerate(caminhos):
        # Garante que o item correspondente no treeview exista
        if i < len(tree.get_children()):
            item_id = tree.get_children()[i]
        else:
            # Caso algum erro ocorra na seleção inicial e o item não esteja no treeview
            # Insere com status de erro e modelo N/A
            tree.insert("", "end", values=(os.path.basename(caminho),
                                           f"Erro: Arquivo {os.path.basename(caminho)} não encontrado na lista inicial.",
                                           "## NONE ##"), tags=('error',))  # Aplica a tag de erro
            item_id = tree.get_children()[-1]

        if os.path.isfile(caminho):
            resultado_dict = renomear_arquivo(caminho)
            tags_to_apply = ('normal',)  # Tag padrão
            # Condição para aplicar a tag de erro (vermelho)
            if resultado_dict['model'] == "## NONE ##" or \
                    "erro" in resultado_dict['message'].lower() or \
                    resultado_dict['model'] == "Uberaba":  # Adicionada a condição para Uberaba
                tags_to_apply = ('error',)  # Aplica a tag de erro
            # Atualiza o item do Treeview com a mensagem e o modelo e as tags
            tree.item(item_id, values=(os.path.basename(caminho), resultado_dict['message'], resultado_dict['model']),
                      tags=tags_to_apply)
            tree.see(item_id)  # Garante que o item esteja visível na lista
        else:
            # Se o arquivo não for encontrado no disco
            tree.item(item_id, values=(os.path.basename(caminho), "Erro: Arquivo não encontrado", "## NONE ##"),
                      tags=('error',))  # Aplica a tag de erro

        # Atualiza a barra de progresso
        progress_bar["value"] = i + 1
        janela.update_idletasks()  # Força a atualização da GUI

    # messagebox.showinfo("Resultados da Renomeação", "\n".join(resultados)) # REMOVIDO!
    entry_arquivos.set("")  # Limpa a StringVar interna de caminhos
    status_var.set("Processo de renomeação concluído.")
    progress_bar["value"] = 0  # Reseta a barra de progresso

    # Reabilita botões após o processamento
    btn_selecionar.config(state=tk.NORMAL)
    btn_renomear.config(state=tk.NORMAL)


# --- Interface gráfica (Tkinter) ---
janela = tk.Tk()
janela.title("Renomeador de NF-e (PDF e XML)")
janela.geometry("750x500")  # Aumenta a altura e largura inicial
janela.resizable(True, True)

# Define o tamanho mínimo da janela (largura, altura)
# Aumentei a altura para acomodar todos os elementos.
janela.minsize(width=680, height=450)

# Aplicar um tema Tkinter
style = ttk.Style()
style.theme_use("clam")  # Experimente "clam", "alt", "default", "classic", "vista", "xpnative" (Windows)

# Configurações de cores e fontes
cor_fundo = "#f0f0f0"  # Cinza claro
cor_primaria = "#4CAF50"  # Verde (para botões de ação)
cor_secundaria = "#1E88E5"  # Azul (para botões de seleção)
fonte_titulo = ("Arial", 14, "bold")
fonte_padrao = ("Arial", 10)
fonte_pequena = ("Arial", 8)  # Nova fonte para barra de status, se desejar

janela.configure(bg=cor_fundo)  # Define a cor de fundo da janela

# --- Frame principal para conter todos os outros frames, para melhor organização do layout ---
main_frame = ttk.Frame(janela, padding="15")  # Adiciona padding geral
main_frame.pack(fill=tk.BOTH, expand=True)

# --- Frame de Seleção de Arquivos ---
frame_selecao = ttk.LabelFrame(main_frame, text=" 1. Selecione os Arquivos ", padding="10")
frame_selecao.pack(padx=0, pady=(0, 10), fill=tk.X, expand=False)

ttk.Label(frame_selecao, text="Clique no botão abaixo para selecionar arquivos PDF/XML:").pack(pady=(0, 5))

# O entry_arquivos agora é uma StringVar interna, não um widget visível.
entry_arquivos = tk.StringVar()
# entry_arquivos = ttk.Entry(frame_selecao) # Não é mais necessário criar o widget Entry aqui.

btn_selecionar = ttk.Button(frame_selecao, text="Procurar Arquivos...", command=selecionar_arquivos_gui,
                            style="Accent.TButton")
btn_selecionar.pack(pady=5, fill=tk.X, expand=True)

# --- Treeview para exibir os resultados ---
frame_resultados = ttk.LabelFrame(main_frame, text=" 2. Status da Renomeação ", padding="10")
frame_resultados.pack(padx=0, pady=(0, 10), fill=tk.BOTH, expand=True)

# Usando grid para o Treeview e as Scrollbars DENTRO do frame_resultados
# ATUALIZADO: Adicionada a coluna "Modelo"
tree = ttk.Treeview(frame_resultados, columns=("Arquivo", "Status", "Modelo"), show="headings")
tree.heading("Arquivo", text="Nome do Arquivo", anchor="w")
tree.heading("Status", text="Status da Renomeação", anchor="w")
tree.heading("Modelo", text="Modelo da Nota", anchor="w")  # Nova coluna para o modelo
tree.column("Arquivo", width=250, stretch=tk.YES)
tree.column("Status", width=250, stretch=tk.YES)
tree.column("Modelo", width=150, stretch=tk.YES)  # Largura para a nova coluna

# Definir as tags para cores (ADICIONADO)
tree.tag_configure('error', foreground='red')
tree.tag_configure('normal', foreground='black')  # Tag para texto normal

scrollbar_y = ttk.Scrollbar(frame_resultados, orient="vertical", command=tree.yview)
scrollbar_x = ttk.Scrollbar(frame_resultados, orient="horizontal", command=tree.xview)
tree.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

# Posicionando Treeview e Scrollbars com grid
tree.grid(row=0, column=0, sticky="nsew")
scrollbar_y.grid(row=0, column=1, sticky="ns")
scrollbar_x.grid(row=1, column=0, sticky="ew")

# Configurações de redimensionamento do grid para o frame_resultados
frame_resultados.grid_rowconfigure(0, weight=1)  # Faz o treeview expandir verticalmente
frame_resultados.grid_columnconfigure(0, weight=1)  # Faz o treeview expandir horizontalmente

# --- Botão de Renomear ---
frame_botao_renomear = ttk.Frame(main_frame, padding="0")  # Sem padding interno, controlado pelo pack
frame_botao_renomear.pack(padx=0, pady=(0, 10), fill=tk.X, expand=False)

btn_renomear = ttk.Button(frame_botao_renomear, text="3. Renomear Arquivos Selecionados",
                          command=iniciar_renomeacao_gui, style="CallToAction.TButton")
btn_renomear.pack(fill=tk.X, expand=True)

# --- Barra de Progresso ---
progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=100, mode="determinate")
progress_bar.pack(fill=tk.X, padx=0, pady=(0, 5))

# --- Status Bar ---
status_var = tk.StringVar()
status_var.set("Aguardando seleção de arquivos...")
status_bar = ttk.Label(janela, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W, font=fonte_padrao)
status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

# --- Estilos personalizados para os botões ---
style.configure("Accent.TButton", font=fonte_padrao, background=cor_secundaria, foreground="white")
style.map("Accent.TButton", background=[('active', '#2196F3'), ('disabled', '#BBDEFB')])

style.configure("CallToAction.TButton", font=fonte_titulo, background=cor_primaria, foreground="white")
style.map("CallToAction.TButton", background=[('active', '#66BB6A'), ('disabled', '#A5D6A7')])

janela.mainloop()
