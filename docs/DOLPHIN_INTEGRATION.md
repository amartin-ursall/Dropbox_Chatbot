# Dolphin + Gemini Document Preview Integration

## Overview

The Dropbox AI Organizer now includes an intelligent document preview feature that combines:
- **Dolphin**: AI-powered document parsing (text, tables, figures extraction)
- **Gemini**: Intelligent summarization and information extraction

This feature provides users with a preview of their document **before** starting the question flow, improving user experience and reducing errors.

---

## Architecture

### Flow Diagram

```
┌─────────────────────┐
│  1. Upload File     │
│  POST /upload-temp  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  2. Generate Preview│
│  POST /document/    │ → Dolphin parses → Gemini summarizes
│       preview       │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  3. Show Preview    │
│  Frontend displays  │ → User sees summary + confidence
│  summary & asks     │
│  for confirmation   │
└──────────┬──────────┘
           │
        ┌──┴──┐
        │ OK? │
        └──┬──┘
     YES ↓    ↓ NO
   ┌─────────┐  └──→ POST /document/confirm
   │ Confirm │       (confirmed: false)
   └───┬─────┘       → Cleanup temp file
       │
       ↓
┌──────────────────────┐
│ 4. Start Questions   │ → Normal URSALL flow
│ POST /questions/start│
└──────────────────────┘
```

---

## Backend Components

### 1. `app/dolphin_parser.py`

Wrapper for Dolphin document parsing.

**Key Class: `DolphinParser`**

```python
from app.dolphin_parser import get_dolphin_parser

parser = get_dolphin_parser()
parsed_content, confidence = parser.parse_document(file_path)

# Returns:
# {
#   "text": str,           # Full extracted text
#   "elements": List[Dict], # All elements with labels
#   "pages": int,
#   "has_tables": bool,
#   "has_figures": bool
# }
```

**Features:**
- Handles both PDF (multi-page) and images (JPG, PNG)
- Extracts text, tables, and figures in natural reading order
- Returns structured content with bounding boxes
- Parallel batch processing for efficiency

### 2. `app/gemini_summarizer.py`

Gemini-powered document summarization.

**Key Function: `summarize_document()`**

```python
from app.gemini_summarizer import summarize_document

summary = await summarize_document(
    document_text=extracted_text,
    document_metadata={"pages": 3, "has_tables": True, "has_figures": False},
    target_use="legal"  # or "general"
)

# Returns:
# {
#   "summary": str,              # 2-3 sentence summary
#   "document_type": str,        # escritura, demanda, contrato, etc.
#   "is_legal_document": bool,
#   "confidence": float,         # 0-1
#   "key_information": {
#     "partes": ["A", "B"],
#     "jurisdiccion": "Social",
#     "juzgado": "Juzgado Social 2 de Tenerife",
#     "numero_procedimiento": "455/2025",
#     "fecha_documento": "2025-01-15",
#     "materia": "despido"
#   },
#   "suggested_answers": {      # Pre-filled answers for URSALL
#     "client": "Cliente ABC",
#     "partes": "A vs B",
#     "jurisdiccion": "Social"
#   }
# }
```

**Features:**
- Legal-specific prompt for URSALL documents
- Extracts parties, jurisdiction, case numbers, dates
- Provides suggested answers to pre-fill questions
- Returns confidence scores

### 3. `app/document_preview.py`

Orchestration service that combines Dolphin + Gemini.

**Key Function: `generate_document_preview()`**

```python
from app.document_preview import generate_document_preview

preview = await generate_document_preview(
    file_path="/path/to/file.pdf",
    file_id="uuid-123",
    target_use="legal"
)

# Returns complete preview ready for frontend
```

**Features:**
- Coordinates Dolphin parsing and Gemini summarization
- Handles errors gracefully with fallbacks
- Returns unified response structure
- Determines suggested workflow (URSALL vs standard)

---

## API Endpoints

### POST `/api/document/preview`

Generate document preview after upload.

**Request:**
```json
{
  "file_id": "uuid-from-upload-temp",
  "target_use": "legal"  // or "general"
}
```

