#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
```

---

### **Phase 3: Update `settings.py`**

Open `config/settings.py` and make these 4 specific changes.

**A. Add Import at the top:**
```python
import dj_database_url # Add this under 'import os'
```

**B. Update Middleware:**
Add `WhiteNoiseMiddleware` right after `SecurityMiddleware`.

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # <--- ADD THIS NEW LINE
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of list ...
]
```

**C. Update Database Configuration:**
Replace your entire `DATABASES = { ... }` block with this smart configuration. It automatically switches between your local `.env` setup and the live Render database.

```python
# Database
DATABASES = {
    'default': dj_database_url.config(
        # Fallback to local if no URL is found (for development)
        default=os.getenv('DATABASE_URL', f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DB_NAME')}"),
        conn_max_age=600
    )
}
```

**D. Configure Static Files (CSS):**
Scroll to the bottom and **replace** the `STATIC_URL` section with this:

```python
STATIC_URL = 'static/'
# This creates a folder where all CSS files are collected for the server
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# This tells WhiteNoise to compress files for speed
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**E. Update Allowed Hosts:**
Change this line to allow Render to serve your site.
```python
ALLOWED_HOSTS = ['*'] 
```

---

### **Phase 4: Push to GitHub**

Save all files (`Ctrl+S`). Now send these changes to GitHub so Render can download them.

```bash
git add .
git commit -m "Configure settings for Render deployment"
git push origin main