# Temperature Monitor

Temperature Monitor is an application designed to monitor the temperature rise test for mini circuit breakers. It indicates when the temperature has stabilized, helping users efficiently track and record test results.

## Features
- Real-time temperature monitoring
- Automatic detection of temperature stabilization
- User-friendly graphical interface (GUI)
- System tray integration for easy access
- Data cleaning and processing pipeline
- CSV data handling

## Installation

### Requirements
- Python 3.10 or higher
- pip

### Install dependencies
```bash
pip install -r requirements.txt
```

### Install as a package (editable mode)
```bash
pip install -e .
```

## Usage

After installation, you can run the application using the command:

```bash
temperature-monitor
```

Alternatively, you can run directly from the source:

```bash
python -m monitor_de_elevacao.app
```

## Project Structure

```
monitor_de_elevacao/
├── app.py                # Main entry point
├── core/                 # Core logic (calculations, cleaning, rules, tables, pipeline)
├── infra/                # Infrastructure (data handling, file operations, worker)
├── ui/                   # User interface (GUI, tray icon)
└── assets/               # Static assets (images, etc.)
```

## Development

To contribute or modify the project, clone the repository and install dependencies as described above. All main logic is organized under the `monitor_de_elevacao` package.

## Author

Henrique Trevisan (<trehen30@gmail.com>)

## License

To be defined.
