from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from datetime import datetime
import pytz

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production (e.g., specific origins)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = 'upload_log.json'

# Load history from JSON file
def load_history():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return []

# Save history to JSON file
def save_history(history):
    with open(LOG_FILE, 'w') as f:
        json.dump(history, f, indent=4)

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    if not files or not any(file.filename for file in files):
        raise HTTPException(status_code=400, detail="No selected files")
    
    history = load_history()
    cst = pytz.timezone('America/Chicago')
    now = datetime.now(cst).strftime('%Y-%m-%d %I:%M:%S %p %Z')
    
    uploaded_files = []
    for file in files:
        if file.filename.endswith('.zip'):
            # Here, you could save the file if needed: with open(os.path.join('uploads', file.filename), 'wb') as f: f.write(await file.read())
            log_entry = {'name': file.filename, 'date': now}
            if not any(entry['name'] == log_entry['name'] and entry['date'] == log_entry['date'] for entry in history):
                history.append(log_entry)
                uploaded_files.append(log_entry)
    
    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No valid .zip files uploaded")
    
    save_history(history)
    return {"message": "Files uploaded and logged successfully", "uploaded": uploaded_files}

@app.get("/history")
async def get_history():
    history = load_history()
    return history

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
