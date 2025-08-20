from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import zipfile
import os
import tempfile
import joblib
import logging

app = FastAPI(title="ML Model API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific origins (e.g., ["https://your-ui.netlify.app"]) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model loading
model = None
def load_model():
    global model
    if model is None:
        model = joblib.load("/content/model.pkl")  # Adjust path for Colab or cloud
    return model

@app.post("/predict")
async def predict(files: list[UploadFile] = File(...), model=Depends(load_model)):
    predictions = []
    try:
        for file in files:
            # Validate file type
            if not file.filename.endswith(".zip"):
                raise HTTPException(status_code=400, detail=f"File {_ds} is not a zip file")
            
            # Create temporary directory to extract zip
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, file.filename)
                with open(zip_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                # Extract zip file
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Example: Assume zip contains a CSV file for prediction
                # Replace this with your actual data processing logic
                import pandas as pd
                csv_file = [f for f in os.listdir(temp_dir) if f.endswith(".csv")]
                if not csv_file:
                    raise HTTPException(status_code=400, detail=f"No CSV found in {file.filename}")
                
                # Read CSV and prepare data (customize based on your model)
                data = pd.read_csv(os.path.join(temp_dir, csv_file[0]))
                features = data[["feature1", "feature2"]].values  # Adjust columns
                prediction = model.predict(features)[0]  # Adjust for your model output
                predictions.append({"file_name": file.filename, "prediction": float(prediction)})
        
        return {"predictions": predictions}
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "healthy"}
