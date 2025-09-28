
#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

ICON_SRC="$PROJECT_DIR/icon.png"
ICON_DEST="$HOME/.local/share/icons/django-signals-ui.png"
DESKTOP_SRC="$PROJECT_DIR/django-signals-ui.desktop"
DESKTOP_DEST="$HOME/.local/share/applications/django-signals-ui.desktop"
LAUNCHER_PATH="$PROJECT_DIR/launcher.sh"

echo "Setting up Python virtual environment..."
python3 -m venv "$PROJECT_DIR/.venv"
source "$PROJECT_DIR/.venv/bin/activate"
pip install -r "$PROJECT_DIR/requirements.txt"

echo "Copying icon..."
cp "$ICON_SRC" "$ICON_DEST"

# Patch the .desktop file to use the absolute path to the launcher
sed "s|^Exec=.*|Exec=$LAUNCHER_PATH|" "$DESKTOP_SRC" > "$DESKTOP_DEST"
update-desktop-database "$HOME/.local/share/applications/"

echo "Making launcher executable..."
chmod +x "$PROJECT_DIR/launcher.sh"

echo "Installation completed! You can now find Django Signals UI in your application menu."
