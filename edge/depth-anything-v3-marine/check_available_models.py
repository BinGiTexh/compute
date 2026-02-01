#!/usr/bin/env python3
"""Check available Depth-Anything models"""

from huggingface_hub import list_models

print("🔍 Searching for Depth-Anything models on Hugging Face...")

# Search for depth-anything models
models = list_models(search="depth-anything", limit=20)

print("\nAvailable models:")
for i, model in enumerate(models):
    print(f"{i+1:2d}. {model.id}")
    if hasattr(model, tags) and model.tags:
        print(f"    Tags: {, .join(model.tags[:5])}")

print(f"\nFound {len(list(models))} models matching depth-anything")
