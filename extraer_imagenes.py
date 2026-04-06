import fitz  # PyMuPDF
import os

def procesar_pdf_examen(ruta_pdf, carpeta_salida):
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    doc = fitz.open(ruta_pdf)
    
    # 1. INTENTO DE EXTRACCIÓN DIRECTA (Para fotos/bitmaps)
    contador_extrapoladas = 0
    for num_pag in range(len(doc)):
        pagina = doc.load_page(num_pag)
        lista_img = pagina.get_images(full=True)
        for i, img in enumerate(lista_img, start=1):
            base_img = doc.extract_image(img[0])
            nombre = f"ext_p{num_pag+1}_img{i}.{base_img['ext']}"
            with open(os.path.join(carpeta_salida, nombre), "wb") as f:
                f.write(base_img["image"])
            contador_extrapoladas += 1

    # 2. RENDERIZADO DE PÁGINAS (Para vectores/dibujos de LaTeX)
    # Usamos un zoom de 2 para que las preguntas se vean nítidas en tu web
    matriz = fitz.Matrix(2, 2) 
    for num_pag in range(len(doc)):
        pagina = doc.load_page(num_pag)
        pix = pagina.get_pixmap(matrix=matriz)
        nombre_pag = f"render_pagina_{num_pag + 1}.png"
        pix.save(os.path.join(carpeta_salida, nombre_pag))

    print(f"--- Proceso Finalizado ---")
    print(f"Imágenes extraídas directamente: {contador_extrapoladas}")
    print(f"Páginas renderizadas como fotos: {len(doc)}")
    print(f"Todo guardado en: {carpeta_salida}")

# --- EJECUCIÓN ---
ruta_archivo = "examen_diagnostico.pdf" 
carpeta_destino = "recursos_examen"

procesar_pdf_examen(ruta_archivo, carpeta_destino)