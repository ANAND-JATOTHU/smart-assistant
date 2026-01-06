# Smart Assistant - Git Setup Guide

## Initial Git Setup

Follow these steps to set up version control for Smart Assistant:

### 1. **Initialize Git Repository**
```bash
cd "c:\Users\JATOTHU ANAND\Desktop\sruthi ai"
git init
```

### 2. **Create .gitignore File**
Create a `.gitignore` file to exclude unnecessary files:
```
# Virtual Environment
env_sruthi/

# Python Cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Data Files (personal conversations)
data/memory.json

# Model Files (too large for Git)
*.gguf
*.bin
models/*.gguf

# Temporary Files
assets/temp_*.wav
*.tmp
*.log

# IDE Settings
.vscode/
.idea/
*.code-workspace

# OS Files
.DS_Store
Thumbs.db
desktop.ini

# Environment Variables (contains paths)
.env
```

### 3. **Configure Git User**
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 4. **Make Initial Commit**
```bash
git add .
git commit -m "Initial commit: Smart Assistant with ChatGPT-style GUI"
```

## Version Management

### **Creating Named Versions (Tags)**

#### Mark Current Version
```bash
# Create a tag for current stable version
git tag -a v1.0.0 -m "Version 1.0.0 - Smart Assistant with modern GUI"
```

#### Create Version for Specific Feature
```bash
# After completing a feature, commit and tag
git add .
git commit -m "Added chat management features (rename/delete)"
git tag -a v1.1.0 -m "Version 1.1.0 - Chat management features"
```

### **Viewing Versions**
```bash
# List all versions
git tag -l

# View specific version details
git show v1.0.0

# View version history
git log --oneline --decorate
```

### **Switching Between Versions**
```bash
# Go back to specific version
git checkout v1.0.0

# Return to latest version
git checkout main
```

### **Comparing Versions**
```bash
# See changes between versions
git diff v1.0.0 v1.1.0

# See what changed in specific files
git diff v1.0.0 v1.1.0 -- gui/app_chatgpt_style.py
```

## Recommended Versioning Strategy

### **Version Number Format: X.Y.Z**
- **X (Major)**: Breaking changes, major redesign
- **Y (Minor)**: New features added
- **Z (Patch)**: Bug fixes, small improvements

### **Example Workflow**

1. **Working on new features:**
   ```bash
   git add .
   git commit -m "Added voice streaming feature"
   ```

2. **Completed feature - create minor version:**
   ```bash
   git tag -a v1.2.0 -m "Version 1.2.0 - Voice streaming"
   ```

3. **Bug fix - create patch version:**
   ```bash
   git commit -m "Fixed scroll bug in chat history"
   git tag -a v1.2.1 -m "Version 1.2.1 - Fixed scroll bug"
   ```

## Branching for Experiments

### **Create Feature Branch**
```bash
# Create and switch to new branch for experimental feature
git checkout -b feature/new-tts-engine

# Work on code...
git add .
git commit -m "Experimenting with Coqui TTS"

# If successful, merge back to main
git checkout main
git merge feature/new-tts-engine

# If not successful, just switch back without merging
git checkout main
```

## Backup to GitHub (Optional)

### **Setup Remote Repository**
```bash
# After creating repo on GitHub
git remote add origin https://github.com/yourusername/smart-assistant.git
git branch -M main
git push -u origin main

# Push tags
git push --tags
```

## Quick Reference Commands

```bash
# Check current status
git status

# View commit history
git log --oneline --graph --all

# Create new version
git tag -a v1.X.X -m "Description"

# List all versions
git tag -l

# Go to specific version
git checkout v1.X.X

# Return to latest
git checkout main

# Save work in progress
git stash

# Restore saved work
git stash pop
```

## Current Recommended Tags

Based on your development so far:

```bash
# Tag major milestones
git tag -a v0.1.0 -m "Initial SRUTHI-AI"
git tag -a v1.0.0 -m "ChatGPT-style GUI with sidebar"
git tag -a v1.1.0 -m "Chat management (rename/delete)"
git tag -a v1.2.0 -m "Enhanced search commands"
```

## Troubleshooting

**Undo last commit (before push):**
```bash
git reset --soft HEAD~1
```

**Discard all local changes:**
```bash
git reset --hard HEAD
```

**View what changed:**
```bash
git diff
```
