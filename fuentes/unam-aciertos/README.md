# Aciertos mínimos de ingreso a licenciatura UNAM — fuente oficial

Contra lo que parece a primera vista, la UNAM **sí publica** el corte de aciertos por
carrera y plantel. No está en los PDF de resultados de la DGAE (esos son de trámite:
fechas y entrega de documentos) ni en el PAAUNAM de Planeación (ese es el perfil
socioeconómico de aspirantes). Está en el folleto anual **"¿Cómo ingreso a la UNAM?"**
de la Dirección General de Administración Escolar, en la sección **"Cuadro con los
antecedentes de aciertos"**.

| Archivo | Datos del concurso | Origen |
|---|:-:|---|
| `aciertos-2020.pdf` | 2020 | `repositorio.dgae.unam.mx/pdfs/tablas_licenciatura.pdf` |
| `aciertos-2021.pdf` | 2021 | `escolar1.unam.mx/pdfs/licenciatura20212022.pdf` |
| `aciertos-2022.pdf` | 2022 | `escolar1.unam.mx/pdfs/licenciatura20222023.pdf` |
| `aciertos-2023.pdf` | 2023 | `escolar1.unam.mx/pdfs/licenciatura20232024.pdf` |
| `aciertos-2024.pdf` | 2024 | `escolar1.unam.mx/pdfs/licenciatura20242025.pdf` |

Cada tabla trae, por carrera-plantel-sistema: lugares disponibles, aspirantes que
concursaron por ellos y **el número de aciertos con que se cubrió el cupo**.

`escolar1.unam.mx` está detrás de Cloudflare y rechaza descargas automatizadas; los
folletos 2021-2024 se recuperaron del Internet Archive. `repositorio.dgae.unam.mx` sí
responde directo.

## Pendiente

- **2025**: el folleto `licenciatura20252026.pdf` todavía no aparece publicado ni
  archivado. Hay que revisar si sale, porque el criterio del examen de control 2026
  abarca de 2021 a 2026.
- La tabla de **bachillerato** del folleto 2024 sí muestra cinco años en un solo
  cuadro (2020-2024); la de licenciatura solo muestra el año en curso, de ahí que
  haga falta un folleto por año.

## Ojo con el texto

El PDF conserva las columnas al extraer con `pdftotext -layout`, pero las celdas se
parten en varios renglones y las carreras largas ocupan dos o tres. Un corte por
posición fija de columna desalinea las filas: hay que usar las coordenadas reales
(`pdftotext -bbox-layout`) o revisar el resultado a mano.
