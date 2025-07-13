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

    # Padrão para PDFs de Marechal Cândido Rondon (PRIMEIRA PRIORIDADE)
    pattern_initial_marechal = r'PREFEITURA MUNICIPAL DE MARECHAL\s+CANDIDO RONDON'
    if re.search(pattern_initial_marechal, texto, re.IGNORECASE | re.DOTALL):
        pattern_marechal_nf = r'NOTA FISCAL ELETRÔNICA N[º°o]\s*(\d+)'
        match_marechal = re.search(pattern_marechal_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_marechal:
            return match_marechal.group(1), "Marechal Cândido Rondon"

    # Padrão para PDFs de Londrina (SEGUNDA PRIORIDADE)
    pattern_initial_londrina = r'PREFEITURA DO MUNICÍPIO DE LONDRINA'
    if re.search(pattern_initial_londrina, texto, re.IGNORECASE | re.DOTALL):
        pattern_londrina_nf = r'Número da Nota\s*(\d+)'
        match_londrina = re.search(pattern_londrina_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_londrina:
            numero_nf = match_londrina.group(1)
            if numero_nf and len(numero_nf) > 1 and numero_nf.startswith('0'):
                numero_nf = str(int(numero_nf))
            return numero_nf, "Londrina"

    # Padrão para PDFs de Goiânia (TERCEIRA PRIORIDADE)
    pattern_initial_goiania_1 = r'Prefeitura de Goiânia'
    pattern_initial_goiania_2 = r'Nota Fiscal de Serviços Eletrônica'
    if re.search(pattern_initial_goiania_1, texto, re.IGNORECASE) and re.search(pattern_initial_goiania_2, texto, re.IGNORECASE):
        pattern_goiania_nf = r'Número da Nota\s*(\d+)'
        match_goiania = re.search(pattern_goiania_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_goiania:
            return match_goiania.group(1), "Goiânia"

    # Padrão para PDFs de Passo Fundo (QUARTA PRIORIDADE)
    pattern_initial_passo_fundo = r'PREFEITURA MUNICIPAL DE PASSO FUNDO/RS'
    if re.search(pattern_initial_passo_fundo, texto, re.IGNORECASE | re.DOTALL):
        pattern_passo_fundo_nf = r'Número da Nota.*?(\d+)'
        match_passo_fundo = re.search(pattern_passo_fundo_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_passo_fundo:
            return match_passo_fundo.group(1), "Passo Fundo"

    # Padrão para PDFs de Cascavel (QUINTA PRIORIDADE)
    pattern_initial_cascavel = r'MUNICÍPIO DE CASCAVEL.*?NOTA FISCAL DE SERVIÇO ELETRÔNICA'
    if re.search(pattern_initial_cascavel, texto, re.IGNORECASE | re.DOTALL):
        pattern_cascavel_nf = r'Número da NFS-e\s*(\d+)'
        match_cascavel = re.search(pattern_cascavel_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_cascavel:
            return match_cascavel.group(1), "Cascavel"

    # Padrão para PDFs de Guaraniaçu (SEXTA PRIORIDADE)
    pattern_guaraniacu = r'Número da NFS-e\s*(\d+).*?PREFEITURA MUNICIPAL DE GUARANIAÇU'
    match_guaraniacu = re.search(pattern_guaraniacu, texto, re.IGNORECASE | re.DOTALL)
    if match_guaraniacu:
        return match_guaraniacu.group(1), "Guaraniaçu"

    # Padrão para PDFs de Ampére (SÉTIMA PRIORIDADE)
    pattern_initial_ampere = r'PREFEITURA DA CIDADE DE AMPÉRE'
    if re.search(pattern_initial_ampere, texto, re.IGNORECASE | re.DOTALL):
        pattern_ampere_nf = r'Número da NFS-e\s*(\d+)'
        match_ampere = re.search(pattern_ampere_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_ampere:
            return match_ampere.group(1), "Ampére"

    # Padrão para PDFs de Foz do Iguaçu (OITAVA PRIORIDADE)
    pattern_initial_foz = r'FOZ DO IGUAÇU.*?NOTA FISCAL DE SERVIÇOS ELETRÔNICA'
    if re.search(pattern_initial_foz, texto, re.IGNORECASE | re.DOTALL):
        pattern_foz_nf = r'Ativa\s*\n\s*(\d+)\s*\n\s*(\d{2}/\d{2}/(\d{4}))'
        match_foz_iguacu = re.search(pattern_foz_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_foz_iguacu:
            numero_nf_candidato = match_foz_iguacu.group(1)
            ano_emissao = match_foz_iguacu.group(3)
            if numero_nf_candidato.startswith(ano_emissao):
                return numero_nf_candidato, "Foz do Iguaçu"

    # Padrão para PDFs de Franca (NONA PRIORIDADE)
    pattern_initial_franca = r'PREFEITURA MUNICIPAL DE FRANCA.*?Nota Fiscal de Serviços Eletrônica - NFS-e'
    if re.search(pattern_initial_franca, texto, re.IGNORECASE | re.DOTALL):
        pattern_franca_nf = r'Número Nota Fiscal:\s*(\d+)\s*Data Emissão'
        match_franca = re.search(pattern_franca_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_franca:
            return match_franca.group(1), "Franca"

    # Padrão para PDFs de Garibaldi (DÉCIMA PRIORIDADE)
    pattern_initial_garibaldi = r'MUNICÍPIO DE GARIBALDI.*?NOTA FISCAL FATURA DE SERVIÇOS ELETRÔNICA'
    if re.search(pattern_initial_garibaldi, texto, re.IGNORECASE | re.DOTALL):
        pattern_garibaldi_nf = r'Número / Série NFS-e\s*(\d+)\s*/\s*S'
        match_garibaldi = re.search(pattern_garibaldi_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_garibaldi:
            return match_garibaldi.group(1), "Garibaldi"

    # Padrão para PREFEITURA MUNICIPAL DE ARARAQUARA (DÉCIMA PRIMEIRA PRIORIDADE)
    pattern_araraquara = r'PREFEITURA MUNICIPAL DE ARARAQUARA.*?SECRETARIA MUNICIPAL DA FAZENDA\s*(\d+)'
    match_araraquara = re.search(pattern_araraquara, texto, re.IGNORECASE | re.DOTALL)
    if match_araraquara:
        return match_araraquara.group(1), "Araraquara"

    # Padrão para PREFEITURA MUNICIPAL DE BAURU (DÉCIMA SEGUNDA PRIORIDADE)
    pattern_bauru = r'PREFEITURA MUNICIPAL DE BAURU.*?Número Nota Fiscal:\s*(\d+)'
    match_bauru = re.search(pattern_bauru, texto, re.IGNORECASE | re.DOTALL)
    if match_bauru:
        return match_bauru.group(1), "Bauru"

    # Padrão para PREFEITURA MUNICIPAL DE BELO HORIZONTE (DÉCIMA TERCEIRA PRIORIDADE)
    pattern_bh = r'NFS-e.*?N[º°o]:\s*\d{4}/(\d+)'
    match_bh = re.search(pattern_bh, texto, re.IGNORECASE | re.DOTALL)
    if match_bh:
        return match_bh.group(1), "Belo Horizonte"

    # Padrão para PREFEITURA DO MUNICIPIO DE CAMPO MAGRO (DÉCIMA QUARTA PRIORIDADE)
    pattern_campo_magro = r'UMP5OQQBD\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2}(\d+)'
    match_campo_magro = re.search(pattern_campo_magro, texto, re.IGNORECASE | re.DOTALL)
    if match_campo_magro:
        return match_campo_magro.group(1), "Campo Magro"

    # Padrão para PDFs de Capanema (DÉCIMA QUINTA PRIORIDADE)
    pattern_initial_capanema = r'MUNICÍPIO DE CAPANEMA.*?NOTA FISCAL DE SERVIÇOS ELETRÔNICA'
    if re.search(pattern_initial_capanema, texto, re.IGNORECASE | re.DOTALL):
        pattern_capanema_nf = r'Número da Nota:\s*(\d+)'
        match_capanema = re.search(pattern_capanema_nf, texto, re.IGNORECASE)
        if match_capanema:
            return match_capanema.group(1), "Capanema"

    # Padrão para DANFSe v1.0 (DÉCIMA SEXTA PRIORIDADE)
    pattern_initial_danfse = r'DANFSe v1\.0'
    if re.search(pattern_initial_danfse, texto, re.IGNORECASE | re.DOTALL):
        pattern_danfse_nf = r'N[uú]mero\s*daNFS-\s*e\s*(\d+)'
        match_nfs_e = re.search(pattern_danfse_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_nfs_e:
            return match_nfs_e.group(1), "DANFSe v1.0"

    # Padrão para PDF da PREFEITURA MUNICIPAL DE CURITIBA (DÉCIMA SÉTIMA PRIORIDADE) - ROBUSTO
    # Tenta o primeiro layout de Curitiba (número após "Número da Nota")
    pattern_curitiba_A = r'PREFEITURA MUNICIPAL DE CURITIBA.*?Número da Nota\s+(\d+)'
    match_curitiba = re.search(pattern_curitiba_A, texto, re.IGNORECASE | re.DOTALL)
    if match_curitiba:
        return match_curitiba.group(1), "Curitiba (Layout 1)"

    # Se o primeiro falhar, tenta o segundo layout (número após "Código de Verificação")
    pattern_curitiba_B = r'PREFEITURA MUNICIPAL DE CURITIBA.*?Código de Verificação\s*(\d+)'
    match_curitiba = re.search(pattern_curitiba_B, texto, re.IGNORECASE | re.DOTALL)
    if match_curitiba:
        return match_curitiba.group(1), "Curitiba (Layout 2)"

    # Padrão para PDFs de Uberlândia (DÉCIMA OITAVA PRIORIDADE)
    pattern_uberlandia = r'PREFEITURA DE UBERLÂNDIA.*?Número da Nota\s*(\d+)'
    match_uberlandia = re.search(pattern_uberlandia, texto, re.IGNORECASE | re.DOTALL)
    if match_uberlandia:
        return match_uberlandia.group(1), "Uberlândia"

    # Padrão para PDFs de Taubaté (DÉCIMA NONA PRIORIDADE) - CORREÇÃO FINAL
    pattern_taubate = r'MUNICÍPIO DE TAUBATÉ.*?Nota N[º°o]\.?\s*-?\s*S[ée]rie\s+(\d+)'
    match_taubate = re.search(pattern_taubate, texto, re.IGNORECASE | re.DOTALL)
    if match_taubate:
        numero_taubate = match_taubate.group(1)
        if numero_taubate:
            try:
                numero_taubate = str(int(numero_taubate))
            except ValueError:
                return None, "Taubaté (Inválido)"
            return numero_taubate, "Taubaté"

    # Padrão para PDFs de Realeza (VIGÉSIMA PRIORIDADE)
    pattern_realeza = r'CENTRO - Realeza - PR.*?N[UÚ]MERO\s*DA\s*NOTA\s*(\d+)'
    match_realeza = re.search(pattern_realeza, texto, re.IGNORECASE | re.DOTALL)
    if match_realeza:
        return match_realeza.group(1), "Realeza"

    # Padrão para PDFs de Uberaba (VIGÉSIMA PRIMEIRA PRIORIDADE)
    pattern_uberaba = r'PREFEITURA MUNICIPAL DE UBERABA'
    if re.search(pattern_uberaba, texto, re.IGNORECASE | re.DOTALL):
        return None, "Uberaba"

    # Padrão para PDFs de Santos (VIGÉSIMA SEGUNDA PRIORIDADE)
    pattern_initial_santos = r'PREFEITURA MUNICIPAL DE SANTOS'
    if re.search(pattern_initial_santos, texto, re.IGNORECASE | re.DOTALL):
        pattern_santos_nf = r'NFS-e(?: Substituída)?\s*(\d+)\s*NFS-e\s*[\r\n]+\s*Código de Verificação'
        match_santos = re.search(pattern_santos_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_santos:
            return match_santos.group(1), "Santos"

    # Padrão para PDFs de Ubiratã (VIGÉSIMA TERCEIRA PRIORIDADE)
    pattern_initial_ubirata = r'MUNICÍPIO DE UBIRATÃ'
    if re.search(pattern_initial_ubirata, texto, re.IGNORECASE | re.DOTALL):
        pattern_ubirata_nf = r'Número NFS-e:\s*(\d+)'
        match_ubirata = re.search(pattern_ubirata_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_ubirata:
            return match_ubirata.group(1), "Ubiratã"

    # Padrão para DANFE Padrão (VIGÉSIMA QUARTA PRIORIDADE) - VALIDADO
    pattern_danfe_id_1 = r'DANFE'
    pattern_danfe_id_2 = r'Documento Auxiliar da Nota\s+Fiscal Eletrônica'
    if re.search(pattern_danfe_id_1, texto, re.IGNORECASE) and re.search(pattern_danfe_id_2, texto, re.IGNORECASE):
        pattern_danfe_nf = r'N[º°o]\.\s*([\d\.]+)\s+Série'
        match_danfe = re.search(pattern_danfe_nf, texto, re.IGNORECASE | re.DOTALL)
        if match_danfe:
            numero_nf = match_danfe.group(1)
            numero_sem_pontos = numero_nf.replace('.', '')
            try:
                numero_final = str(int(numero_sem_pontos))
                return numero_final, "DANFE Padrão (OK)"
            except ValueError:
                return numero_nf, "DANFE Padrão (Falha na Limpeza)"

    # Padrão genérico (fallback final):
    pattern_generico = r'N[º°o.]*\s*.*?(\d[\d\.]{5,})'
    match_generico = re.search(pattern_generico, texto, re.IGNORECASE)
    if match_generico:
        numero = match_generico.group(1).replace('.', '')
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
    """
    ext = os.path.splitext(caminho)[1].lower()
    novo_nome = None
    modelo_nota = "Não Aplicável"
    try:
        if ext == '.pdf':
            try:
                with open(caminho, 'rb') as f:
                    reader = PdfReader(f)
                    texto = ''.join(p.extract_text() or '' for p in reader.pages)
                numero, modelo_nota = extrair_nf_pdf(texto)
                if modelo_nota == "Uberaba":
                    return {'message': f"{os.path.basename(caminho)} - Não renomeado (Modelo: Uberaba)",
                            'model': modelo_nota}
                if numero:
                    novo_nome = f"{numero}.pdf"
                else:
                    modelo_nota = "## NONE ##"
            except Exception as e:
                return {'message': f"{os.path.basename(caminho)} - Erro na leitura do PDF: {e}", 'model': "## NONE ##"}
        elif ext == '.xml':
            numero = extrair_nf_xml(caminho)
            if numero:
                novo_nome = f"{numero}.xml"
            else:
                modelo_nota = "## NONE ##"

        if novo_nome:
            diretorio = os.path.dirname(caminho)
            novo_caminho = os.path.join(diretorio, novo_nome)
            if not os.path.exists(novo_caminho):
                os.rename(caminho, novo_caminho)
                return {'message': f"{os.path.basename(caminho)} ➜ {novo_nome}", 'model': modelo_nota}
            else:
                return {'message': f"{os.path.basename(caminho)} - já existe como {novo_nome}", 'model': modelo_nota}
        else:
            return {'message': f"{os.path.basename(caminho)} - número não encontrado", 'model': modelo_nota}
    except Exception as e:
        return {'message': f"{os.path.basename(caminho)} - erro geral: {e}", 'model': "## NONE ##"}


# --- Funções da GUI ---
def selecionar_arquivos_gui():
    """
    Abre uma caixa de diálogo para o usuário selecionar múltiplos arquivos PDF ou XML.
    """
    caminhos = filedialog.askopenfilenames(filetypes=[
        ("Arquivos de Nota Fiscal (PDF/XML)", "*.pdf *.xml"),
        ("Documentos PDF", "*.pdf"),
        ("Arquivos XML", "*.xml")
    ])
    if caminhos:
        for i in tree.get_children():
            tree.delete(i)
        entry_arquivos.set(";".join(caminhos))
        for caminho in caminhos:
            tree.insert("", "end", values=(os.path.basename(caminho), "Aguardando...", ""), tags=('normal',))
        status_var.set(f"{len(caminhos)} arquivo(s) selecionado(s). Clique em 'Renomear'.")


def iniciar_renomeacao_gui():
    """
    Inicia o processo de renomeação para os arquivos selecionados na GUI.
    """
    caminhos_str = entry_arquivos.get()
    if not caminhos_str:
        status_var.set("Aviso: Nenhum arquivo selecionado para renomear.")
        return
    caminhos = caminhos_str.split(';')
    status_var.set("Iniciando renomeação...")
    progress_bar["maximum"] = len(caminhos)
    progress_bar["value"] = 0
    janela.update_idletasks()

    btn_selecionar.config(state=tk.DISABLED)
    btn_renomear.config(state=tk.DISABLED)

    for i, caminho in enumerate(caminhos):
        if i < len(tree.get_children()):
            item_id = tree.get_children()[i]
            if os.path.isfile(caminho):
                resultado_dict = renomear_arquivo(caminho)
                tags_to_apply = ('normal',)
                if resultado_dict['model'] == "## NONE ##" or \
                        "erro" in resultado_dict['message'].lower() or \
                        resultado_dict['model'] == "Uberaba":
                    tags_to_apply = ('error',)
                tree.item(item_id, values=(os.path.basename(caminho), resultado_dict['message'], resultado_dict['model']),
                          tags=tags_to_apply)
                tree.see(item_id)
            else:
                tree.item(item_id, values=(os.path.basename(caminho), "Erro: Arquivo não encontrado", "## NONE ##"),
                          tags=('error',))

        progress_bar["value"] = i + 1
        janela.update_idletasks()

    entry_arquivos.set("")
    status_var.set("Processo de renomeação concluído.")
    progress_bar["value"] = 0

    btn_selecionar.config(state=tk.NORMAL)
    btn_renomear.config(state=tk.NORMAL)


# --- Interface gráfica (Tkinter) ---
janela = tk.Tk()
janela.title("Renomeador de NF-e (PDF e XML)")
janela.geometry("750x500")
janela.resizable(True, True)
janela.minsize(width=680, height=450)

style = ttk.Style()
style.theme_use("clam")

cor_fundo = "#f0f0f0"
cor_primaria = "#4CAF50"
cor_secundaria = "#1E88E5"
fonte_titulo = ("Arial", 14, "bold")
fonte_padrao = ("Arial", 10)

janela.configure(bg=cor_fundo)

main_frame = ttk.Frame(janela, padding="15")
main_frame.pack(fill=tk.BOTH, expand=True)

frame_selecao = ttk.LabelFrame(main_frame, text=" 1. Selecione os Arquivos ", padding="10")
frame_selecao.pack(padx=0, pady=(0, 10), fill=tk.X, expand=False)

ttk.Label(frame_selecao, text="Clique no botão abaixo para selecionar arquivos PDF/XML:").pack(pady=(0, 5))
entry_arquivos = tk.StringVar()
btn_selecionar = ttk.Button(frame_selecao, text="Procurar Arquivos...", command=selecionar_arquivos_gui,
                             style="Accent.TButton")
btn_selecionar.pack(pady=5, fill=tk.X, expand=True)

frame_resultados = ttk.LabelFrame(main_frame, text=" 2. Status da Renomeação ", padding="10")
frame_resultados.pack(padx=0, pady=(0, 10), fill=tk.BOTH, expand=True)

tree = ttk.Treeview(frame_resultados, columns=("Arquivo", "Status", "Modelo"), show="headings")
tree.heading("Arquivo", text="Nome do Arquivo", anchor="w")
tree.heading("Status", text="Status da Renomeação", anchor="w")
tree.heading("Modelo", text="Modelo da Nota", anchor="w")
tree.column("Arquivo", width=250, stretch=tk.YES)
tree.column("Status", width=250, stretch=tk.YES)
tree.column("Modelo", width=150, stretch=tk.YES)

tree.tag_configure('error', foreground='red')
tree.tag_configure('normal', foreground='black')

scrollbar_y = ttk.Scrollbar(frame_resultados, orient="vertical", command=tree.yview)
scrollbar_x = ttk.Scrollbar(frame_resultados, orient="horizontal", command=tree.xview)
tree.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scrollbar_y.grid(row=0, column=1, sticky="ns")
scrollbar_x.grid(row=1, column=0, sticky="ew")

frame_resultados.grid_rowconfigure(0, weight=1)
frame_resultados.grid_columnconfigure(0, weight=1)

frame_botao_renomear = ttk.Frame(main_frame, padding="0")
frame_botao_renomear.pack(padx=0, pady=(0, 10), fill=tk.X, expand=False)
btn_renomear = ttk.Button(frame_botao_renomear, text="3. Renomear Arquivos Selecionados",
                          command=iniciar_renomeacao_gui, style="CallToAction.TButton")
btn_renomear.pack(fill=tk.X, expand=True)

progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=100, mode="determinate")
progress_bar.pack(fill=tk.X, padx=0, pady=(0, 5))

status_var = tk.StringVar()
status_var.set("Aguardando seleção de arquivos...")
status_bar = ttk.Label(janela, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W, font=fonte_padrao)
status_bar.pack(side=tk.BOTTOM, fill=tk.X, expand=False)

style.configure("Accent.TButton", font=fonte_padrao, background=cor_secundaria, foreground="white")
style.map("Accent.TButton", background=[('active', '#2196F3'), ('disabled', '#BBDEFB')])
style.configure("CallToAction.TButton", font=fonte_titulo, background=cor_primaria, foreground="white")
style.map("CallToAction.TButton", background=[('active', '#66BB6A'), ('disabled', '#A5D6A7')])

janela.mainloop()
