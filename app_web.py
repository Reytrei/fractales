import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import hashlib
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

# --- FUNCIONES MATEMÁTICAS (Idénticas a tu script local) ---
def procesar_semilla(texto):
    hash_obj = hashlib.sha256(texto.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    # 1. Parámetro C (Posiciones 0-15 del hash)
    parte_real = int(hash_hex[:8], 16)
    parte_imag = int(hash_hex[8:16], 16)
    max_val = 0xFFFFFFFF
    real_norm = (parte_real / max_val) * 3.0 - 1.5
    imag_norm = (parte_imag / max_val) * 3.0 - 1.5
    c = complex(real_norm, imag_norm)
    
    # 2. Exponente o Simetría (Posiciones 16-19 del hash)
    # Genera un número entero entre 2 y 6
    exponente = 2 + (int(hash_hex[16:20], 16) % 5)
    
    # 3. Paleta de colores (Posiciones 20-23 del hash)
    paletas = ['twilight_shifted', 'magma', 'inferno', 'plasma', 'ocean', 'cubehelix', 'turbo', 'gist_earth']
    idx_color = int(hash_hex[20:24], 16) % len(paletas)
    cmap = paletas[idx_color]
    
    return c, exponente, cmap

@st.cache_data 
def generar_julia_racional(c_real, c_imag, exponente, width=800, height=800, max_iter=256):
    c = complex(c_real, c_imag) 
    
    xmin, xmax = -2.5, 2.5
    ymin, ymax = -2.5, 2.5
    escape_radius = 10.0

    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    smooth_iter = np.zeros(Z.shape, dtype=float)
    active = np.ones(Z.shape, dtype=bool)

    for i in range(max_iter):
        Z_act = Z[active]
        Z_act[Z_act == 0] = 1e-10 
        
        # APLICAMOS EL NUEVO EXPONENTE DINÁMICO
        Z_new = Z_act**exponente + (c / Z_act)
        Z[active] = Z_new
        
        escaped_local = np.abs(Z_new) > escape_radius
        
        if np.any(escaped_local):
            z_esc = Z_new[escaped_local]
            
            # EL SUAVIZADO AHORA DEPENDE DEL EXPONENTE MATEMÁTICO
            smooth_val = (i + 1) - np.log(np.log(np.abs(z_esc))) / np.log(exponente)
            
            active_indices = np.where(active)
            esc_idx_x = active_indices[0][escaped_local]
            esc_idx_y = active_indices[1][escaped_local]
            smooth_iter[esc_idx_x, esc_idx_y] = smooth_val
            
            active[active_indices[0][escaped_local], active_indices[1][escaped_local]] = False

    smooth_iter[active] = max_iter
    return smooth_iter, (xmin, xmax, ymin, ymax)

# --- INTERFAZ DE USUARIO (STREAMLIT) ---
st.set_page_config(page_title="Generador de Fractales", layout="centered")
hide_streamlit_style = """
    <style>
    /* Oculta el menú principal de la esquina superior derecha (hamburguesa) */
    #MainMenu {visibility: hidden;}
    
    /* Oculta el pie de página ('Made with Streamlit') */
    footer {visibility: hidden;}
    
    /* Opcional: Oculta la barra superior decorativa */
    header {visibility: hidden;}
    </style>
"""

st.title("Maquina Generadora de Fractales: De palabras a imagenes")
st.markdown("Introduce una semilla (tu nombre, un poema, un concepto matemático) para generar un atractor de Julia único.")

# Input del usuario
semilla = st.text_input("Palabra Semilla:", "Atractor de Julia")

if semilla:
    # 1. Obtenemos todas las variables de la semilla
    c, exponente, cmap_elegido = procesar_semilla(semilla)
    
    # Mostramos los datos matemáticos al usuario
    col1, col2 = st.columns(2)
    col1.write(f"**Constante $c$:** `{c.real:.4f} + {c.imag:.4f}i`")
    col2.write(f"**Grado polinómico:** $z^{exponente}$")
    st.write(f"**Paleta cromática asignada:** `{cmap_elegido}`")
    
    with st.spinner("Calculando sistema dinámico..."):
        # 2. Pasamos el exponente a la caché
        matriz_fractal, limites = generar_julia_racional(c.real, c.imag, exponente)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    # 3. Aplicamos la paleta de color única
    ax.imshow(matriz_fractal, cmap=cmap_elegido, extent=limites, origin='lower')
    ax.axis('off')
    
    st.pyplot(fig)