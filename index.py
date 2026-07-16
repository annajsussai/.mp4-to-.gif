import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font

import cv2
from PIL import Image, ImageTk

BG_ESCURO = "#0d0d10"
BG_PAINEL = "#18181d"
BG_CAMPO = "#222228"
COR_ACENTO = "#f2b705"      
COR_ACENTO_HOVER = "#ffce33"
COR_ACENTO_ATIVO = "#d9a300"
COR_TEXTO = "#f6f6f4"
COR_TEXTO_FRACO = "#8f8f98"
COR_BORDA_FILME = "#000000"
COR_FURO = "#38383f"
COR_BORDA_PAINEL = "#2c2c33"
COR_BORDA_PAINEL_HOVER = "#3a3a42"
COR_SOMBRA = "#000000"
RAIO_PADRAO = 10


class RoloDeFilme(tk.Canvas):
    """Uma tira de filme decorativa, com furinhos de sprocket, usada
    como moldura no topo e na base da janela."""

    def __init__(self, master, altura=26, **kwargs):
        super().__init__(master, height=altura, bg=COR_BORDA_FILME,
                          highlightthickness=0, **kwargs)
        self._altura = altura
        self.bind("<Configure>", self._desenhar)

    def _desenhar(self, event=None):
        self.delete("all")
        largura = self.winfo_width() or 800
        h = self._altura
        furo = h * 0.42
        espaco = furo * 1.9
        y = h / 2
        x = espaco / 2
        while x < largura:
            self.create_rectangle(
                x - furo / 2, y - furo / 2, x + furo / 2, y + furo / 2,
                fill=COR_FURO, outline="", width=0
            )
            x += espaco


def _forma_arredondada(canvas, x1, y1, x2, y2, raio, **kwargs):
    """Desenha um retângulo com cantos arredondados de verdade num Canvas."""
    pontos = [
        x1 + raio, y1, x2 - raio, y1, x2, y1, x2, y1 + raio,
        x2, y2 - raio, x2, y2, x2 - raio, y2, x1 + raio, y2,
        x1, y2, x1, y2 - raio, x1, y1 + raio, x1, y1,
    ]
    return canvas.create_polygon(pontos, smooth=True, **kwargs)


class BotaoAcento(tk.Canvas):

    def __init__(self, master, texto, comando, largura=None, secundario=False, **kwargs):
        self._bg_pai = master["bg"] if isinstance(master, (tk.Frame, tk.Tk)) else BG_ESCURO
        super().__init__(master, bg=self._bg_pai, highlightthickness=0,
                          bd=0, **kwargs)
        self.comando = comando
        self.secundario = secundario
        self.texto = texto
        self._ativo = True
        self._fonte = ("Segoe UI", 10, "bold")
        self._largura_min = largura or 0
        self.bind("<Configure>", lambda e: self._redesenhar())
        self.bind("<Button-1>", self._clicar)
        self.bind("<Enter>", lambda e: self._redesenhar(hover=True))
        self.bind("<Leave>", lambda e: self._redesenhar(hover=False))
        self.after(10, self._ajustar_tamanho)

    def _ajustar_tamanho(self):
        tam = tk.font.Font(font=self._fonte).measure(self.texto)
        largura = max(tam + 44, self._largura_min)
        self.config(width=largura, height=38)
        self._redesenhar()

    def _cores(self, hover=False):
        if not self._ativo:
            return "#2c2c31", "#6b6b72"
        if self.secundario:
            return (COR_BORDA_PAINEL_HOVER if hover else BG_CAMPO), (COR_ACENTO if hover else COR_TEXTO)
        return (COR_ACENTO_HOVER if hover else COR_ACENTO), "#1a1400"

    def _redesenhar(self, hover=False):
        self.delete("all")
        w = self.winfo_width() or (self._largura_min + 44)
        h = self.winfo_height() or 38
        fundo, frente = self._cores(hover)
        if not self.secundario:
            _forma_arredondada(self, 2, 4, w - 2, h, 9, fill="#000000",
                                outline="", stipple="gray25")
        _forma_arredondada(self, 1, 1, w - 1, h - 3, 9, fill=fundo, outline="")
        self.create_text(w / 2, (h - 2) / 2, text=self.texto, fill=frente,
                          font=self._fonte)
        self.config(cursor="hand2" if self._ativo else "arrow")

    def _clicar(self, e):
        if self._ativo and self.comando:
            self.comando()

    def desabilitar(self):
        self._ativo = False
        self._redesenhar()

    def habilitar(self):
        self._ativo = True
        self._redesenhar()


