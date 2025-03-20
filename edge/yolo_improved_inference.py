from ultralytics import YOLO
import cv2
import argparse
import os
import time

def process_video(model_path, video_path=None, output_path=None, device=0, use_trt=True):
    """
    Process a video with YOLO pose detection.
    
    Args:
        model_path (str): Path to the YOLO model file (.pt or .engine)
        video_path (str, optional): Path to video file. If None, uses webcam.
        output_path (str, optional): Path to save the processed video. If None, doesn't save.
        device (int or str): Camera device number or video path.
        use_trt (bool): Whether to export and use TensorRT model.
    """
    # Load the YOLO model
    if use_trt and model_path.endswith('.pt'):
        print(f"Loading model {model_path} and exporting to TensorRT...")
        model = YOLO(model_path)
        engine_path = model_path.replace('.pt', '.engine')
        model.export(format="engine")  # creates engine file
        model = YOLO(engine_path)
        print(f"TensorRT model loaded from {engine_path}")
    else:
        print(f"Loading model {model_path}...")
        model = YOLO(model_path)
    
    # Open the video source (file or camera)
    if video_path:
        print(f"Opening video file: {video_path}")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return
    else:
        print(f"Opening camera device: {device}")
        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            print(f"Error: Could not open camera device {device}")
            return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if video_path else 0
    
    # Setup video writer if output path is specified
    writer = None
    if output_path:
        print(f"Setting up video writer to save to {output_path}")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Variables for performance tracking
    frame_count = 0
    start_time = time.time()
    
    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()
        if not success:
            break
        
        # Run YOLO inference on the frame
        results = model(frame)
        
        # Visualize the results on the frame
        annotated_frame = results[0].plot()
        
        # Write frame to output video if a writer is set up
        if writer:
            writer.write(annotated_frame)
        
        # Display the annotated frame
        cv2.imshow("YOLO Inference", annotated_frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
        # Update frame count and print progress
        frame_count += 1
        if frame_count % 30 == 0:
            elapsed_time = time.time() - start_time
            fps_processing = frame_count / elapsed_time
            if total_frames > 0:
                progress = (frame_count / total_frames) * 100
                print(f"Processed {frame_count}/{total_frames} frames ({progress:.1f}%) at {fps_processing:.2f} FPS")
            else:
                print(f"Processed {frame_count} frames at {fps_processing:.2f} FPS")
    
    # Release resources
    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    
    # Print summary
    elapsed_time = time.time() - start_time
    fps_processing = frame_count / elapsed_time if elapsed_time > 0 else 0
    print(f"Processing complete: {frame_count} frames processed in {elapsed_time:.2f} seconds ({fps_processing:.2f} FPS)")
    if output_path:
        print(f"Output saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a video with YOLO pose detection")
    parser.add_argument("--model", type=str, default="yolov11n-pose.pt", 
                        help="Path to the YOLO model file (.pt or .engine)")
    parser.add_argument("--video", type=str, default=None, 
                        help="Path to input video file (if not specified, uses webcam)")
    parser.add_argument("--output", type=str, default=None, 
                        help="Path to save output video (if not specified, doesn't save)")
    parser.add_argument("--device", type=int, default=0, 
                        help="Camera device number (only used if no video path provided)")
    parser.add_argument("--no-trt", action="store_true", 
                        help="Disable TensorRT export and use PyTorch model directly")
    
    args = parser.parse_args()
    
    process_video(
        model_path=args.model,
        video_path=args.video,
        output_path=args.output,
        device=args.device,
        use_trt=not args.no_trt
    )
