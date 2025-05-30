# 🗂️ Temporary Files Directory

This directory is used for temporary files during development and testing.

## 📁 Contents

- Build artifacts
- Test outputs
- Temporary configurations
- Cache files
- Development scratch files

## 🧹 Cleanup

This directory is automatically cleaned:
- On server startup
- Daily via cron job
- Manually via `scripts/cleanup-temp.py`

## ⚠️ Important

Do not store important files here - they will be deleted automatically!
