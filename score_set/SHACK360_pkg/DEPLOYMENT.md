# Counter - Community Savings Platform

## Deployment Fix Guide

### If Vercel Isn't Picking Up Changes:

1. **Force Redeploy in Vercel Dashboard:**
   - Go to your Vercel dashboard
   - Click on your project
   - Go to "Deployments" tab
   - Click the three dots (...) on the latest deployment
   - Select "Redeploy" → Check "Use existing Build Cache" should be **UNCHECKED**
   - Click "Redeploy"

2. **Clear Build Cache:**
   ```bash
   # In Vercel dashboard:
   Settings → General → Build & Development Settings
   → Click "Clear Build Cache"
   ```

3. **Verify Git Integration:**
   - Settings → Git → Make sure it's connected to `main` branch
   - Enable "Automatically deploy" for the main branch

4. **Force Push (if needed):**
   ```bash
   git commit --allow-empty -m "Force rebuild"
   git push origin main
   ```

5. **Check Environment Variables:**
   - Settings → Environment Variables
   - Make sure `DATABASE_URL` is set
   - Make sure `SECRET_KEY` is set

### Quick Deploy Commands:

```bash
# Make changes
git add .
git commit -m "Your message"
git push origin main

# If Vercel doesn't auto-deploy, force it:
git commit --allow-empty -m "trigger deploy"
git push
```

### Common Issues:

- **Old cached content**: Clear browser cache (Ctrl+Shift+R)
- **Database not updated**: Migrations run automatically via `build_files.sh`
- **Changes not reflected**: Check Vercel deployment logs for errors

## Local Development

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run migrations
python manage.py migrate

# Create test data
python manage.py create_notifications

# Run server
python manage.py runserver
```
