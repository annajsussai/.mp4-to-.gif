<div align="center">
  <img src="./images/logo.svg" width="80" height="80" alt="Logo MP4 para GIF">
  <h1>Conversor de Vídeo para GIF</h1>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/linguagem-Python-blue" alt="Python">
  <img src="https://img.shields.io/badge/interface-Tkinter-yellow" alt="Tkinter">
  <img src="https://img.shields.io/badge/processamento-OpenCV-green" alt="OpenCV">
</div>

Ferramenta desktop intuitiva desenvolvida em Python para transformar clipes de vídeo (`.mp4`) em GIFs leves, otimizados e prontos para loop. Transforme vídeos em GIFs de forma simples: recorte trechos, ajuste FPS, redimensione e controle a velocidade com interface intuitiva e processamento em segundo plano.

---

## 🎥 Demonstração

<div align="center">
  <img src="./images/mp4_to_gif.gif" width="500" alt="Demonstração do conversor de MP4 para GIF">
</div>

---

## 📃 Funcionalidades

- **Interface Gráfica Moderna:** Construída com `tkinter`.
- **Controle Total:** Ajuste início/fim, FPS, largura e velocidade.
- **Processamento Assíncrono:** Uso de *threading* para não travar a interface.
- **Otimização:** Geração de GIF com redimensionamento de alta qualidade (LANCZOS).
- **Validação:** Barra de progresso em tempo real.

---

## 🛠️ Tecnologias Utilizadas

- **Python**
- **Tkinter** (Interface GUI)
- **OpenCV (`cv2`)** (Processamento de vídeo)
- **Pillow (`PIL`)** (Manipulação de imagem)

---

## 🚀 Como utilizar

1. **Instale as dependências:**
   ```bash
   pip install opencv-python-headless pillow
