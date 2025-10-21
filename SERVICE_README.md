# Dolphin Document Parsing API Service

API REST para parsear documentos (imágenes y PDFs) usando el modelo Dolphin.

## Iniciar el Servicio

```bash
# Activar el entorno virtual
venv\Scripts\activate

# Iniciar el servicio en localhost:1000
python app.py --port 1000 --host 127.0.0.1
```

## Endpoints Disponibles

### 1. Health Check
```bash
GET http://127.0.0.1:1000/health
```

Respuesta:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

### 2. Parse Document
```bash
POST http://127.0.0.1:1000/parse
```

**Parámetros (multipart/form-data):**
- `file`: Archivo a parsear (imagen PNG/JPG/JPEG o PDF)
- `max_batch_size` (opcional): Tamaño máximo del batch (default: 16)

**Ejemplo con curl:**
```bash
curl -X POST http://127.0.0.1:1000/parse \
  -F "file=@./demo/page_imgs/page_1.png" \
  -F "max_batch_size=16"
```

**Ejemplo con Python:**
```python
import requests

url = "http://127.0.0.1:1000/parse"
files = {'file': open('./demo/page_imgs/page_1.png', 'rb')}
data = {'max_batch_size': 16}

response = requests.post(url, files=files, data=data)
result = response.json()
print(result)
```

**Respuesta (imagen):**
```json
{
  "success": true,
  "file_type": "image",
  "results": [
    {
      "label": "header",
      "text": "186 Chapter 7. THE ZETA FUNCTION AND PRIME NUMBER THEOREM",
      "bbox": [418, 138, 1337, 175],
      "reading_order": 0
    },
    {
      "label": "equ",
      "text": "$$\\log \\zeta(s)=\\log \\prod_{p} \\frac{1}{1-p^{-s}}=...$$",
      "bbox": [492, 270, 1261, 362],
      "reading_order": 2
    },
    ...
  ]
}
```

**Respuesta (PDF):**
```json
{
  "success": true,
  "file_type": "pdf",
  "total_pages": 3,
  "results": [
    {
      "page_number": 1,
      "elements": [...]
    },
    {
      "page_number": 2,
      "elements": [...]
    },
    ...
  ]
}
```

## Tipos de Elementos

El servicio identifica y parsea los siguientes tipos de elementos:

- `header`: Encabezados
- `para`: Párrafos
- `half_para`: Párrafos parciales
- `equ`: Ecuaciones matemáticas
- `tab`: Tablas
- `fig`: Figuras/imágenes
- `code`: Bloques de código
- Y otros tipos de elementos de documento

## Script de Prueba

Para probar el servicio rápidamente:

```bash
python test_client.py "./demo/page_imgs/page_1.png"
```

Esto ejecutará una prueba completa y guardará el resultado en `test_response.json`.

## Notas

- El servicio usa CPU por defecto (puede ser lento)
- Para mejor rendimiento, usar con GPU (CUDA)
- Tamaño máximo de archivo: 50MB
- Formatos soportados: PNG, JPG, JPEG, PDF
