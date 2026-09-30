import os
from django.conf import settings
from django.http import HttpResponseNotFound
from django.views.static import serve as static_serve

PUBLIC_DIR = settings.BASE_DIR / 'public'


def frontend(request, path=''):
    """
    Mirrors this part of the original server.js:

        app.use(express.static(path.join(__dirname, 'public')));
        app.get('*', (req, res, next) => {
          if (req.path.startsWith('/api')) return next();
          res.sendFile(path.join(__dirname, 'public', 'index.html'));
        });

    Serve the exact file if it exists under public/, otherwise fall back to index.html.
    """
    clean_path = path.lstrip('/')
    candidate = PUBLIC_DIR / clean_path if clean_path else PUBLIC_DIR / 'index.html'

    if clean_path and os.path.isfile(candidate):
        return static_serve(request, clean_path, document_root=str(PUBLIC_DIR))

    index_path = PUBLIC_DIR / 'index.html'
    if os.path.isfile(index_path):
        return static_serve(request, 'index.html', document_root=str(PUBLIC_DIR))

    return HttpResponseNotFound('index.html not found in public/')
