import os
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from inference_sdk import InferenceHTTPClient
import uvicorn
from typing import Dict, Any

app = FastAPI(title="Video Processing Inference Server")

# Initialize the Roboflow client
client = InferenceHTTPClient(
    api_key=os.environ.get("ROBOFLOW_API_KEY"),
)

@app.post("/predict")
async def predict(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Process an image and return predictions.
    """
    # Read and decode image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Get predictions from model
    try:
        result = client.infer(
            image,
            model_id=os.environ.get("MODEL_ID", "fish-scuba-project/2")
        )
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Check server health.
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("INFERENCE_SERVER_PORT", 9001))
    uvicorn.run(app, host="0.0.0.0", port=port)
