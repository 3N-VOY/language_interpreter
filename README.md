# Sigil Programming Language

## About Sigil🔮

Sigil is a name inspired by the mystical symbols used in magic🪄. In those contexts, a *sigil* is a unique symbol believed to hold magical power, often created to represent a specific intent or concept. Just like a magical sigil channels power through a symbol, the Sigil language channels computational power through code.✨

## Overview

This project implements a custom programming language interpreter named Sigil that supports:

- Basic arithmetic operations (addition, subtraction, multiplication, division)
- Boolean logic (comparisons, equality, logical operations)
- Text values (string literals, concatenation, comparison)
- Global variables (assignment, reading, printing)
- Control flow (if-else statements, while loops, user input)
- List data structure (creation, access, modification, append, length, concatenation)

## Requirements & Running

- Python 3.9+ installed on your system

### Running in Interactive Mode

To start interactive mode run:
```bash
python sigil.py
```
Example usage in interactive mode:

x = 10
y = 20
print x + y
30.0
myList = [1, 2, 3]
myList.append(4)
print myList
[1.0, 2.0, 3.0, 4.0]
name = "Alice"
print "Hello, " + name
Hello, Alice


Type `quit` or `exit` to close the program.

### Running from a File

You can also write programs in a text file and execute them:

python sigil.py my_program.txt


## Language Features

### 1. Arithmetic Operations
- Addition, subtraction, multiplication, division
- Parentheses for grouping
- Unary negation

Example: `(10 * 2) / 6`

### 2. Boolean Logic
- Boolean values (`true`, `false`)
- Comparison operators (`<`, `>`, `<=`, `>=`)
- Equality operators (`==`, `!=`)
- Logical operators (`and`, `or`)
- Boolean negation (`!`)

Example: `(5 < 10) or false`

### 3. Text Values
- String literals with double quotes: `"Hello, world!"`
- String concatenation with `+`
- String comparison with `==` and `!=`
- Escape sequences (`\n`, `\t`, `\"`, `\\`)

Example: `"Hello, " + "world!"`

### 4. Global Variables
- Variable assignment: `x = 10`
- Variable reading: `x + 5`
- Printing values: `print x`

### 5. Control Flow
- If-else statements:
if (condition) {
// statements
} else {
// statements
}

- While loops:
while (condition) {
// statements
}

- User input: `input("Prompt message")`

### 6. List Data Structure
- List creation: `myList = [1, 2, 3]`
- List access: `myList[0]`
- List modification: `myList[1] = 10`
- List append: `myList.append(4)`
- List length: `len(myList)`
- List concatenation: `list1 + list2`

## Error Handling

The interpreter provides detailed error messages for:
- Syntax errors
- Type errors
- Undefined variables
- Index out of range errors
- Division by zero

## Implementation Details

The interpreter follows a standard pipeline:
1. **Tokenization**: Converts source code into tokens
2. **Parsing**: Builds an Abstract Syntax Tree (AST)
3. **Interpretation**: Executes the AST

Comments are supported using the `#` character.
