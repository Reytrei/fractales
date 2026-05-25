import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import hashlib
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

# --- FUNCIONES MATEMÁTICAS (Idénticas a tu script local) ---
def texto_a_parametro(texto):
    hash_obj = hashlib.sha256(texto.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    parte_real = int(hash_hex[:8], 16)
    parte_imag = int(hash_hex[32:40], 16)
    
    max_val = 0xFFFFFFFF
    real_norm = (parte_real / max_val) * 3.0 - 1.5
    imag_norm = (parte_imag / max_val) * 3.0 - 1.5
    
    return complex(real_norm, imag_norm)

@st.cache_data 
def generar_julia_racional(c_real, c_imag, width=800, height=800, max_iter=256):
    # Reconstruimos el número complejo de forma segura dentro de la función
    c = complex(c_real, c_imag) 
    
    xmin, xmax = -2.5, 2.5
    ymin, ymax = -2.5, 2.5
    escape_radius = 10.0

    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y

    # ... (El resto del bucle for se mantiene exactamente igual) ...

    smooth_iter = np.zeros(Z.shape, dtype=float)
    active = np.ones(Z.shape, dtype=bool)

    for i in range(max_iter):
        Z_act = Z[active]
        Z_act[Z_act == 0] = 1e-10 
        
        Z_new = Z_act**2 + (c / Z_act)
        Z[active] = Z_new
        
        escaped_local = np.abs(Z_new) > escape_radius
        
        if np.any(escaped_local):
            z_esc = Z_new[escaped_local]
            smooth_val = (i + 1) - np.log2(np.log(np.abs(z_esc)))
            
            active_indices = np.where(active)
            esc_idx_x = active_indices[0][escaped_local]
            esc_idx_y = active_indices[1][escaped_local]
            smooth_iter[esc_idx_x, esc_idx_y] = smooth_val
            
            active[active_indices[0][escaped_local], active_indices[1][escaped_local]] = False

    smooth_iter[active] = max_iter
    return smooth_iter, (xmin, xmax, ymin, ymax)

# --- INTERFAZ DE USUARIO (STREAMLIT) ---
st.set_page_config(page_title="Generador de Fractales", layout="centered")

st.title("Fractales Criptográficos")
st.markdown("Introduce una semilla (tu seudónimo, un concepto matemático, etc.) para generar un Atractor de Julia único.")

# Input del usuario
semilla = st.text_input("Palabra Semilla:", "Atractor Extraño")

if semilla:
    # Procesamiento
    c = texto_a_parametro(semilla)
    st.write(f"**Parámetro $c$ generado:** `{c.real:.4f} + {c.imag:.4f}i`")
    
    with st.spinner("Calculando sistema dinámico..."):
        # Pasamos los floats individuales en lugar del objeto complex
        matriz_fractal, limites = generar_julia_racional(c.real, c.imag)
    
    # Renderizado
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(matriz_fractal, cmap='twilight_shifted', extent=limites, origin='lower')
    ax.axis('off')
    
    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)