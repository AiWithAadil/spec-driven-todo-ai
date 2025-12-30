# Python CLI Todo Application

A lightweight, single-file Python CLI application for managing tasks with persistent JSON storage.

## Features

- **Add tasks**: Create new tasks with descriptions
- **View tasks**: Display all tasks with completion status
- **Mark complete**: Track task progress
- **Update tasks**: Modify task descriptions
- **Delete tasks**: Remove unwanted tasks

## Installation

```bash
# Ensure Python 3.8+ is installed
python3 --version

# No external dependencies required - uses Python standard library only
```

## Usage

```bash
# Add a new task
python -m src.todo_app add "Buy groceries"

# View all tasks
python -m src.todo_app list

# Mark task as complete
python -m src.todo_app complete 1

# Update a task description
python -m src.todo_app update 1 "Buy organic groceries"

# Delete a task
python -m src.todo_app delete 1

# Get help
python -m src.todo_app help
```

## Data Storage

Tasks are automatically saved to: `~/.todo/tasks.json` (Unix/macOS) or `%USERPROFILE%\.todo\tasks.json` (Windows)

## Development

### Running Tests

```bash
# Install pytest for testing
pip install pytest

# Run all tests
pytest tests/

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
```

### Project Structure

```
src/
├── __init__.py
├── todo_app.py       # Entry point and CLI dispatcher
├── models.py         # Task and TaskList models
├── storage.py        # File persistence layer
├── commands.py       # Command implementations
├── formatter.py      # Output formatting
└── errors.py         # Custom exceptions

tests/
├── unit/             # Unit tests
├── integration/      # Integration tests
└── fixtures/         # Test data
```

## Architecture

- **Models**: Task entity with validation and state management
- **Storage**: JSON-based persistence with atomic writes
- **Commands**: Modular command implementations
- **Formatter**: Clean output formatting with status indicators
- **Errors**: Custom exception hierarchy for clear error handling

## Requirements

- Python 3.8 or later
- pytest (for testing)
- No external dependencies for runtime

## License

MIT
