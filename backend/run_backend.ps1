$env:PYTHONUNBUFFERED = "1"
Set-Location "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\backend"
& "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\backend\venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "C:\Users\amartin\Documents\Aplicativos\Dropbox_Chatbot\logs\backend_20251017_135057.log" 2>&1
