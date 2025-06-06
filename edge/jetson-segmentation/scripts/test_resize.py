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
    parser.add_argument('--max_size', type=int, default=512, help='Maximum size for image dimension')
    return parser.parse_args()

def resize_image(image, max_size):
    """Resize image while maintaining aspect ratio"""
    ratio = max_size / max(image.size)
    if ratio < 1:
        new_size = tuple(int(dim * ratio) for dim in image.size)
        return image.resize(new_size, Image.Resampling.LANCZOS)
    return image

def process_image(image_path, model, preprocessor, output_dir, max_size=1024):
    """Process a single image and save results"""
    # Load and resize image
    image = Image.open(image_path).convert("RGB")
    image = resize_image(image, max_size)
    
    # Get the basename for the output file
    basename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Clear CUDA cache
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # Preprocess and run inference
    inputs = preprocessor(image, return_tensors="pt")
    
    # Move inputs to GPU if available
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
        model = model.cuda()
    
    # Run inference
    with torch.no_grad():
        outputs = model(**inputs)
        
    # Clear CUDA cache again
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
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
    image_files = glob.glob(os.path.join(args.input_dir, "*.[jp][pn][pg]"))
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
                max_size=args.max_size
            )
            print(f"Processed {image_path} -> {output_path}")
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    print(f"Processing complete. Results saved to {args.output_dir}")

if __name__ == "__main__":
    main()
