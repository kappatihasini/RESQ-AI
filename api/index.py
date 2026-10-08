import sys
import os
from urllib.parse import parse_qs, urlencode

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app as base_app


class VercelPathFixMiddleware:
    """
    ASGI middleware ensuring reliable request path resolution
    when deployed as a Vercel Serverless Function.
    Handles x-matched-path, x-forwarded-uri, rewrite query parameters, and prefix routing.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            matched_path = headers.get(b"x-matched-path")
            forwarded_uri = headers.get(b"x-forwarded-uri")

            orig_path = None
            if matched_path:
                orig_path = matched_path.decode("utf-8", errors="ignore")
            elif forwarded_uri:
                orig_path = forwarded_uri.decode("utf-8", errors="ignore").split("?")[0]

            if orig_path and orig_path not in ("/api/index.py", "/api/index", "/index.py"):
                scope["path"] = orig_path
            else:
                qs = scope.get("query_string", b"").decode("utf-8", errors="ignore")
                if "__path__=" in qs:
                    params = parse_qs(qs)
                    p = params.get("__path__", [""])[0]
                    if p:
                        scope["path"] = f"/api/{p}" if not p.startswith("/") else p
                        del params["__path__"]
                        scope["query_string"] = urlencode(params, doseq=True).encode("utf-8")
                else:
                    path = scope.get("path", "")
                    if path.startswith("/api/index.py/"):
                        scope["path"] = path[len("/api/index.py"):]
                    elif path.startswith("/index.py/"):
                        scope["path"] = path[len("/index.py"):]
                    elif path in ("/api/index.py", "/index.py", "/api"):
                        scope["path"] = "/api/health"

        await self.app(scope, receive, send)


app = VercelPathFixMiddleware(base_app)
