
# GUIDE FOR DEVELOPING AGENTS IN THE TEMPERATURE MONITOR PROJECT

This document summarises the architectural principles and development practices used in the Temperature Monitor project. It is intended to guide the creation of new code, explain how to separate the project into layers and modules, organise files and folders, and document the expected coding style. All code, comments, variable names and user‑visible strings should be written in English.

## 1. OVERVIEW AND PHILOSOPHY

The project follows a layered design and emphasises simplicity and testability. The initial plan for the GUI was to apply **layered programming** concepts, split the code into **small files** and **small functions**, and adhere to best programming practices.

At the user‑interface level the screen state is captured as a **snapshot**: a plain Python dictionary describing all user inputs. This snapshot is converted into a **payload** in the format expected by the worker through pure functions in `infra/config_adapter.py`. Persistence to disk uses the snapshot (not the payload). The persistence flow is: GUI → snapshot → payload → save to disk → load snapshot from disk → apply snapshot to GUI.

## 2. PROJECT FOLDER STRUCTURE

The `monitor_de_elevacao` package is organised into:

- `core/` : core logic (calculations, cleaning, rules, pipeline).
- `infra/` : infrastructure (global state, persistence, data format adapters, worker communication).
- `ui/` : user interface (screens, components, tray icon).
- `assets/` : static assets such as images.
- `tests/` : unit tests for pure functions and adapters.

When adding files, keep this division: business logic goes into `core/`, persistence and data transformation into `infra/`, and visual components into `ui/`. Static resources belong in `assets/`.

## 3. LAYER SEPARATION

### **User interface layer**

- Each part of the interface should be encapsulated in its own class and file. For example, `ConfigScreen`, `DeviceConfigTable` and `LimitCard` each reside in separate files under `ui/`. This improves reusability and clarity.
- Components must expose methods to export and import their state. `DeviceConfigTable` implements `get_channels()` to export its channels and `set_channels()` to fill entries. `LimitCard` defines `to_dict()` and `set_values()`. `ConfigScreen.get_config_snapshot()` collects data from all widgets and returns a plain dictionary, while `apply_snapshot()` applies a saved snapshot back to the GUI.
- Build the user interface incrementally. Create a `build_widgets()` method that sets up the layout and documents each section with docstrings and comments. The example in `ConfigScreen.build_widgets()` shows how to separate the interface into rows with clear comments.
- When the number of devices or poles changes, the tables are rebuilt dynamically in `rebuild_device_tables()`. This method destroys old tables, reads the current combobox values and creates new `DeviceConfigTable` instances.
- Event handlers such as `on_change_num_devices` and `on_change_num_poles` should update the state and rebuild UI components accordingly.
- The `App` class stores screen instances in a dictionary and raises the desired frame to the front using `show_frame()`. Starting the monitoring process involves reading the snapshot, validating it, saving it to disk and switching to the monitoring screen.

### **Infrastructure layer**

- Global state is stored in `infra/data.py` as variables and queues for communication. Use this module only for shared state; pure functions must not modify it.
- The `infra/config_adapter.py` module implements the class `ConfigAdapter` with the method `snapshot_to_worker_payload()`, converting the GUI snapshot into the worker payload. This function is **pure** and free of side effects. It handles the number of devices and poles, separates terminal and body channels, and constructs the `ambient`, `circuit_breakers` and `limiters` sections.
- Persistence is handled in a separate file such as `infra/persistence.py` or `persistence_file.py`. The implementation finds the user’s documents folder regardless of system language and stores a JSON file named `config.json`. The `PersistenceFile` class encapsulates the logic of locating directories, saving snapshots and loading them. Always store the snapshot rather than the payload.
- To submit validation jobs or other tasks to the worker thread, `ConfigAdapter.ask_queue_to_validate()` updates `data.user_input_variables` and pushes the message to the queue. Use similar patterns when adding new asynchronous operations.

### **Core layer**

- Calculations, data cleaning and business rules belong to `core/`. Functions in this layer should be pure and should return new data rather than mutate inputs. `core/pipeline.py` orchestrates calls to other functions. For new logic, implement functions in this folder and create adapters in `infra/` if required.
- Keep the user interface free of computation. The worker should handle reading CSV files, condensing lines and calculating deltas; the GUI only displays the payload. Follow the same separation when adding new business logic.

## 4. CODING STYLE AND NAMING

- **Language:** All identifiers (variables, functions, classes), docstrings, comments and visible text must be in English. Use descriptive names; avoid abbreviations unless they are well known.
- **Naming conventions:** Use `snake_case` for variables and functions and `PascalCase` for classes. For example, `get_config_snapshot`, `apply_snapshot` and `PersistenceFile`.
- **Type hints:** Annotate parameters and return types using Python type hints (e.g., `list[int]`, `Dict[str, Any]`) to improve readability and catch errors earlier.
- **Docstrings:** Begin each class or function with a docstring explaining its purpose. In longer methods, list the main steps. The `ConfigAdapter` docstring notes that the class converts the snapshot to a payload and pushes tasks to the queue. If there are classes or functions with no docstrings, create for them.
- **Section comments:** Use comments to separate logical sections of code. The `ConfigScreen` implementation uses line separators to group the upper bar, file selection, comboboxes, tables and limit cards.
- **Short, cohesive functions:** Each method should perform a single task. The `rebuild_device_tables()` function destroys old tables, reads the number of devices and poles, creates the new tables and updates the list. Keeping functions cohesive makes them easier to test.
- **Controlled side effects:** Functions that modify global state (saving files, changing values in `data.py`) should be isolated and clearly documented. Transformation functions (such as those in `infra/config_adapter.py`) must not alter global state.
- **Paths and files:** Use Python’s `pathlib` for file paths. Avoid concatenating path strings manually.
- **Threading and queues:** Use the `threading` module to run background tasks (like the tray icon) and `queue.Queue` for thread communication. Never block the GUI thread with long operations; instead, push work to a background worker.

## 5. INCREMENTAL DEVELOPMENT AND TESTING

Development should proceed in small steps. Implement a pure function, write a test, and then move to the next piece. For example, after implementing `snapshot_to_worker_payload`, create a simple test in `tests/test_config_adapter.py` that constructs a manual snapshot, calls the function and asserts the result. Subsequent layers such as persistence or configuration migration can then be added in separate modules.

Write unit tests for pure functions in `core/` and `infra/`. Cover normal cases and edge cases (e.g., invalid numbers of poles or empty strings). Avoid testing UI elements directly; instead test their export methods (`get_channels`, `get_config_snapshot`) that return data structures.

## 6. CONCLUSION

To contribute effectively to this project, adhere to the layered architecture (UI, Infra, Core), keep each module’s responsibilities clear, write pure and testable functions, and document your code thoroughly. Ensuring that code and comments are in English promotes consistency and ease of collaboration. Following these guidelines will simplify the future expansion of the monitor, whether adding new devices, implementing new calculations or extending the user interface.
