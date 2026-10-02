#!/usr/bin/env python3
"""
Images Sync Script for Obsidian to Hugo
========================================
This script syncs images from Obsidian attachments folder to Hugo's static/images folder
and updates the markdown files to point to the correct image paths.

Features:
- Finds images recursively in subfolders
- Handles spaces in filenames (replaces with underscores)
- Updates markdown image references

Usage:
    python3 images.py
"""

import os
import re
import shutil
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

OBSIDIAN_ATTACHMENTS_DIR = "/home/thaus/GoogleDrive/Obsidian/attachments"
HUGO_STATIC_IMAGES_DIR = "/home/thaus/Documents/my-blog/static/images"
HUGO_POSTS_DIR = "/home/thaus/Documents/my-blog/content/posts"

# ============================================
# HELPER FUNCTIONS
# ============================================

def find_all_images(attachments_dir):
    """Find all image files recursively in attachments folder."""
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}
    images = {}
    
    for root, dirs, files in os.walk(attachments_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                # Store original path and clean path (spaces to underscores)
                clean_name = file.replace(' ', '_')
                original_path = os.path.join(root, file)
                images[clean_name.lower()] = {
                    'original_name': file,
                    'clean_name': clean_name,
                    'original_path': original_path,
                    'folder': os.path.basename(root)
                }
    
    return images

def slugify_filename(filename):
    """Convert filename to URL-friendly format."""
    # Replace spaces with underscores
    slug = filename.replace(' ', '_')
    # Remove any other problematic characters
    slug = re.sub(r'[^\w\-\.]', '_', slug)
    return slug

def find_image_in_attachments(image_name, all_images):
    """Find image by name, handling spaces and variations."""
    # Try exact match first
    if image_name in all_images:
        return all_images[image_name]
    
    # Try with spaces replaced by underscores
    clean_name = image_name.replace(' ', '_').lower()
    if clean_name in all_images:
        return all_images[clean_name]
    
    # Try case-insensitive match
    lower_name = image_name.lower()
    for key, data in all_images.items():
        if key.lower() == lower_name or data['original_name'].lower() == lower_name:
            return data
    
    return None

def find_markdown_files(directory):
    """Find all markdown files in the given directory."""
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

def process_markdown_file(filepath, static_images_dir, all_images, logger):
    """Process a markdown file and update image references."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    images_copied = []
    
    # Regex to find markdown images: ![alt](path/to/image.png)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+\.(?:png|jpg|jpeg|gif|webp|svg))\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        filename = os.path.basename(image_path)
        
        # Find the image in our collection
        image_data = find_image_in_attachments(filename, all_images)
        
        if image_data:
            # Use clean filename (no spaces) for the static folder
            dest_filename = image_data['clean_name']
            source_path = image_data['original_path']
            dest_path = os.path.join(static_images_dir, dest_filename)
            
            # Copy image to Hugo static/images
            if not os.path.exists(dest_path):
                shutil.copy2(source_path, dest_path)
                logger(f"  Copied: {image_data['original_name']} -> {dest_filename}")
            
            images_copied.append(dest_filename)
            
            # Return new path with clean filename
            return f'![{alt_text}](/images/{dest_filename})'
        else:
            logger(f"  Warning: Image not found: {filename}")
            return match.group(0)
    
    content = re.sub(image_pattern, replace_image, content)
    
    # Write updated content if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return images_copied

def main():
    print("=" * 50)
    print("Obsidian to Hugo Image Sync (Enhanced)")
    print("=" * 50)
    
    # Verify directories exist
    if not os.path.exists(OBSIDIAN_ATTACHMENTS_DIR):
        print(f"Error: Obsidian attachments directory not found: {OBSIDIAN_ATTACHMENTS_DIR}")
        return
    
    if not os.path.exists(HUGO_STATIC_IMAGES_DIR):
        os.makedirs(HUGO_STATIC_IMAGES_DIR)
        print(f"Created directory: {HUGO_STATIC_IMAGES_DIR}")
    
    # Find all images recursively
    print("\nScanning attachments folder...")
    all_images = find_all_images(OBSIDIAN_ATTACHMENTS_DIR)
    print(f"Found {len(all_images)} images in attachments")
    
    # Show sample images found
    sample = list(all_images.items())[:5]
    if sample:
        print("Sample images:")
        for key, data in sample:
            print(f"  - {data['original_name']} (folder: {data['folder']})")
    
    # Find and process markdown files
    md_files = find_markdown_files(HUGO_POSTS_DIR)
    print(f"\nFound {len(md_files)} markdown files")
    
    total_images = 0
    for md_file in md_files:
        rel_path = os.path.relpath(md_file, HUGO_POSTS_DIR)
        print(f"\nProcessing: {rel_path}")
        
        images = process_markdown_file(
            md_file, 
            HUGO_STATIC_IMAGES_DIR, 
            all_images,
            print
        )
        total_images += len(images)
    
    print("-" * 50)
    print(f"Markdown files processed: {len(md_files)}")
    print(f"Images copied: {total_images}")
    print("-" * 50)
    
    if total_images > 0:
        print("Image sync completed successfully!")
        print(f"Images are in: {HUGO_STATIC_IMAGES_DIR}")
    else:
        print("No images were copied. Check your markdown files reference images correctly.")

if __name__ == "__main__":
    main()
