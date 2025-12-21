# match-expression

A Python implementation of TypeScript's [ts-pattern](https://github.com/gvergnaud/ts-pattern), bringing powerful, type-safe pattern matching to Python with an expressive, chainable API.

## Features

- **Chainable API**: Intuitive `match(value).case(pattern, then).exhaustive()` syntax
- **Type-safe**: Full type inference support with pyright/mypy
- **Exhaustiveness checking**: Ensures all cases are handled at compile time
- **Tuple patterns**: Match against compound patterns like `(Dog, Car)` or `("success", 200)`
- **Zero dependencies**: Lightweight and fast
- **Pythonic**: Leverages Python 3.12+ type system features

## Installation

```bash
pip install match_expression
```

## Quick Start

```python
from typing import Literal
from match_expression import match

# Literal type matching
def process_status(status: Literal["pending", "success", "error"]) -> int:
    return (
        match(status)
        .case("pending", 0)
        .case("success", 1)
        .case("error", -1)
        .exhaustive()
    )

# Type matching with classes
class Dog:
    def bark(self) -> str:
        return "Woof!"

class Cat:
    def meow(self) -> str:
        return "Meow!"

def handle_animal(animal: Dog | Cat) -> str:
    return (
        match(animal)
        .case(Dog, lambda d: d.bark())
        .case(Cat, lambda c: c.meow())
        .exhaustive()
    )
```

## Examples

### Literal Type Matching

```python
from typing import Literal
from match_expression import match

type Platform = Literal["web", "mobile", "desktop"]

def get_app_name(platform: Platform) -> str:
    return (
        match(platform)
        .case("web", "Web Application")
        .case("mobile", "Mobile App")
        .case("desktop", "Desktop Software")
        .exhaustive()
    )

# Type checker knows all cases are covered!
```

### Class Type Matching

```python
from match_expression import match

class Success:
    def __init__(self, value: str):
        self.value = value

class Error:
    def __init__(self, message: str):
        self.message = message

def handle_result(result: Success | Error) -> str:
    return (
        match(result)
        .case(Success, lambda s: f"Success: {s.value}")
        .case(Error, lambda e: f"Error: {e.message}")
        .exhaustive()
    )
```

### Tuple Pattern Matching

Match against tuple values with compound patterns:

```python
from typing import Literal
from match_expression import match

class Dog:
    def speak(self) -> str:
        return "Woof!"

class Cat:
    def speak(self) -> str:
        return "Meow!"

class Car:
    def drive(self) -> str:
        return "Vroom!"

class Bike:
    def ride(self) -> str:
        return "Pedaling!"

def handle_pair(pair: tuple[Dog | Cat, Car | Bike]) -> str:
    return (
        match(pair)
        .case((Dog, Car), lambda d, c: f"{d.speak()} {c.drive()}")
        .case((Dog, Bike), lambda d, b: f"{d.speak()} {b.ride()}")
        .case((Cat, Car), lambda c, car: f"{c.speak()} {car.drive()}")
        .case((Cat, Bike), lambda c, b: f"{c.speak()} {b.ride()}")
        .exhaustive()
    )

# Multi-argument lambdas receive unpacked tuple elements
handle_pair((Dog(), Car()))  # "Woof! Vroom!"
```

You can also mix literals and types in tuple patterns:

```python
type Status = Literal["success", "error"]
type Platform = Literal["web", "mobile"]

def handle_response(response: tuple[Status, Platform]) -> str:
    return (
        match(response)
        .case(("success", "web"), "Web success!")
        .case(("success", "mobile"), "Mobile success!")
        .case(("error", "web"), "Web error!")
        .case(("error", "mobile"), "Mobile error!")
        .exhaustive()
    )
```

### Using `otherwise` for Default Cases

```python
from match_expression import match

def classify_number(n: int) -> str:
    return (
        match(n)
        .case(0, "zero")
        .case(1, "one")
        .case(2, "two")
        .otherwise("many")
    )
```

### Mixed Return Types

The library correctly infers union return types:

```python
from match_expression import match

def process(value: int | str) -> int | str:
    return (
        match(value)
        .case(int, lambda i: i * 2)      # Returns int
        .case(str, lambda s: s.upper())  # Returns str
        .exhaustive()
    )
    # Type is inferred as: int | str
```

### Delayed Evaluation with `eval=False`

You can defer the evaluation of callable functions by using `eval=False`:

```python
from match_expression import match
from typing import Callable

def get_handler(command: str) -> Callable[[], str]:
    return (
        match(command)
        .case("start", lambda: "Starting application...")
        .case("stop", lambda: "Stopping application...")
        .case("restart", lambda: "Restarting application...")
        .exhaustive(eval=False)  # Returns the lambda without calling it
    )

# Get the handler function without executing it
handler = get_handler("start")
# Execute later when needed
result = handler()  # "Starting application..."
```

This is useful when you want to:
- Return handler functions for later execution
- Implement lazy evaluation patterns
- Build command dispatch systems

## API Reference

### `match(value: V) -> Match[V]`
Starts a pattern matching chain.

### `.case(pattern: P, then: R) -> Case[V, P, R]`
Matches against a pattern. If the pattern matches, executes `then`.

- `pattern`: A value to match against (for literals), a type (for isinstance checks), or a tuple of patterns
- `then`: The value to return or a function to execute with the matched value. For tuple patterns, multi-argument lambdas receive unpacked elements.

### `.exhaustive(eval: bool = True) -> R`
Ensures all cases are handled. Raises `ExhaustiveError` if not all cases are covered.

- `eval`: When `True` (default), evaluates callable functions. When `False`, returns the callable without evaluating it.

### `.otherwise(default: R, eval: bool = True) -> R`
Provides a default value for unmatched cases.

- `default`: The value to return or a function to execute when no patterns match
- `eval`: When `True` (default), evaluates callable functions. When `False`, returns the callable without evaluating it.

## Type Checking

The library is designed to work with type checkers like pyright and mypy:

```bash
# Install pyright
pip install pyright

# Type check your code
pyright your_file.py
```

## Contributing

Contributions are welcome! Here's how to get started:

1. Clone the repository
```bash
git clone https://github.com/qodot/match-expression.git
cd match-expression
```

2. Install development dependencies
```bash
uv sync --dev
```

3. Run tests
```bash
uv run pytest
```

4. Type check
```bash
uv run pyright src/ tests/
```

## Requirements

- Python 3.12 or higher
- No external dependencies

## Special Thanks
- [@code-yeongyu](https://github.com/code-yeongyu) and [@indentcorp](https://github.com/indentcorp)
