"""Interface gráfica do Capturador de Imagens."""

import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from compressor import comprimir_imagem, FORMATOS_SAIDA
from file_handler import selecionar_arquivos, selecionar_pasta, selecionar_destino


class ImageCompressorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Capturador de Imagens")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        self.arquivos = []
        self.pasta_destino = None

        self._construir_interface()

    def _construir_interface(self):
        """Constrói todos os widgets da interface."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === SEÇÃO ORIGEM ===
        origem_frame = ttk.LabelFrame(main_frame, text="Origem", padding="5")
        origem_frame.pack(fill=tk.X, pady=(0, 10))

        btn_frame = ttk.Frame(origem_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Adicionar Imagens",
                   command=self._adicionar_imagens).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Adicionar Pasta",
                   command=self._adicionar_pasta).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Remover Selecionados",
                   command=self._remover_selecionados).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Limpar Lista",
                   command=self._limpar_lista).pack(side=tk.RIGHT)

        # Lista de arquivos
        list_frame = ttk.Frame(origem_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lista_arquivos = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                         selectmode=tk.EXTENDED, height=8,
                                         bg='white', fg='black',
                                         selectbackground='#4a9eff', selectforeground='white')
        self.lista_arquivos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_arquivos.yview)

        self.lista_arquivos.bind('<<ListboxSelect>>', self._on_select)

        # === SEÇÃO PRÉ-VISUALIZAÇÃO ===
        preview_frame = ttk.LabelFrame(main_frame, text="Pré-visualização", padding="5")
        preview_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_preview = ttk.Label(preview_frame, text="Selecione uma imagem para visualizar")
        self.lbl_preview.pack(fill=tk.X)

        # === SEÇÃO DESTINO ===
        destino_frame = ttk.LabelFrame(main_frame, text="Destino", padding="5")
        destino_frame.pack(fill=tk.X, pady=(0, 10))

        destino_row = ttk.Frame(destino_frame)
        destino_row.pack(fill=tk.X)

        self.lbl_destino = ttk.Label(destino_row, text="Nenhuma pasta selecionada")
        self.lbl_destino.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(destino_row, text="Escolher Pasta",
                   command=self._escolher_destino).pack(side=tk.RIGHT)

        self.var_subpasta = tk.BooleanVar(value=True)
        ttk.Checkbutton(destino_frame, text="Criar subpasta nomeada (comprimido_DATA_HORA)",
                        variable=self.var_subpasta).pack(anchor=tk.W, pady=(5, 0))

        # === SEÇÃO CONFIGURAÇÕES ===
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(config_frame, text="Tamanho máximo (MB):").grid(row=0, column=0, sticky=tk.W)
        self.entry_tamanho = ttk.Entry(config_frame, width=10)
        self.entry_tamanho.insert(0, "1.0")
        self.entry_tamanho.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))

        ttk.Label(config_frame, text="Formato de saída:").grid(row=0, column=2, sticky=tk.W)
        self.combo_formato = ttk.Combobox(config_frame, values=FORMATOS_SAIDA,
                                          state="readonly", width=8)
        self.combo_formato.set("WebP")
        self.combo_formato.grid(row=0, column=3, sticky=tk.W, padx=(5, 20))

        self.var_manter_ext = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Manter extensão original",
                        variable=self.var_manter_ext).grid(row=0, column=4, sticky=tk.W)

        # === SEÇÃO AÇÃO ===
        acao_frame = ttk.Frame(main_frame)
        acao_frame.pack(fill=tk.X, pady=(0, 5))

        self.btn_comprimir = ttk.Button(acao_frame, text="COMPRIMIR",
                                        command=self._comprimir)
        self.btn_comprimir.pack(fill=tk.X)

        self.progresso = ttk.Progressbar(main_frame, mode='determinate')
        self.progresso.pack(fill=tk.X, pady=(5, 0))

        self.lbl_status = ttk.Label(main_frame, text="Pronto")
        self.lbl_status.pack(fill=tk.X, pady=(5, 0))

    def _on_select(self, event):
        """Atualiza pré-visualização quando seleciona um item."""
        selection = self.lista_arquivos.curselection()
        if selection:
            index = selection[0]
            if index < len(self.arquivos):
                caminho = self.arquivos[index]
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(caminho)
                    img.thumbnail((200, 150))
                    photo = ImageTk.PhotoImage(img)
                    self.lbl_preview.config(image=photo, text="")
                    self.lbl_preview.image = photo
                except Exception:
                    self.lbl_preview.config(image="", text="Pré-visualização indisponível")
        else:
            self.lbl_preview.config(image="", text="Selecione uma imagem para visualizar")

    def _adicionar_imagens(self):
        arquivos = selecionar_arquivos()
        for arq in arquivos:
            if arq not in self.arquivos:
                self.arquivos.append(arq)
                tamanho = os.path.getsize(arq) / (1024 * 1024)
                self.lista_arquivos.insert(tk.END, f"{os.path.basename(arq)}  ({tamanho:.1f} MB)")

    def _adicionar_pasta(self):
        arquivos = selecionar_pasta()
        for arq in arquivos:
            if arq not in self.arquivos:
                self.arquivos.append(arq)
                tamanho = os.path.getsize(arq) / (1024 * 1024)
                self.lista_arquivos.insert(tk.END, f"{os.path.basename(arq)}  ({tamanho:.1f} MB)")

    def _remover_selecionados(self):
        selection = self.lista_arquivos.curselection()
        for index in reversed(selection):
            self.arquivos.pop(index)
            self.lista_arquivos.delete(index)

    def _limpar_lista(self):
        self.arquivos.clear()
        self.lista_arquivos.delete(0, tk.END)

    def _escolher_destino(self):
        destino = selecionar_destino()
        if destino:
            self.pasta_destino = destino
            self.lbl_destino.config(text=destino)

    def _comprimir(self):
        if not self.arquivos:
            messagebox.showwarning("Aviso", "Nenhuma imagem na lista.")
            return

        if not self.pasta_destino:
            messagebox.showwarning("Aviso", "Selecione uma pasta de destino.")
            return

        try:
            tamanho_max = float(self.entry_tamanho.get())
            if tamanho_max <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Tamanho máximo inválido.")
            return

        formato = self.combo_formato.get()
        manter_ext = self.var_manter_ext.get()

        self.btn_comprimir.config(state=tk.DISABLED)
        self.progresso['maximum'] = len(self.arquivos)
        self.progresso['value'] = 0

        thread = threading.Thread(
            target=self._processar_compressao,
            args=(tamanho_max, formato, manter_ext),
            daemon=True
        )
        thread.start()

    def _processar_compressao(self, tamanho_max, formato, manter_ext):
        if self.var_subpasta.get():
            nome_subpasta = f"comprimido_{datetime.now().strftime('%Y-%m-%d_%H-%M')}"
            pasta_saida = os.path.join(self.pasta_destino, nome_subpasta)
        else:
            pasta_saida = self.pasta_destino

        os.makedirs(pasta_saida, exist_ok=True)

        erros = []
        total = len(self.arquivos)

        for i, caminho in enumerate(self.arquivos):
            try:
                nome_arquivo = os.path.basename(caminho)
                self.root.after(0, lambda n=nome_arquivo, idx=i, t=total:
                                self.lbl_status.config(text=f"{idx+1}/{t} — {n}"))

                resultado = comprimir_imagem(caminho, tamanho_max, formato, manter_ext)

                nome_base = os.path.splitext(nome_arquivo)[0]
                caminho_saida = os.path.join(pasta_saida, f"{nome_base}{resultado['extensao']}")

                with open(caminho_saida, 'wb') as f:
                    f.write(resultado['dados'])

                self.root.after(0, lambda idx=i: self.progresso.configure(value=idx + 1))

            except Exception as e:
                erros.append(f"{os.path.basename(caminho)}: {str(e)}")

        self.root.after(0, lambda: self._finalizar_compressao(pasta_saida, erros))

    def _finalizar_compressao(self, pasta_saida, erros):
        self.btn_comprimir.config(state=tk.NORMAL)
        self.lbl_status.config(text=f"Concluído! Salvo em: {pasta_saida}")

        if erros:
            mensagem = "Compressão concluída com erros:\n\n" + "\n".join(erros[:10])
            if len(erros) > 10:
                mensagem += f"\n... e mais {len(erros) - 10} erros."
            messagebox.showwarning("Concluído com erros", mensagem)
        else:
            messagebox.showinfo("Sucesso", f"Compressão concluída!\nSalvo em: {pasta_saida}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageCompressorApp()
    app.run()
