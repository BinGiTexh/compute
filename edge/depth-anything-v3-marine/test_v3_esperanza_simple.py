#!/usr/bin/env python3
# Test V3 with ESPERANZA - Simple approach
import os
print('=== V3 ESPERANZA TEST ===')

# Check if video exists
video_file = '/jetson-ssd/20251107_ESPERANZA_T2_20M_V1_AR.mp4'
if os.path.exists(video_file):
    file_size = os.path.getsize(video_file) / (1024*1024)
    print(f'✅ ESPERANZA video found: {file_size:.1f}MB')
    
    # Basic CV2 test (avoid numpy issues)
    try:
        import cv2
        cap = cv2.VideoCapture(video_file)
        if cap.isOpened():
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f'✅ Video: {frame_count} frames, {fps}fps, {width}x{height}')
            
            # Read one frame
            ret, frame = cap.read()
            if ret:
                print(f'✅ Frame read: {frame.shape}')
                print('🎉 V3 CONTAINER + ESPERANZA = READY!')
            cap.release()
        else:
            print('❌ Could not open video')
    except Exception as e:
        print(f'Video test error: {e}')
else:
    print('❌ ESPERANZA video not found')
