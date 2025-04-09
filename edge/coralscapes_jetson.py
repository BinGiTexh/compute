import os
import glob
import argparse
import numpy as np
from PIL import Image
import torch
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description='Process images from a local directory using Segformer model')
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing input images')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to save output predictions')
    parser.add_argument('--model_path', type=str, default="EPFL-ECEO/segformer-b5-finetuned-coralscapes-1024-1024", 
                        help='Path to the model or HuggingFace model name')
    parser.add_argument('--save_overlay', action='store_true', help='Save overlay visualizations')
    parser.add_argument('--overlay_alpha', type=float, default=0.6, help='Alpha value for overlay visualization')
    return parser.parse_args()

def get_image_files(directory):
    """Get all image files in a directory"""
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff']
    image_files = []
    
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
        image_files.extend(glob.glob(os.path.join(directory, '**', ext), recursive=True))
    
    return sorted(list(set(image_files)))  # Remove duplicates and sort

def process_image(image_path, model, preprocessor, output_dir, save_overlay=False, overlay_alpha=0.6):
    """Process a single image and save results"""
    # Load image
    image = Image.open(image_path).convert("RGB")
    
    # Get the basename for the output file
    basename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Preprocess and run inference
    inputs = preprocessor(image, return_tensors="pt")
    
    # Move inputs to GPU if available
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
        model = model.cuda()
    
    # Run inference
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Post-process
    seg_preds = preprocessor.post_process_semantic_segmentation(
        outputs, target_sizes=[(image.size[1], image.size[0])]
    )
    
    # Convert to numpy array
    label_pred = seg_preds[0].cpu().numpy()
    
    # Save prediction as image
    pred_image = Image.fromarray(label_pred.astype(np.uint8))
    pred_path = os.path.join(output_dir, f"{basename}_pred.png")
    pred_image.save(pred_path)
    
    # Optionally create and save overlay visualization
    if save_overlay:
        # You would need a mapping from label indices to colors
        # For simplicity, let's create a colorized version using a simple colormap
        # In a real application, you would use id2color from the original code
        from matplotlib import cm
        
        # Create a colormap (adjust number of classes as needed)
        num_classes = outputs.logits.shape[1]  # Get number of classes from model output
        colormap = cm.get_cmap('viridis', num_classes)
        
        # Create RGB image from prediction
        colored_pred = np.zeros((label_pred.shape[0], label_pred.shape[1], 3), dtype=np.uint8)
        for i in range(num_classes):
            mask = label_pred == i
            color = np.array(colormap(i)[:3]) * 255
            colored_pred[mask] = color
        
        # Create overlay
        overlay_img = Image.fromarray(colored_pred)
        overlay = Image.blend(image, overlay_img, alpha=overlay_alpha)
        
        # Save overlay
        overlay_path = os.path.join(output_dir, f"{basename}_overlay.png")
        overlay.save(overlay_path)
    
    return pred_path

def main():
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load model and preprocessor
    print(f"Loading model from {args.model_path}...")
    preprocessor = SegformerImageProcessor.from_pretrained(args.model_path)
    model = SegformerForSemanticSegmentation.from_pretrained(args.model_path)
    model.eval()
    
    # Get list of images
    image_files = get_image_files(args.input_dir)
    if not image_files:
        print(f"No image files found in {args.input_dir}")
        return
    
    print(f"Found {len(image_files)} images. Processing...")
    
    # Process each image
    for image_path in tqdm(image_files):
        try:
            output_path = process_image(
                image_path, 
                model, 
                preprocessor, 
                args.output_dir,
                save_overlay=args.save_overlay,
                overlay_alpha=args.overlay_alpha
            )
            print(f"Processed {image_path} -> {output_path}")
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
    
    print(f"Processing complete. Results saved to {args.output_dir}")

if __name__ == "__main__":
    main()
