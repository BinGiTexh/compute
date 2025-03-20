# import the inference-sdk
from inference_sdk import InferenceHTTPClient

API_KEY=

# initialize the client
CLIENT = InferenceHTTPClient(
    api_url="http://localhost:9001",
    api_key=API_KEY
)

MODEL_ID="fish-scuba-project/2"
VIDEO = "GH011294.MP4"


# infer on a local image
#result = CLIENT.infer("YOUR_IMAGE.jpg", model_id="fish-scuba-project/2")
for frame_id, frame, prediction in CLIENT.infer_on_stream(VIDEO, MODEL_ID):
    print(frame_id, frame, prediction)
