#!/bin/bash
#
# ============================================================
# MEGA SCRIPT: Obsidian → Hugo → GitHub Blog Pipeline
# ============================================================
#
# This script automates the entire blogging workflow:
# 1. Sync posts from Obsidian vault to Hugo content folder
# 2. Sync images from Obsidian attachments to Hugo static/images
# 3. Build the Hugo site
# 4. Commit and push to GitHub (master branch)
# 5. Push to hosting branch (gh-pages or hoster)
#
# ============================================================

# ============================================
# CONFIGURATION - Edit these paths as needed
# ============================================

# Path to your Obsidian vault posts folder
OBSIDIAN_POSTS_DIR="/path/to/your/Obsidian/vault/posts"

# Path to your Obsidian vault attachments folder
OBSIDIAN_ATTACHMENTS_DIR="/path/to/your/Obsidian/vault/attachments"

# Git repository URL (SSH format recommended)
GIT_REPO="git@github.com:YOUR_USERNAME/YOUR_REPO.git"

# GitHub username
GIT_USERNAME="YOUR_USERNAME"

# Commit message (optional, defaults to auto-generated)
COMMIT_MESSAGE=""

# ============================================
# COLORS
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# SCRIPT START
# ============================================
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  OBSIDIAN → HUGO BLOG PIPELINE${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if we're in the Hugo directory
if [ ! -f "hugo.toml" ] && [ ! -f "config.toml" ]; then
    echo -e "${RED}Error: This script must be run from your Hugo blog directory.${NC}"
    echo "Current directory: $(pwd)"
    echo ""
    echo "Please navigate to your Hugo blog directory and run this script again."
    exit 1
fi

# ============================================
# STEP 1: Sync posts from Obsidian
# ============================================
echo -e "${YELLOW}Step 1: Syncing posts from Obsidian...${NC}"

if [ ! -d "$OBSIDIAN_POSTS_DIR" ]; then
    echo -e "${RED}Error: Obsidian posts directory not found: $OBSIDIAN_POSTS_DIR${NC}"
    echo "Please update the OBSIDIAN_POSTS_DIR path in this script."
    exit 1
fi

# Create content/posts directory if it doesn't exist
mkdir -p content/posts

# Sync posts using rsync (Linux/Mac)
rsync -av --delete "$OBSIDIAN_POSTS_DIR/" "content/posts/"
echo -e "${GREEN}✓ Posts synced successfully!${NC}"
echo ""

# ============================================
# STEP 2: Sync images from Obsidian
# ============================================
echo -e "${YELLOW}Step 2: Syncing images from Obsidian...${NC}"

if [ ! -d "$OBSIDIAN_ATTACHMENTS_DIR" ]; then
    echo -e "${RED}Error: Obsidian attachments directory not found: $OBSIDIAN_ATTACHMENTS_DIR${NC}"
    echo "Please update the OBSIDIAN_ATTACHMENTS_DIR path in this script."
    exit 1
fi

# Create static/images directory if it doesn't exist
mkdir -p static/images

# Run Python script to sync images and update markdown paths
python3 images.py
echo -e "${GREEN}✓ Images synced successfully!${NC}"
echo ""

# ============================================
# STEP 3: Build Hugo site
# ============================================
echo -e "${YELLOW}Step 3: Building Hugo site...${NC}"
hugo
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Hugo site built successfully!${NC}"
else
    echo -e "${RED}✗ Hugo build failed!${NC}"
    exit 1
fi
echo ""

# ============================================
# STEP 4: Git add and commit
# ============================================
echo -e "${YELLOW}Step 4: Committing changes to Git...${NC}"

# Generate commit message if not provided
if [ -z "$COMMIT_MESSAGE" ]; then
    COMMIT_MESSAGE="Blog update: $(date '+%Y-%m-%d %H:%M:%S')"
fi

git add -A
git commit -m "$COMMIT_MESSAGE"
echo -e "${GREEN}✓ Changes committed!${NC}"
echo ""

# ============================================
# STEP 5: Push to GitHub master/main branch
# ============================================
echo -e "${YELLOW}Step 5: Pushing to GitHub (main branch)...${NC}"
git push origin main
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Pushed to GitHub main branch!${NC}"
else
    echo -e "${RED}✗ Failed to push to GitHub!${NC}"
    exit 1
fi
echo ""

# ============================================
# STEP 6: Push public folder to hosting branch
# ============================================
echo -e "${YELLOW}Step 6: Deploying to hosting branch...${NC}"

# Using subtree push to deploy only the public folder
git subtree push --prefix public origin gh-pages
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deployed to hosting branch (gh-pages)!${NC}"
else
    echo -e "${YELLOW}Note: gh-pages branch deployment failed.${NC}"
    echo "This is normal if this is your first push."
    echo "You may need to initialize the gh-pages branch manually:"
    echo "  git push origin \$(git subtree split --prefix public main):gh-pages --force"
fi
echo ""

# ============================================
# COMPLETION
# ============================================
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  BLOG PIPELINE COMPLETED!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Your blog has been updated and deployed!"
echo "It may take a few minutes for changes to appear on your live site."
echo ""