class AppMp4ParaGif(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transforme qualquer vídeo em gif.")
        self.geometry("640x720")
        self.minsize(560, 680)
        self.configure(bg=BG_ESCURO)

        self.caminho_video = None
        self.info_video = None  # (fps, total_frames, duracao, largura, altura)
        self.thumb_img = None

        self._configurar_estilos()
        self._montar_layout()

    def _configurar_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(
            "Acento.Horizontal.TProgressbar",
            troughcolor=BG_CAMPO, background=COR_ACENTO, thickness=6,
            borderwidth=0
        )
        estilo.configure(
            "Acento.Horizontal.TScale",
            background=BG_ESCURO, troughcolor=BG_CAMPO,
            borderwidth=0, sliderthickness=16, sliderlength=16
        )
        estilo.map(
            "Acento.Horizontal.TScale",
            background=[("active", BG_ESCURO)],
        )
        self.estilo = estilo

    
    # layout
    
    def _montar_layout(self):
        RoloDeFilme(self).pack(fill="x", side="top")

        corpo = tk.Frame(self, bg=BG_ESCURO)
        corpo.pack(fill="both", expand=True, padx=28, pady=(22, 10))

        # cabecalho --------------------------------------------------
        tk.Label(
            corpo, text="🎞  Transforme qualquer vídeo em gif.",
            bg=BG_ESCURO, fg=COR_TEXTO, font=("Segoe UI", 19, "bold"),
            anchor="w", justify="left"
        ).pack(fill="x")

        tk.Label(
            corpo,
            text="Solte um clipe, ajuste o quadro e o ritmo, e revele\n"
                 "um GIF leve, pronto pra rodar em loop.",
            bg=BG_ESCURO, fg=COR_TEXTO_FRACO, font=("Segoe UI", 10),
            anchor="w", justify="left"
        ).pack(fill="x", pady=(4, 18))

        # area de selecao video ------------------------------------
        moldura_arquivo = tk.Canvas(corpo, bg=BG_ESCURO, highlightthickness=0,
                                     height=172)
        moldura_arquivo.pack(fill="x", pady=(0, 16))

        def _desenhar_moldura(event=None):
            moldura_arquivo.delete("fundo")
            w = moldura_arquivo.winfo_width() or 560
            h = moldura_arquivo.winfo_height() or 172
            _forma_arredondada(moldura_arquivo, 1, 1, w - 1, h - 1, RAIO_PADRAO,
                                fill=BG_PAINEL, outline=COR_BORDA_PAINEL, width=1,
                                tags="fundo")
            moldura_arquivo.tag_lower("fundo")

        moldura_arquivo.bind("<Configure>", _desenhar_moldura)

        self.painel_arquivo = tk.Frame(moldura_arquivo, bg=BG_PAINEL)
        moldura_arquivo.create_window(0, 0, window=self.painel_arquivo,
                                       anchor="nw", tags="conteudo")

        def _ajustar_conteudo(event):
            moldura_arquivo.itemconfig("conteudo", width=event.width)
            self.painel_arquivo.config(height=event.height)

        moldura_arquivo.bind("<Configure>", _ajustar_conteudo, add="+")

        self.miniatura_lbl = tk.Label(
            self.painel_arquivo, bg=BG_CAMPO, width=18, height=6,
            text="sem\npré-visualizacao", fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 9)
        )
        self.miniatura_lbl.pack(side="left", padx=18, pady=18)

        info_frame = tk.Frame(self.painel_arquivo, bg=BG_PAINEL)
        info_frame.pack(side="left", fill="both", expand=True, pady=18, padx=(0, 18))

        self.arquivo_nome_lbl = tk.Label(
            info_frame, text="Nenhum vídeo selecionado",
            bg=BG_PAINEL, fg=COR_TEXTO, font=("Segoe UI", 11, "bold"),
            anchor="w"
        )
        self.arquivo_nome_lbl.pack(fill="x")

        self.arquivo_detalhe_lbl = tk.Label(
            info_frame, text="Formatos aceitos: .mp4",
            bg=BG_PAINEL, fg=COR_TEXTO_FRACO, font=("Segoe UI", 9),
            anchor="w"
        )
        self.arquivo_detalhe_lbl.pack(fill="x", pady=(4, 10))

        BotaoAcento(
            info_frame, "Escolher vídeo .mp4", self._escolher_arquivo,
            secundario=True
        ).pack(anchor="w")

        # ajustes quadro e ritmo --------------------------------------
        cabecalho_ajustes = tk.Frame(corpo, bg=BG_ESCURO)
        cabecalho_ajustes.pack(fill="x", pady=(6, 10))
        tk.Label(
            cabecalho_ajustes, text="●", bg=BG_ESCURO, fg=COR_ACENTO,
            font=("Segoe UI", 7)
        ).pack(side="left", padx=(0, 6))
        tk.Label(
            cabecalho_ajustes, text="QUADRO E RITMO", bg=BG_ESCURO, fg=COR_TEXTO,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left")
        tk.Frame(cabecalho_ajustes, bg=COR_BORDA_PAINEL, height=1).pack(
            side="left", fill="x", expand=True, padx=(12, 0), pady=(1, 0)
        )

        ajustes = tk.Frame(corpo, bg=BG_PAINEL)
        ajustes.pack(fill="x", pady=(0, 16))
        grade = tk.Frame(ajustes, bg=BG_PAINEL)
        grade.pack(fill="x", padx=14, pady=14)
        grade.columnconfigure((0, 1), weight=1)

        # inicio / fim (recorte)
        self.var_inicio = tk.DoubleVar(value=0.0)
        self.var_fim = tk.DoubleVar(value=0.0)
        self._campo_slider(grade, 0, "Início do recorte (s)", self.var_inicio, 0, 1)
        self._campo_slider(grade, 1, "Fim do recorte (s)", self.var_fim, 0, 1)

        # fps / largura
        self.var_fps = tk.IntVar(value=12)
        self.var_largura = tk.IntVar(value=480)
        self._campo_slider(grade, 2, "Quadros por segundo (fps)", self.var_fps, 3, 30)
        self._campo_slider(grade, 3, "Largura do GIF (px)", self.var_largura, 120, 720)

        # velocidade
        self.var_velocidade = tk.DoubleVar(value=1.0)
        self._campo_slider(grade, 4, "Velocidade (x)", self.var_velocidade, 0.25, 3.0, passo=0.05)

        # loop
        self.var_loop = tk.BooleanVar(value=True)
        loop_frame = tk.Frame(grade, bg=BG_PAINEL)
        loop_frame.grid(row=2, column=1, sticky="ew", padx=8, pady=8)
        tk.Checkbutton(
            loop_frame, text="Repetir em loop infinito", variable=self.var_loop,
            bg=BG_PAINEL, fg=COR_TEXTO, selectcolor=BG_CAMPO,
            activebackground=BG_PAINEL, activeforeground=COR_TEXTO,
            font=("Segoe UI", 9), relief="flat", bd=0,
            highlightthickness=0, cursor="hand2"
        ).pack(anchor="w")

        # progresso e acao -----------------------------------------
        rodape = tk.Frame(corpo, bg=BG_ESCURO)
        rodape.pack(fill="x", side="bottom", pady=(6, 0))

        self.status_lbl = tk.Label(
            rodape, text="Aguardando um vídeo…", bg=BG_ESCURO,
            fg=COR_TEXTO_FRACO, font=("Segoe UI", 9), anchor="w"
        )
        self.status_lbl.pack(fill="x")

        self.barra = ttk.Progressbar(
            rodape, style="Acento.Horizontal.TProgressbar",
            orient="horizontal", mode="determinate"
        )
        self.barra.pack(fill="x", pady=(6, 12))

        botoes = tk.Frame(rodape, bg=BG_ESCURO)
        botoes.pack(fill="x")
        self.botao_converter = BotaoAcento(
            botoes, "🎬  Gerar GIF", self._iniciar_conversao
        )
        self.botao_converter.pack(side="right")
        self.botao_converter.desabilitar()

        RoloDeFilme(self).pack(fill="x", side="bottom")

    def _campo_slider(self, master, row, rotulo, variavel, minimo, maximo, passo=1):
        col = row % 2
        r = row // 2
        bloco = tk.Frame(master, bg=BG_PAINEL)
        bloco.grid(row=r, column=col, sticky="ew", padx=8, pady=8)
        master.rowconfigure(r, weight=0)

        cabeca = tk.Frame(bloco, bg=BG_PAINEL)
        cabeca.pack(fill="x")
        tk.Label(cabeca, text=rotulo, bg=BG_PAINEL, fg=COR_TEXTO_FRACO,
                 font=("Segoe UI", 9)).pack(side="left")
        valor_lbl = tk.Label(cabeca, textvariable=self._texto_valor(variavel, passo),
                              bg=BG_PAINEL, fg=COR_ACENTO, font=("Segoe UI", 9, "bold"))
        valor_lbl.pack(side="right")

        escala = ttk.Scale(
            bloco, variable=variavel, from_=minimo, to=maximo,
            orient="horizontal", style="Acento.Horizontal.TScale",
            command=lambda v: variavel.set(round(float(v) / passo) * passo)
        )
        escala.pack(fill="x", pady=(6, 0))

    def _texto_valor(self, variavel, passo):
        texto = tk.StringVar()

        def atualizar(*_):
            v = variavel.get()
            if passo < 1:
                texto.set(f"{v:.2f}")
            else:
                texto.set(f"{int(v)}")

        variavel.trace_add("write", atualizar)
        atualizar()
        return texto

    
    # selecao de arquivo
    
    def _escolher_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Escolha um vídeo .mp4",
            filetypes=[("Vídeos MP4", "*.mp4"), ("Todos os arquivos", "*.*")]
        )
        if not caminho:
            return
        self._carregar_video(caminho)

    def _carregar_video(self, caminho):
        cap = cv2.VideoCapture(caminho)
        if not cap.isOpened():
            messagebox.showerror("Erro", "Nao foi possível abrir esse vídeo.")
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        largura = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        altura = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duracao = total_frames / fps if fps else 0

        ok, frame = cap.read()
        cap.release()

        self.caminho_video = caminho
        self.info_video = (fps, total_frames, duracao, largura, altura)

        nome = os.path.basename(caminho)
        self.arquivo_nome_lbl.config(text=nome)
        self.arquivo_detalhe_lbl.config(
            text=f"{largura}x{altura} px · {duracao:.1f}s · {fps:.0f} fps originais"
        )

        # atualiza limites do recorte
        self.var_inicio.set(0.0)
        self.var_fim.set(round(duracao, 1))
        for filho in self.nametowidget(".").winfo_children():
            pass 

        # miniatura
        if ok:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.thumbnail((140, 140))
            self.thumb_img = ImageTk.PhotoImage(img)
            self.miniatura_lbl.config(image=self.thumb_img, text="", width=140, height=140)

        self.status_lbl.config(text="Pronto para gerar o GIF.")
        self.botao_converter.habilitar()

    
    # conversao
    
    def _iniciar_conversao(self):
        if not self.caminho_video:
            return

        destino = filedialog.asksaveasfilename(
            title="Salvar GIF como",
            defaultextension=".gif",
            filetypes=[("GIF", "*.gif")],
            initialfile=os.path.splitext(os.path.basename(self.caminho_video))[0] + ".gif"
        )
        if not destino:
            return

        self.botao_converter.desabilitar()
        self.barra["value"] = 0
        self.status_lbl.config(text="Lendo os quadros do vídeo…")

        parametros = dict(
            origem=self.caminho_video,
            destino=destino,
            fps_saida=int(self.var_fps.get()),
            largura_saida=int(self.var_largura.get()),
            inicio=float(self.var_inicio.get()),
            fim=float(self.var_fim.get()),
            velocidade=float(self.var_velocidade.get()),
            loop_infinito=self.var_loop.get(),
        )

        thread = threading.Thread(target=self._converter_em_thread, kwargs=parametros, daemon=True)
        thread.start()

    def _converter_em_thread(self, origem, destino, fps_saida, largura_saida,
                              inicio, fim, velocidade, loop_infinito):
        try:
            cap = cv2.VideoCapture(origem)
            fps_original = cap.get(cv2.CAP_PROP_FPS) or 24
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duracao_total = total_frames / fps_original if fps_original else 0

            fim_real = fim if fim > inicio else duracao_total
            fim_real = min(fim_real, duracao_total) if duracao_total else fim_real
            inicio_real = max(0.0, min(inicio, fim_real))

            frame_inicial = int(inicio_real * fps_original)
            frame_final = int(fim_real * fps_original) if fim_real else total_frames
            frame_final = min(frame_final, total_frames) if total_frames else frame_final

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_inicial)

            passo = max(1, round((fps_original / fps_saida) / max(velocidade, 0.01)))

            quadros = []
            indice = frame_inicial
            capturados = 0
            faixa = max(1, frame_final - frame_inicial)

            while indice < frame_final:
                ok, frame = cap.read()
                if not ok:
                    break
                if (indice - frame_inicial) % passo == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    if largura_saida and img.width != largura_saida:
                        proporcao = largura_saida / img.width
                        nova_altura = max(1, int(img.height * proporcao))
                        img = img.resize((largura_saida, nova_altura), Image.LANCZOS)
                    quadros.append(img)
                    capturados += 1

                indice += 1
                if indice % 5 == 0:
                    progresso = min(95, int((indice - frame_inicial) / faixa * 90))
                    self._atualizar_status(f"Extraindo quadros… {capturados} capturados", progresso)

            cap.release()

            if not quadros:
                raise RuntimeError("Nenhum quadro foi extraído. Verifique o recorte de início/fim.")

            self._atualizar_status("Montando o GIF…", 96)

            duracao_quadro_ms = int(1000 / fps_saida)
            quadros[0].save(
                destino,
                save_all=True,
                append_images=quadros[1:],
                duration=duracao_quadro_ms,
                loop=0 if loop_infinito else 1,
                optimize=True,
                disposal=2,
            )

            tamanho_kb = os.path.getsize(destino) / 1024
            self._atualizar_status(
                f"GIF pronto! {len(quadros)} quadros · {tamanho_kb:.0f} KB", 100
            )
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", f"Seu GIF foi salvo em:\n{destino}"
            ))

        except Exception as erro:
            self.after(0, lambda: messagebox.showerror("Erro na conversao", str(erro)))
            self._atualizar_status("Falha na conversao.", 0)
        finally:
            self.after(0, self.botao_converter.habilitar)

    def _atualizar_status(self, texto, progresso):
        def _fazer():
            self.status_lbl.config(text=texto)
            self.barra["value"] = progresso
        self.after(0, _fazer)


if __name__ == "__main__":
    app = AppMp4ParaGif()
    app.mainloop()
