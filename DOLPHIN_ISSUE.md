# Problema con Dolphin - Incompatibilidad de Modelo

## Resumen del Problema

El modelo de Dolphin descargado (`dolphin_model.bin`, 1244.5 MB) tiene una **arquitectura incompatible** con el código actual.

## Errores Específicos

### Error Original
```
size mismatch for vpm.model.layers.1.downsample.norm.weight:
  copying a param with shape torch.Size([1024]) from checkpoint,
  the shape in current model is torch.Size([512]).

size mismatch for vpm.model.layers.2.downsample.norm.weight:
  copying a param with shape torch.Size([2048]) from checkpoint,
  the shape in current model is torch.Size([1024]).
```

**Interpretación**: El modelo tiene dimensiones más grandes (1024, 2048) en las capas intermedias, pero el código espera dimensiones más pequeñas (512, 1024).

### Error con `strict=False`

Cambiar a `strict=False` en `chat.py` no resuelve el problema porque las dimensiones fundamentales son incompatibles. El modelo no puede funcionar con capas de tamaño incorrecto.

## Causa Raíz

El archivo `dolphin_model.bin` descargado **NO corresponde** a la configuración en `Dolphin.yaml`. Hay dos posibilidades:

1. **Modelo incorrecto**: El archivo descargado no es la versión correcta de Dolphin
2. **Configuración incorrecta**: La configuración en `Dolphin.yaml` no coincide con el modelo

## Soluciones Posibles

### Opción 1: Descargar el modelo correcto desde HuggingFace ⭐ RECOMENDADO

El modelo oficial de Dolphin está en HuggingFace:

**Repositorio oficial**: https://huggingface.co/bytedance/Dolphin

**Archivos necesarios**:
- `model.safetensors` o `pytorch_model.bin` (modelo principal)
- `tokenizer.json` (tokenizador)
- `config.json` (configuración del modelo)

**Cómo descargar**:
```bash
# Opción 1: Usar Git LFS (recomendado)
git lfs install
git clone https://huggingface.co/bytedance/Dolphin

# Opción 2: Descargar manualmente desde la web
# https://huggingface.co/bytedance/Dolphin/tree/main
```

**Colocar archivos en**:
```
backend/Dolphin/checkpoints/
  ├── pytorch_model.bin (o model.safetensors)
  ├── tokenizer.json
  └── config.json (para verificar configuración)
```

### Opción 2: Modificar la configuración para que coincida con el modelo actual

Si el modelo descargado es válido pero tiene configuración diferente, podríamos:

1. Inspeccionar el modelo para determinar sus dimensiones exactas
2. Crear una nueva configuración en `Dolphin.yaml` que coincida

**Comando para inspeccionar el modelo**:
```python
import torch
ckpt = torch.load('backend/Dolphin/checkpoints/dolphin_model.bin')
print(ckpt.keys())
print(ckpt['vpm.model.layers.1.downsample.norm.weight'].shape)
```

### Opción 3: Usar un modelo alternativo compatible con Document AI

Alternativas a Dolphin:
- **Donut** (https://huggingface.co/naver-clova-ix/donut-base)
- **LayoutLMv3** (https://huggingface.co/microsoft/layoutlmv3-base)
- **Nougat** (https://huggingface.co/facebook/nougat-base)

## Recomendación

**1. Descargar el modelo oficial de HuggingFace** es la mejor solución porque:
   - Garantiza compatibilidad con el código existente
   - Es la fuente oficial y verificada
   - Incluye todos los archivos necesarios con la configuración correcta

**2. Si prefieres usar el modelo actual**, necesitarías:
   - Inspeccionar el checkpoint para entender su arquitectura
   - Crear una configuración personalizada en `Dolphin.yaml`
   - Esto requiere conocimiento técnico profundo de la arquitectura Swin Transformer

## Estado Actual del Sistema

- ✅ Código de integración Dolphin implementado
- ✅ Gemini configurado y funcionando
- ✅ Vista previa de documentos funcionando
- ✅ UI con feedback de progreso implementada
- ❌ **Dolphin bloqueado por incompatibilidad de modelo**

## Próximos Pasos

1. Decidir qué opción seguir (descargar modelo correcto vs modificar configuración)
2. Una vez Dolphin funcione, probar el flujo completo: Upload → Preview → Dolphin Parse → Gemini Summary
3. Verificar calidad de extracción de texto en documentos legales
