import numpy as np
import matplotlib.pyplot as plt
import hashlib
import warnings
import time

# Ignorar warnings temporales por divisiones por cero
warnings.filterwarnings("ignore", category=RuntimeWarning)

def texto_a_parametro(texto):
    """
    Convierte una cadena de texto en un parámetro complejo 'c' 
    utilizando SHA-256 para garantizar determinismo y dispersión.
    """
    hash_obj = hashlib.sha256(texto.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()
    
    # Extraer dos bloques de 8 caracteres (32 bits cada uno)
    parte_real = int(hash_hex[:8], 16)
    parte_imag = int(hash_hex[8:16], 16)
    
    # Normalizar al rango de interés para el fractal [-1.5, 1.5]
    # Reducimos un poco el rango respecto a [-2, 2] para evitar 
    # parámetros que degeneren demasiado rápido.
    max_val = 0xFFFFFFFF
    real_norm = (parte_real / max_val) * 3.0 - 1.5
    imag_norm = (parte_imag / max_val) * 3.0 - 1.5
    
    return complex(real_norm, imag_norm)

def generar_julia_racional(c, width=1000, height=1000, max_iter=256):
    """
    Calcula la matriz de escape continuo para f(z) = z^2 + c/z
    """
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
        Z_act[Z_act == 0] = 1e-10 # Evitar singularidad pura
        
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

def main():
    print("========================================")
    print("   GENERADOR DE FRACTALES CRIPTOGRÁFICOS")
    print("========================================\n")
    
    semilla = input("Introduce un nombre, concepto o frase semilla: ")
    
    if not semilla.strip():
        print("Error: La semilla no puede estar vacía.")
        return

    # 1. Calcular el parámetro
    c = texto_a_parametro(semilla)
    print(f"\n[+] Semilla procesada: '{semilla}'")
    print(f"[+] Parámetro c generado: {c.real:.4f} + {c.imag:.4f}i")
    print("[+] Calculando el atractor dinámico (esto puede tardar unos segundos)...")

    # 2. Generar el fractal
    inicio = time.time()
    # Resolución reducida a 1000x1000 para pruebas rápidas en local
    matriz_fractal, limites = generar_julia_racional(c, width=1000, height=1000) 
    fin = time.time()
    print(f"[+] Fractal renderizado en {fin - inicio:.2f} segundos.")

    # 3. Visualización
    plt.figure(figsize=(10, 10))
    # Puedes probar otros mapas de color como 'magma', 'inferno' o 'ocean'
    plt.imshow(matriz_fractal, cmap='twilight_shifted', extent=limites, origin='lower')
    plt.axis('off')
    plt.title(f"Semilla: {semilla}\nc = {c.real:.4f} + {c.imag:.4f}i", color='white', fontsize=10, y=0.02)
    
    # Fondo oscuro para la ventana
    plt.gcf().patch.set_facecolor('black') 
    
    print("[+] Abriendo ventana de visualización. Cierra la ventana para terminar.")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()