**Response:**
```json
{
  "file_id": "uuid",
  "status": "success",
  "preview": {
    "summary": "Demanda de despido presentada ante el Juzgado Social...",
    "document_type": "demanda",
    "confidence": 0.92,
    "is_legal_document": true,
    "pages": 5,
    "has_tables": true,
    "has_figures": false,
    "suggested_workflow": "ursall",
    "key_information": {
      "partes": ["Juan Pérez", "Empresa XYZ S.L."],
      "jurisdiccion": "Social",
      "juzgado": "Juzgado Social 2 de Tenerife",
      "numero_procedimiento": "455/2025"
    },
    "suggested_answers": {
      "client": "Juan Pérez",
      "partes": "Juan Pérez vs Empresa XYZ S.L.",
      "jurisdiccion": "Social"
    }
  },
  "raw_text": "Primera parte del texto extraído...",
  "error": null
}
```

### POST `/api/document/confirm`

User confirms or rejects the preview.

**Request:**
```json
{
  "file_id": "uuid",
  "confirmed": true  // or false to cancel
}
```

**Response:**
```json
{
  "success": true,
  "message": "Documento confirmado. Puedes proceder con las preguntas."
}
```

If `confirmed: false`, the temp file is deleted and the user can upload a new document.

### GET `/api/document/preview/status`

Check if preview service is available.

**Response:**
```json
{
  "dolphin_available": true,
  "gemini_available": true,
  "preview_available": true,
  "message": "Document preview service fully operational"
}
```

---

## Frontend Integration (TODO)

The frontend needs to be updated to:

1. **After upload**: Call `/api/document/preview` instead of going directly to questions
2. **Show preview UI**: Display the summary, document type, confidence, and key information
3. **Confirmation buttons**:
   - "Confirmar y Continuar" → Calls `/api/document/confirm` with `confirmed: true`, then starts questions
   - "Cancelar y Subir Otro" → Calls `/api/document/confirm` with `confirmed: false`, resets flow

### Suggested UI Flow

```typescript
// After upload
const uploadResponse = await uploadFile(file);
const fileId = uploadResponse.file_id;

// Get preview
const preview = await fetch('/api/document/preview', {
  method: 'POST',
  body: JSON.stringify({ file_id: fileId, target_use: 'legal' })
});

// Show preview to user
showPreview({
  summary: preview.preview.summary,
  type: preview.preview.document_type,
  confidence: preview.preview.confidence,
  keyInfo: preview.preview.key_information
});

// User clicks "Confirmar"
await fetch('/api/document/confirm', {
  method: 'POST',
  body: JSON.stringify({ file_id: fileId, confirmed: true })
});

// Now start question flow
await startQuestions(fileId);
```

---

## Installation & Setup

### 1. Dolphin Model Download

Download the Dolphin model files:

**Option A: Google Drive**
```bash
# Download from: https://drive.google.com/drive/folders/1PQJ3UutepXvunizZEw-uGaQ0BCzf-mie
# Place files in: backend/Dolphin/checkpoints/
```

**Option B: Baidu Yun**
```bash
# Download from: https://pan.baidu.com/s/15zcARoX0CTOHKbW8bFZovQ?pwd=9rpx
# Place files in: backend/Dolphin/checkpoints/
```

Required files:
- `dolphin_model.bin` (~300MB)
- `dolphin_tokenizer.json`

### 2. Install Dependencies

Dolphin dependencies are already in `requirements.txt`:

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- PyTorch + TorchVision
- Transformers, Accelerate
- OpenCV, Pillow
- PyMuPDF (for PDF parsing)
- OmegaConf

### 3. Configure Gemini API

Ensure `GEMINI_API_KEY` is set in `backend/.env`:

```bash
GEMINI_API_KEY=your_key_here
```

Get a free API key at: https://aistudio.google.com/app/apikey

---

## Configuration

### Dolphin Config

Located at: `backend/Dolphin/config/Dolphin.yaml`

```yaml
model:
  model_name_or_path: "./checkpoints/dolphin_model.bin"
  tokenizer_path: "./checkpoints/dolphin_tokenizer.json"
  max_length: 4096
  decoder_layer: 10
  # ... (see file for full config)
```

### Batch Size Tuning

Adjust `max_batch_size` in the preview service for performance:

```python
# In dolphin_parser.py, adjust batch size
parsed_content, confidence = parser.parse_document(
    file_path,
    max_batch_size=4  # Increase for faster processing (needs more GPU/RAM)
)
```

