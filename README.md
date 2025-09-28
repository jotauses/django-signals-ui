# Django Signals Explorer

A desktop application built with PyQt6 for navigating, searching and filtering Django signals in your project.

---

## Features

- **Automatic Parsing:** Scans your Django codebase to extract signals, senders, receivers and file locations.
- **Interactive Table View:** Searchable and filterable table of all signals.
- **Graph Visualization:** Visual, grouped and organized graph of signals, senders and receivers.
- **Details Panel:** View details for any signal, sender or receiver.
- **Read-Only:** The app does not modify your codebase.

## Requirements
- Python 3.8 or higher
- All dependencies are installed inside the virtual environment using pip:
  - PyQt6
  - graphviz
  - pydot
  - pyparsing

> **Note:** You do not need to install any system packages. All requirements are handled via `pip install -r requirements.txt` inside your virtual environment.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python main.py --project-root /path/to/your/django/project
```

- For best results, point `--project-root` to the root folder containing your Django apps.

## Project Structure

```
main.py                  # Entry point, CLI argument parsing, launches UI
requirements.txt         # Python dependencies
domain/
    models.py            # Signal domain model
infrastructure/
    parser.py            # Signal parser for Django codebase
    graph.py             # DOT/Graphviz generation
ui/
    app.py               # Main PyQt6 application
    widgets/
        graph_scene.py   # Custom QGraphicsScene for graph
        graphics.py      # Zoomable graphics view
        details.py       # Details panel widget
```

## Development

- Modular, maintainable, and professional codebase.
- Clean Code and DDD principles.
- Easily extensible for new features.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
