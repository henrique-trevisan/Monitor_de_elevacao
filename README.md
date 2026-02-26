# Temperature Monitor

Temperature Monitor is a desktop application for automating temperature-rise tests of mini circuit breakers. It collects and processes temperature measurements, detects when temperature stabilizes, and helps operators record and export results.

## Key Features

- Real-time temperature plotting and monitoring
- Automatic detection of temperature stabilization events
- CSV import/export and data cleaning pipeline
- System tray integration for lightweight background operation
- Threaded worker for long-running processing without blocking the GUI

## Requirements

- Python 3.10 or newer
- Recommended: create and use a virtual environment

## Installation

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Install the package in editable mode for development:

```bash
pip install -e .
```

## Running the App

Run the installed CLI entry (after `pip install -e .`):

```bash
temperature-monitor
```

Or run directly from source:

```bash
python -m monitor_de_elevacao.app
```

On Windows you can also run the tray app entry point at `monitor_tray.app` when relevant.

## Configuration & Persistence

User configuration (GUI snapshot) is saved as a JSON file in the user's Documents folder by the persistence layer. The adapter in `monitor_de_elevacao/infra/persistence_file.py` locates a suitable folder and stores `config.json` there. The saved snapshot is the source of truth for the GUI state.

## Project Structure

```text
monitor_de_elevacao/
|-- app.py                # Main entry point
|-- core/                 # Pure business logic (calculations, cleaning, rules, pipeline)
|-- infra/                # Persistence, adapters, file handling, worker
|-- ui/                   # GUI screens, widgets and tray integration
`-- assets/               # Static assets (icons, images)
```

## Development & Tests

Recommended workflow:

1. Create a virtual environment: `python -m venv venv` and activate it.
2. Install the editable package and dependencies.
3. Run unit tests with `pytest` (tests live in the `tests/` folder).

The codebase follows a layered architecture: UI (screens and widgets) exports/imports snapshots, `infra` adapts snapshots to worker payloads and handles persistence, and `core` contains pure functions for calculations and rules.

## Contributing

Contributions are welcome. Please open issues for bugs or feature requests, and submit pull requests with focused changes and tests for new logic.

## Author

Henrique Trevisan (<trehen30@gmail.com>)

## License

Commercial use of this project is allowed only if the user contributes code back to this project.

This is a custom usage condition described in this README (not a standard open-source license).