---

## Advantages

### User Experience
1. **Early validation**: User sees if document is correct BEFORE answering 11 questions
2. **Visual context**: Summary helps confirm the right file was uploaded
3. **Confidence indicator**: User knows if analysis is reliable
4. **Time savings**: Avoids wasting time on wrong documents

### Technical
1. **Modular**: Each component (Dolphin, Gemini, Preview) is independent
2. **Reusable**: `DolphinParser` can be used in other contexts
3. **Fallback support**: If Dolphin fails, normal flow continues
4. **Cacheable**: Parse results can be cached to avoid re-processing

### Legal (URSALL)
1. **Smart extraction**: Gemini pre-identifies parties, jurisdiction, case numbers
2. **Auto-suggestions**: Can pre-fill answers for questions
3. **Validation**: Detects if document is NOT legal (wrong upload)

---

## Error Handling

The system handles errors gracefully:

1. **Dolphin unavailable**: Returns basic preview without AI parsing
2. **Gemini unavailable**: Returns basic preview with Dolphin data only
3. **Both unavailable**: User sees message to check configuration
4. **Parse failure**: Error message with details, user can retry

Check service status:
```bash
curl http://localhost:8000/api/document/preview/status
```

---

## Performance

### Dolphin Parsing
- **Single page PDF**: ~2-3 seconds
- **Multi-page PDF (5 pages)**: ~8-12 seconds
- **Large PDF (20+ pages)**: ~30-60 seconds

### Gemini Summarization
- **Typical document**: ~1-3 seconds
- Depends on text length and API latency

### Total Preview Generation
- **Typical case**: 5-10 seconds
- Shows loading indicator to user

---

## Testing

### Manual Testing

1. Start backend:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Test preview endpoint:
```bash
# Upload a file first
curl -X POST http://localhost:8000/api/upload-temp \
  -F "file=@/path/to/document.pdf"

# Get file_id from response, then:
curl -X POST http://localhost:8000/api/document/preview \
  -H "Content-Type: application/json" \
  -d '{"file_id": "uuid-here", "target_use": "legal"}'
```

3. Check logs for Dolphin + Gemini processing details

### Unit Testing (TODO)

Add tests in `backend/tests/`:
- `test_dolphin_parser.py`
- `test_gemini_summarizer.py`
- `test_document_preview.py`

---

## Future Enhancements

1. **Cache parsed results**: Store in Redis/database to avoid re-parsing
2. **Async processing**: Return preview link, poll for completion
3. **Multi-language support**: Extend Gemini prompts for other languages
4. **Advanced validation**: Check if document matches expected type
5. **Image preview**: Show document thumbnail alongside summary
6. **Confidence thresholds**: Warn user if confidence < 0.7

---

## Troubleshooting

### Dolphin fails to load

**Error:** `ImportError: No module named 'chat'`

**Fix:** Ensure Dolphin dependencies are installed:
```bash
pip install -r backend/Dolphin/requirements.txt
```

### Model not found

**Error:** `FileNotFoundError: dolphin_model.bin not found`

**Fix:** Download model files to `backend/Dolphin/checkpoints/`

### Gemini quota exceeded

**Error:** `429 Resource Exhausted`

**Fix:** Gemini free tier has limits (15 RPM, 1500 RPD). Wait or upgrade to paid tier.

### Preview is slow

**Solutions:**
1. Reduce `max_batch_size` if running out of memory
2. Use GPU instead of CPU for Dolphin (requires CUDA)
3. Enable preview caching (future enhancement)

---

## References

- **Dolphin Paper**: [arXiv:2505.14059](https://arxiv.org/abs/2505.14059)
- **Dolphin GitHub**: [bytedance/Dolphin](https://github.com/bytedance/Dolphin)
- **Gemini API**: [Google AI Studio](https://aistudio.google.com)
- **URSALL Docs**: See `docs/URSALL_IMPLEMENTATION.md`

---

## Summary

The Dolphin + Gemini integration provides:
- ✅ Intelligent document preview before questions
- ✅ Automatic information extraction for URSALL
- ✅ Improved user experience and reduced errors
- ✅ Modular, extensible architecture
- ✅ Graceful error handling and fallbacks

**Next Step:** Implement frontend UI to display preview and confirmation flow.
