import fitz  # PyMuPDF
import os

def extraer_imagenes_de_pdf(ruta_pdf, carpeta_salida):
    # Crear la carpeta de salida si no existe
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Abrir el documento PDF
    doc = fitz.open(ruta_pdf)

    for numero_pagina in range(len(doc)):
        pagina = doc.load_page(numero_pagina)
        # Renderizar la página como imagen (2x de resolución)
        mat = fitz.Matrix(2, 2)
        pix = pagina.get_pixmap(matrix=mat)
        nombre_archivo = f"pagina_{numero_pagina + 1}.png"
        ruta_archivo = os.path.join(carpeta_salida, nombre_archivo)
        pix.save(ruta_archivo)
        print(f"Guardada: {nombre_archivo}")

    print(f"¡Listo! Se guardaron {len(doc)} páginas en la carpeta '{carpeta_salida}'.")

# --- USO DEL SCRIPT ---
ruta_del_pdf = "examen_diagnostico.pdf"
carpeta_destino = "imagenes_extraidas"

extraer_imagenes_de_pdf(ruta_del_pdf, carpeta_destino)