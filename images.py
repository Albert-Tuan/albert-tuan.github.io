#!/usr/bin/env python3
"""
Images Sync Script for Obsidian to Hugo
========================================
This script syncs images from Obsidian attachments folder to Hugo's static/images folder
and updates the markdown files to point to the correct image paths.

Usage:
    python3 images.py

Configuration:
    Edit the paths below to match your Obsidian vault location.
"""

import os
import re
import shutil
from pathlib import Path

# ============================================
# CONFIGURATION - Edit these paths as needed
# ============================================

# Path to your Obsidian posts folder (where you write your blogs)
OBSIDIAN_POSTS_DIR = "/path/to/your/Obsidian/vault/posts"

# Path to your Obsidian vault attachments folder (where Obsidian stores images)
OBSIDIAN_ATTACHMENTS_DIR = "/home/thaus/GoogleDrive/Obsidian/attachments"

# Path to your Hugo static/images folder
HUGO_STATIC_IMAGES_DIR = "/home/thaus/Documents/my-blog/static/images"

# Path to your Hugo content/posts folder
HUGO_POSTS_DIR = "/home/thaus/Documents/my-blog/content/posts"

# ============================================
# SCRIPT LOGIC
# ============================================

def find_markdown_files(directory):
    """Find all markdown files in the given directory."""
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

def process_markdown_file(filepath, static_images_dir, attachments_dir, hugo_posts_dir):
    """
    Process a markdown file:
    1. Find image references
    2. Copy images to Hugo static folder
    3. Update image paths in markdown
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    images_copied = []
    
    # Regex to find image references in markdown
    # Matches: ![alt text](image.png) or ![alt text](path/to/image.png)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+\.(?:png|jpg|jpeg|gif|webp|svg))\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # Get just the filename
        filename = os.path.basename(image_path)
        
        # Source path in Obsidian attachments
        source_path = os.path.join(attachments_dir, filename)
        
        # Destination path in Hugo static/images
        dest_path = os.path.join(static_images_dir, filename)
        
        # Copy image if it exists in attachments
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)
            images_copied.append(filename)
            # Return new path pointing to Hugo's images directory
            return f'![{alt_text}](/images/{filename})'
        else:
            # If image not found in attachments, keep original path
            print(f"  Warning: Image not found: {source_path}")
            return match.group(0)
    
    content = re.sub(image_pattern, replace_image, content)
    
    # Write updated content if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return images_copied

def main():
    print("=" * 50)
    print("Obsidian to Hugo Image Sync")
    print("=" * 50)
    
    # Verify directories exist
    if not os.path.exists(OBSIDIAN_POSTS_DIR):
        print(f"Error: Obsidian posts directory not found: {OBSIDIAN_POSTS_DIR}")
        print("Please update the OBSIDIAN_POSTS_DIR path in this script.")
        return
    
    if not os.path.exists(OBSIDIAN_ATTACHMENTS_DIR):
        print(f"Error: Obsidian attachments directory not found: {OBSIDIAN_ATTACHMENTS_DIR}")
        print("Please update the OBSIDIAN_ATTACHMENTS_DIR path in this script.")
        return
    
    if not os.path.exists(HUGO_STATIC_IMAGES_DIR):
        os.makedirs(HUGO_STATIC_IMAGES_DIR)
        print(f"Created directory: {HUGO_STATIC_IMAGES_DIR}")
    
    # Find and process markdown files
    md_files = find_markdown_files(HUGO_POSTS_DIR)
    
    total_images = 0
    for md_file in md_files:
        rel_path = os.path.relpath(md_file, HUGO_POSTS_DIR)
        print(f"Processing: {rel_path}")
        
        images = process_markdown_file(
            md_file, 
            HUGO_STATIC_IMAGES_DIR, 
            OBSIDIAN_ATTACHMENTS_DIR,
            HUGO_POSTS_DIR
        )
        
        for img in images:
            print(f"  - Copied: {img}")
        total_images += len(images)
    
    print("-" * 50)
    print(f"Markdown files processed: {len(md_files)}")
    print(f"Images copied: {total_images}")
    print("-" * 50)
    
    if total_images > 0:
        print("Image sync completed successfully!")
    else:
        print("No images were copied. Check your configuration and ensure your markdown files reference images from the attachments folder.")

if __name__ == "__main__":
    main()
