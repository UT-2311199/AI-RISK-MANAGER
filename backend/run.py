# =============================================================================
# run.py — Application Entry Point Script
# =============================================================================
# Run this file to start the development server: python run.py
#
# It starts uvicorn (the ASGI web server) programmatically.
# Equivalent to running: uvicorn app.main:app --reload --port 8000
#
# WHY uvicorn?
# FastAPI is an ASGI (Asynchronous Server Gateway Interface) framework.
# ASGI apps need a specialized server. Uvicorn is the recommended, 
# high-performance ASGI server for FastAPI in development.
# =============================================================================

import uvicorn
# uvicorn is the web server that runs our FastAPI app.
# It handles HTTP connections, parses requests, and passes them to FastAPI.

if __name__ == "__main__":
    # __name__ == "__main__" → This block only runs when you execute this file
    # DIRECTLY (python run.py). It does NOT run when another file imports it.
    # This is a Python best practice for entry point scripts.

    uvicorn.run(
        "app.main:app",
        # "app.main:app" → Python module path + variable name.
        # "app.main" = the file app/main.py (Python module notation uses dots)
        # ":app"     = the FastAPI instance variable named 'app' inside that file.

        host="0.0.0.0",
        # host="0.0.0.0" → Listen on ALL network interfaces.
        # 0.0.0.0 means: accept connections from anywhere (localhost, LAN, etc.)
        # Use "127.0.0.1" to only accept connections from the same machine.

        port=8000,
        # Port 8000 is the FastAPI/uvicorn convention.
        # Access your API at: http://localhost:8000

        reload=True,
        # reload=True → HOT RELOAD mode.
        # Uvicorn watches your Python files for changes.
        # When you edit and save a file, the server AUTOMATICALLY restarts.
        # This is ONLY for development — disable in production (it's slow).

        log_level="info"
        # log_level="info" → Show informational messages in the terminal.
        # You'll see: "GET /projects 200 OK" for every request.
        # Other levels: "debug" (very verbose), "warning", "error"
    )
