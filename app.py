import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
import io

# --- Configuração da Página ---
st.set_page_config(page_title="Processador Geométrico de Imagens", layout="wide")

st.title("🎨 Transformador Geométrico de Imagens")
st.write("Faça upload de uma imagem para detectar cores e desenhar formas geométricas.")

# --- Barra Lateral (Parâmetros) ---
st.sidebar.header("Configurações")

# Parâmetros que estavam no código original, agora interativos
SATURATION_FACTOR = st.sidebar.slider("Fator de Saturação", 1.0, 10.0, 5.0, 0.5)
STEP_SIZE = st.sidebar.slider("Tamanho do Bloco (Pixels)", 5, 50, 10, 1)
PRESENCE_THRESHOLD = st.sidebar.slider("Limiar de Presença de Cor", 0.1, 0.9, 0.2, 0.05)

st.sidebar.subheader("Filtros de Intensidade")
GRAY_SAT_THRESHOLD = st.sidebar.slider("Limiar Saturação (Cinza)", 0, 100, 25)
BLACK_THRESHOLD = st.sidebar.slider("Limiar Preto", 0, 100, 30)
WHITE_THRESHOLD = st.sidebar.slider("Limiar Branco", 150, 255, 230)

# Constantes de desenho
ALPHA_VALUE = int(255 * 0.85)  # 85% opaco
LINE_WIDTH = 1

# --- Funções de Desenho (Originais do seu script) ---
def draw_square(draw, center_x, center_y, size, r_value):
    """Desenha quadrado vermelho"""
    s = size / 2
    color = (r_value, 0, 0, ALPHA_VALUE)
    draw.rectangle(
        (center_x - s, center_y - s, center_x + s, center_y + s),
        outline=color,
        width=LINE_WIDTH
    )

def draw_circle(draw, center_x, center_y, size, g_value):
    """Desenha círculo verde"""
    s = size / 2
    color = (0, g_value, 0, ALPHA_VALUE)
    draw.ellipse(
        (center_x - s, center_y - s, center_x + s, center_y + s),
        outline=color,
        width=LINE_WIDTH
    )

def draw_triangle(draw, center_x, center_y, size, b_value):
    """Desenha triângulo azul"""
    s = size / 2
    color = (0, 0, b_value, ALPHA_VALUE)
    points = [
        (center_x, center_y - s),
        (center_x - s, center_y + s),
        (center_x + s, center_y + s)
    ]
    draw.polygon(points, outline=color, width=LINE_WIDTH)

# --- Lógica Principal ---
def process_image(image_input):
    # 1. Converter e Saturar
    img = image_input.convert('RGBA')
    
    # Aplicar super saturação
    converter = ImageEnhance.Color(img)
    img_saturated = converter.enhance(SATURATION_FACTOR)
    
    # Imagem de saída (cópia para desenhar em cima)
    output_img = img_saturated.copy()
    draw = ImageDraw.Draw(output_img, 'RGBA')
    
    # Converter para numpy para leitura (opcional, mas suas funções usam crop/numpy array)
    # Vamos manter a lógica original do loop para garantir fidelidade ao seu script
    
    width, height = img.size
    
    # Barra de progresso do Streamlit
    progress_bar = st.progress(0)
    total_steps = (height // STEP_SIZE)
    
    for i, y in enumerate(range(0, height, STEP_SIZE)):
        # Atualizar barra de progresso
        progress_bar.progress(min(i / total_steps, 1.0))
        
        for x in range(0, width, STEP_SIZE):
            box = (x, y, x + STEP_SIZE, y + STEP_SIZE)
            
            # Usamos a imagem saturada para calcular a média de cor
            block_img = img_saturated.crop(box)
            
            # Cálculo da média (seguro contra blocos vazios na borda)
            block_arr = np.array(block_img)
            if block_arr.size == 0: continue
            
            avg_color = np.mean(block_arr, axis=(0, 1))
            
            if len(avg_color) >= 3:
                r, g, b = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
            else:
                continue # Pular se for grayscale puro sem RGB

            intensity = (r + g + b) / 3
            saturation = max(r, g, b) - min(r, g, b)

            if (saturation < GRAY_SAT_THRESHOLD or
                intensity < BLACK_THRESHOLD or
                intensity > WHITE_THRESHOLD):
                continue

            total_color = r + g + b + 0.001
            r_norm = r / total_color
            g_norm = g / total_color
            b_norm = b / total_color

            center_x = x + (STEP_SIZE / 2)
            center_y = y + (STEP_SIZE / 2)
            shape_size = STEP_SIZE * 0.9

            if r_norm > PRESENCE_THRESHOLD:
                draw_square(draw, center_x, center_y, shape_size, r)

            if g_norm > PRESENCE_THRESHOLD:
                draw_circle(draw, center_x, center_y, shape_size, g)

            if b_norm > PRESENCE_THRESHOLD:
                draw_triangle(draw, center_x, center_y, shape_size, b)
                
    progress_bar.empty() # Limpar barra quando terminar
    return img_saturated, output_img

# --- Interface de Upload ---
uploaded_file = st.file_uploader("Escolha uma imagem (JPG, PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # Carregar imagem original
    original_image = Image.open(uploaded_file)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.image(original_image, caption="Imagem Original", use_container_width=True)
    
    # Botão para processar
    if st.button("Processar Imagem", type="primary"):
        with st.spinner('Processando pixels e formas...'):
            img_sat, result_img = process_image(original_image)
            
            with col2:
                st.image(img_sat, caption=f"Saturada (Fator {SATURATION_FACTOR})", use_container_width=True)
            
            with col3:
                st.image(result_img, caption="Resultado Geométrico", use_container_width=True)
            
            # Botão de Download
            buf = io.BytesIO()
            result_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="Baixar Imagem Processada",
                data=byte_im,
                file_name="geometric_art.png",
                mime="image/png"
            )