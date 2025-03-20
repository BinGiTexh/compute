from roboflow import Roboflow

rf = Roboflow(api_key="API_KEY")
project = rf.workspace().project("PROJECT_NAME")
model = project.version(MODEL_ID).model

job_id, signed_url, expire_time = model.predict_video(
    "path_to_video",
    fps=5,
    prediction_type="batch-video",
)

results = model.poll_until_video_results(job_id)

print(results)


