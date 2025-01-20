def tokenize(code):
    #Convert source code into a list of tokens.
    tokens = []
    i = 0
    line_num = 1

    # Keywords and operators to check
    keywords = {
        'true': {'type': 'boolean', 'value': True},
        'false': {'type': 'boolean', 'value': False},
        'and': {'type': 'operator', 'value': 'and'},
        'or': {'type': 'operator', 'value': 'or'},
        'print': {'type': 'keyword', 'value': 'print'},
        'if': {'type': 'keyword', 'value': 'if'},
        'else': {'type': 'keyword', 'value': 'else'},
        'while': {'type': 'keyword', 'value': 'while'},
        'input': {'type': 'keyword', 'value': 'input'},
        'append': {'type': 'keyword', 'value': 'append'},
        'len': {'type': 'keyword', 'value': 'len'}
    }

    # Two-character operators
    two_char_ops = {
        '==': {'type': 'operator', 'value': '=='},
        '!=': {'type': 'operator', 'value': '!='},
        '<=': {'type': 'operator', 'value': '<='},
        '>=': {'type': 'operator', 'value': '>='}
    }

    # Single-character operators and punctuation
    single_char_ops = {
        '+': {'type': 'operator', 'value': '+'},
        '-': {'type': 'operator', 'value': '-'},
        '*': {'type': 'operator', 'value': '*'},
        '/': {'type': 'operator', 'value': '/'},
        '=': {'type': 'operator', 'value': '='},
        '<': {'type': 'operator', 'value': '<'},
        '>': {'type': 'operator', 'value': '>'},
        '!': {'type': 'operator', 'value': '!'},
        '(': {'type': 'punctuation', 'value': '('},
        ')': {'type': 'punctuation', 'value': ')'},
        '{': {'type': 'punctuation', 'value': '{'},
        '}': {'type': 'punctuation', 'value': '}'},
        '[': {'type': 'punctuation', 'value': '['},
        ']': {'type': 'punctuation', 'value': ']'},
        ',': {'type': 'punctuation', 'value': ','},
        '.': {'type': 'punctuation', 'value': '.'}
    }

    while i < len(code):
        char = code[i]

        # Track line numbers
        if char == '\n':
            line_num += 1
            i += 1
            continue

        # Skip whitespace
        if char.isspace():
            i += 1
            continue

        # Skip comments
        if char == '#':
            while i < len(code) and code[i] != '\n':
                i += 1
            continue

        # Handle string literals
        if char == '"':
            string_value = ""
            i += 1  # Skip opening quote

            while i < len(code) and code[i] != '"':
                # Handle escape sequences
                if code[i] == '\\' and i + 1 < len(code):
                    i += 1
                    if code[i] == 'n':
                        string_value += '\n'
                    elif code[i] == 't':
                        string_value += '\t'
                    elif code[i] == '"':
                        string_value += '"'
                    elif code[i] == '\\':
                        string_value += '\\'
                    else:
                        string_value += '\\' + code[i]
                else:
                    string_value += code[i]

                # Track line numbers in strings
                if code[i] == '\n':
                    line_num += 1
                i += 1

            if i >= len(code):
                raise ValueError(f"Line {line_num}: Unterminated string literal")

            i += 1  # Skip closing quote
            tokens.append({'type': 'string', 'value': string_value, 'line': line_num})
            continue

        # Handle numbers (including decimals) - improved handling
        if char.isdigit() or (char == '.' and i + 1 < len(code) and code[i+1].isdigit()):
            num_str = char
            i += 1
            # Allow only one decimal point
            has_decimal = char == '.'

            while i < len(code) and (code[i].isdigit() or (code[i] == '.' and not has_decimal)):
                if code[i] == '.':
                    has_decimal = True
                num_str += code[i]
                i += 1

            tokens.append({'type': 'number', 'value': float(num_str), 'line': line_num})
            continue

        # Check for two-character operators
        if i + 1 < len(code):
            two_chars = code[i:i+2]
            if two_chars in two_char_ops:
                token = two_char_ops[two_chars].copy()
                token['line'] = line_num
                tokens.append(token)
                i += 2
                continue

        # Check for identifiers and keywords
        if char.isalpha() or char == '_':
            identifier = char
            i += 1
            while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                identifier += code[i]
                i += 1

            # Check if it's a keyword
            if identifier in keywords:
                token = keywords[identifier].copy()
                token['line'] = line_num
                tokens.append(token)
            else:
                tokens.append({'type': 'identifier', 'value': identifier, 'line': line_num})
            continue

        # Handle single-character operators and punctuation
        if char in single_char_ops:
            token = single_char_ops[char].copy()
            token['line'] = line_num
            tokens.append(token)
            i += 1
            continue

        # Unrecognized character
        raise ValueError(f"Line {line_num}: Unrecognized character: {char}")

    return tokens

def parse(tokens):
    #Parse tokens into an abstract syntax tree.
    i = [0]  # Current token index (as a mutable list)

    def peek():
        #Look at the current token without consuming it.
        if i[0] >= len(tokens):
            return None
        return tokens[i[0]]

    def advance():
        #Consume the current token and return it.
        token = peek()
        i[0] += 1
        return token

    def check(type, value=None):
        #Check if the current token matches the given type and value.
        token = peek()
        if token is None:
            return False
        if token['type'] != type:
            return False
        if value is not None and token['value'] != value:
            return False
        return True

    def match(type, value=None):
        #Consume the current token if it matches the given type and value.
        if check(type, value):
            return advance()
        return None

    def expect(type, value=None, message=None):
        #Expect the current token to match the given type and value.
        token = match(type, value)
        if token is None:
            current = peek()
            line = current['line'] if current else "end of file"
            if message is None:
                if value is not None:
                    message = f"Expected {type} '{value}'"
                else:
                    message = f"Expected {type}"
            raise ValueError(f"Line {line}: {message}, got {current}")
        return token

    def parse_program():
        #Parse a complete program.
        statements = []
        while peek() is not None:
            statements.append(parse_statement())
        return {'type': 'program', 'body': statements}

    def parse_statement():
        #Parse a statement.
        # Print statement
        if match('keyword', 'print'):
            expr = parse_expression()
            return {'type': 'print', 'expression': expr}

        # If statement
        if match('keyword', 'if'):
            return parse_if_statement()

        # While statement
        if match('keyword', 'while'):
            return parse_while_statement()

        # Variable assignment
        if check('identifier'):
            name = advance()['value']

            # Check for list indexing in assignment: list[index] = value
            if match('punctuation', '['):
                index = parse_expression()
                expect('punctuation', ']', "Expected ']' after index")

                if match('operator', '='):
                    value = parse_expression()
                    return {'type': 'list_set', 'list': name, 'index': index, 'value': value}
                else:
                    # Rewind for normal expression
                    i[0] -= 3  # Go back to before '['

            if match('operator', '='):
                value = parse_expression()
                return {'type': 'assignment', 'name': name, 'value': value}

            # Append method: list.append(value)
            if match('punctuation', '.'):
                if match('keyword', 'append'):
                    expect('punctuation', '(', "Expected '(' after append")
                    value = parse_expression()
                    expect('punctuation', ')', "Expected ')' after append argument")
                    return {'type': 'list_append', 'list': name, 'value': value}
                else:
                    i[0] -= 2  # Rewind if not a method call

            # Rewind if not an assignment or method call
            i[0] -= 1

        # Expression statement
        expr = parse_expression()
        return {'type': 'expression', 'expression': expr}

    def parse_block():
        #Parse a block of statements.
        statements = []

        # Check for opening brace
        expect('punctuation', '{', "Expected '{' to start block")

        # Parse statements until closing brace
        while not match('punctuation', '}'):
            if peek() is None:
                raise ValueError("Unexpected end of file, missing '}'")
            statements.append(parse_statement())

        return statements

    def parse_if_statement():
        #Parse an if statement.
        # Parse condition
        expect('punctuation', '(', "Expected '(' after 'if'")
        condition = parse_expression()
        expect('punctuation', ')', "Expected ')' after condition")

        # Parse if body
        if_body = parse_block()

        # Check for else clause
        else_body = []
        if match('keyword', 'else'):
            else_body = parse_block()

        return {
            'type': 'if',
            'condition': condition,
            'if_body': if_body,
            'else_body': else_body
        }

    def parse_while_statement():
        #Parse a while loop.
        # Parse condition
        expect('punctuation', '(', "Expected '(' after 'while'")
        condition = parse_expression()
        expect('punctuation', ')', "Expected ')' after condition")

        # Parse body
        body = parse_block()

        return {
            'type': 'while',
            'condition': condition,
            'body': body
        }

    def parse_expression():
        #Parse an expression.
        return parse_logical_or()

    def parse_logical_or():
        #Parse a logical OR expression.
        expr = parse_logical_and()

        while match('operator', 'or'):
            right = parse_logical_and()
            expr = {
                'type': 'binary',
                'op': 'or',
                'left': expr,
                'right': right
            }

        return expr

    def parse_logical_and():
        #Parse a logical AND expression.
        expr = parse_equality()

        while match('operator', 'and'):
            right = parse_equality()
            expr = {
                'type': 'binary',
                'op': 'and',
                'left': expr,
                'right': right
            }

        return expr

    def parse_equality():
        #Parse an equality expression.
        expr = parse_comparison()

        while True:
            if match('operator', '=='):
                right = parse_comparison()
                expr = {
                    'type': 'binary',
                    'op': '==',
                    'left': expr,
                    'right': right
                }
            elif match('operator', '!='):
                right = parse_comparison()
                expr = {
                    'type': 'binary',
                    'op': '!=',
                    'left': expr,
                    'right': right
                }
            else:
                break

        return expr

    def parse_comparison():
        #Parse a comparison expression.
        expr = parse_addition()

        while True:
            if match('operator', '<'):
                right = parse_addition()
                expr = {
                    'type': 'binary',
                    'op': '<',
                    'left': expr,
                    'right': right
                }
            elif match('operator', '>'):
                right = parse_addition()
                expr = {
                    'type': 'binary',
                    'op': '>',
                    'left': expr,
                    'right': right
                }
            elif match('operator', '<='):
                right = parse_addition()
                expr = {
                    'type': 'binary',
                    'op': '<=',
                    'left': expr,
                    'right': right
                }
            elif match('operator', '>='):
                right = parse_addition()
                expr = {
                    'type': 'binary',
                    'op': '>=',
                    'left': expr,
                    'right': right
                }
            else:
                break

        return expr

    def parse_addition():
        #Parse an addition expression.
        expr = parse_multiplication()

        while True:
            if match('operator', '+'):
                right = parse_multiplication()
                expr = {
                    'type': 'binary',
                    'op': '+',
                    'left': expr,
                    'right': right
                }
            elif match('operator', '-'):
                right = parse_multiplication()
                expr = {
                    'type': 'binary',
                    'op': '-',
                    'left': expr,
                    'right': right
                }
            else:
                break

        return expr

    def parse_multiplication():
        #Parse a multiplication expression.
        expr = parse_unary()

        while True:
            if match('operator', '*'):
                right = parse_unary()
                expr = {
                    'type': 'binary',
                    'op': '*',
                    'left': expr,
                    'right': right
                }
            elif match('operator', '/'):
                right = parse_unary()
                expr = {
                    'type': 'binary',
                    'op': '/',
                    'left': expr,
                    'right': right
                }
            else:
                break

        return expr

    def parse_unary():
        #Parse a unary expression.
        if match('operator', '-'):
            expr = parse_unary()
            return {
                'type': 'unary',
                'op': '-',
                'expr': expr
            }
        elif match('operator', '!'):
            expr = parse_unary()
            return {
                'type': 'unary',
                'op': '!',
                'expr': expr
            }
        return parse_call_or_access()

    def parse_call_or_access():
        #Parse function calls or list access.
        expr = parse_primary()

        while True:
            # Parse list indexing: list[index]
            if match('punctuation', '['):
                index = parse_expression()
                expect('punctuation', ']', "Expected ']' after index")
                expr = {
                    'type': 'list_access',
                    'list': expr,
                    'index': index
                }
            # Parse function calls like len(list)
            elif check('keyword', 'len') and peek()['value'] == 'len':
                advance()  # Consume 'len'
                expect('punctuation', '(', "Expected '(' after len")
                arg = parse_expression()
                expect('punctuation', ')', "Expected ')' after len argument")
                expr = {
                    'type': 'len',
                    'argument': arg
                }
            else:
                break

        return expr

    def parse_primary():
        #Parse a primary expression.
        # List literal: [1, 2, 3]
        if match('punctuation', '['):
            elements = []

            # Empty list
            if match('punctuation', ']'):
                return {'type': 'list_literal', 'elements': elements}

            # List with elements
            elements.append(parse_expression())

            while match('punctuation', ','):
                elements.append(parse_expression())

            expect('punctuation', ']', "Expected ']' to close list literal")

            return {'type': 'list_literal', 'elements': elements}

        # Literals
        if check('number'):
            return {'type': 'number', 'value': advance()['value']}

        if check('boolean'):
            return {'type': 'boolean', 'value': advance()['value']}

        if check('string'):
            return {'type': 'string', 'value': advance()['value']}

        # Variable
        if check('identifier'):
            return {'type': 'variable', 'name': advance()['value']}

        # Input function
        if match('keyword', 'input'):
            expect('punctuation', '(', "Expected '(' after 'input'")
            prompt = None
            if not check('punctuation', ')'):
                prompt = parse_expression()
            expect('punctuation', ')', "Expected ')' after input parameters")
            return {'type': 'input', 'prompt': prompt}

        # Length function
        if match('keyword', 'len'):
            expect('punctuation', '(', "Expected '(' after 'len'")
            arg = parse_expression()
            expect('punctuation', ')', "Expected ')' after len argument")
            return {'type': 'len', 'argument': arg}

        # Grouping
        if match('punctuation', '('):
            expr = parse_expression()
            expect('punctuation', ')', "Expected ')'")
            return expr

        # Error
        token = peek()
        if token:
            raise ValueError(f"Line {token['line']}: Unexpected token: {token}")
        else:
            raise ValueError("Unexpected end of file")

    # Start parsing from the program level
    return parse_program()

def interpret(ast, environment=None):
    #Interpret an abstract syntax tree.
    if environment is None:
        environment = {'variables': {}, 'output': []}

    def evaluate(node):
        #Evaluate an expression node.
        if node['type'] == 'number':
            return node['value']

        if node['type'] == 'boolean':
            return node['value']

        if node['type'] == 'string':
            return node['value']

        if node['type'] == 'list_literal':
            elements = [evaluate(elem) for elem in node['elements']]
            return elements

        if node['type'] == 'list_access':
            lst = evaluate(node['list'])
            index = evaluate(node['index'])

            if not isinstance(lst, list):
                raise TypeError("Cannot index a non-list value")

            if not isinstance(index, float) or int(index) != index:
                raise TypeError("List index must be an integer")

            index = int(index)
            if index < 0 or index >= len(lst):
                raise IndexError("List index out of range")

            return lst[index]

        if node['type'] == 'len':
            value = evaluate(node['argument'])

            if not isinstance(value, list) and not isinstance(value, str):
                raise TypeError("len() only works on lists and strings")

            return float(len(value))

        if node['type'] == 'variable':
            name = node['name']
            if name not in environment['variables']:
                raise ValueError(f"Undefined variable: {name}")
            return environment['variables'][name]

        if node['type'] == 'input':
            prompt = ""
            if node['prompt']:
                prompt = str(evaluate(node['prompt']))
            return input(prompt)

        if node['type'] == 'unary':
            expr_value = evaluate(node['expr'])

            if node['op'] == '-':
                if isinstance(expr_value, bool) or isinstance(expr_value, str) or isinstance(expr_value, list):
                    raise TypeError("Cannot apply unary '-' to a boolean, string, or list value")
                return -expr_value

            if node['op'] == '!':
                if isinstance(expr_value, float) or isinstance(expr_value, str) or isinstance(expr_value, list):
                    raise TypeError("Cannot apply unary '!' to a numeric, string, or list value")
                return not expr_value

        if node['type'] == 'binary':
            left = evaluate(node['left'])
            right = evaluate(node['right'])
            op = node['op']
            
            
            


            # Arithmetic operations
            if op == '+':
                # String concatenation
                if isinstance(left, str):
                    if isinstance(right, list):
                        # Convert list to a readable string format
                        formatted_list = "[" + ", ".join(str(item) for item in right) + "]"
                        return left + formatted_list
                    return left + str(right)
                if isinstance(right, str):
                    if isinstance(left, list):
                        # Convert list to a readable string format
                        formatted_list = "[" + ", ".join(str(item) for item in left) + "]"
                        return formatted_list + right
                    return str(left) + right
                # List concatenation
                if isinstance(left, list) and isinstance(right, list):
                    return left + right
                # Regular addition for numbers
                if isinstance(left, bool) or isinstance(right, bool) or isinstance(left, list) or isinstance(right, list):
                    raise TypeError("Cannot add boolean or mix list with non-list values")
                return left + right

            if op == '-':
                if isinstance(left, bool) or isinstance(right, bool) or isinstance(left, str) or isinstance(right, str) or isinstance(left, list) or isinstance(right, list):
                    raise TypeError("Cannot subtract boolean, string, or list values")
                return left - right

            if op == '*':
                if isinstance(left, bool) or isinstance(right, bool) or isinstance(left, str) or isinstance(right, str) or isinstance(left, list) or isinstance(right, list):
                    raise TypeError("Cannot multiply boolean, string, or list values")
                return left * right

            if op == '/':
                if isinstance(left, bool) or isinstance(right, bool) or isinstance(left, str) or isinstance(right, str) or isinstance(left, list) or isinstance(right, list):
                    raise TypeError("Cannot divide boolean, string, or list values")
                return left / right

            # Comparison operations
            if op == '<':
                if isinstance(left, bool) or isinstance(right, bool) or isinstance(left, str) or isinstance(right, str) or isinstance(left, list) or isinstance(right, list):
                    raise TypeError("Cannot compare boolean, string, or list values with '<'")
                return left < right

            if op == '>':
                if isinstance(left, bool) or isinstance(right, bool) or isinstance(left, str) or isinstance(right, str) or isinstance(left, list) or isinstance(right, list):
                    raise TypeError("Cannot compare boolean, string, or list values with '>'")
                return left > right

            if op == '<=':
                if isinstance(left, bool) or isinstance(right, bool) or isinstance(left, str) or isinstance(right, str) or isinstance(left, list) or isinstance(right, list):
                    raise TypeError("Cannot compare boolean, string, or list values with '<='")
                return left <= right

            if op == '>=':
                if isinstance(left, bool) or isinstance(right, bool) or isinstance(left, str) or isinstance(right, str) or isinstance(left, list) or isinstance(right, list):
                    raise TypeError("Cannot compare boolean, string, or list values with '>='")
                return left >= right

            # Equality operations
            if op == '==':
                # Only allow comparison between same types
                if type(left) != type(right):
                    return False
                return left == right

            if op == '!=':
                # Only allow comparison between same types
                if type(left) != type(right):
                    return True
                return left != right

            # Logical operations
            if op == 'and':
                if not isinstance(left, bool) or not isinstance(right, bool):
                    raise TypeError("Logical 'and' requires boolean operands")
                return left and right

            if op == 'or':
                if not isinstance(left, bool) or not isinstance(right, bool):
                    raise TypeError("Logical 'or' requires boolean operands")
                return left or right

        raise ValueError(f"Unknown node type or operation: {node}")

    def execute(node):
        #Execute a statement node.
        if node['type'] == 'program':
            result = None
            for statement in node['body']:
                result = execute(statement)
            return result

        if node['type'] == 'expression':
            return evaluate(node['expression'])
        
        
        


        if node['type'] == 'print':
            value = evaluate(node['expression'])
            print(value)

            # Make a deep copy of list values to ensure the output stays consistent
            if isinstance(value, list):
                output_value = value.copy()
            else:
                output_value = value

            environment['output'].append(output_value)
            return value

        if node['type'] == 'assignment':
            value = evaluate(node['value'])
            environment['variables'][node['name']] = value
            return value

        if node['type'] == 'list_append':
            list_name = node['list']
            if list_name not in environment['variables']:
                raise ValueError(f"Undefined variable: {list_name}")

            lst = environment['variables'][list_name]
            if not isinstance(lst, list):
                raise TypeError("Cannot append to a non-list value")

            value = evaluate(node['value'])
            lst.append(value)
            return value

        if node['type'] == 'list_set':
            list_name = node['list']
            if list_name not in environment['variables']:
                raise ValueError(f"Undefined variable: {list_name}")

            lst = environment['variables'][list_name]
            if not isinstance(lst, list):
                raise TypeError("Cannot index-assign to a non-list value")

            index = evaluate(node['index'])
            if not isinstance(index, float) or int(index) != index:
                raise TypeError("List index must be an integer")

            index = int(index)
            if index < 0 or index >= len(lst):
                raise IndexError("List index out of range")

            value = evaluate(node['value'])
            lst[index] = value
            return value

        if node['type'] == 'if':
            condition = evaluate(node['condition'])
            if not isinstance(condition, bool):
                raise TypeError("Condition must be a boolean expression")

            result = None
            if condition:
                for statement in node['if_body']:
                    result = execute(statement)
            else:
                for statement in node['else_body']:
                    result = execute(statement)
            return result

        if node['type'] == 'while':
            result = None
            while True:
                condition = evaluate(node['condition'])
                if not isinstance(condition, bool):
                    raise TypeError("Condition must be a boolean expression")

                if not condition:
                    break

                for statement in node['body']:
                    result = execute(statement)

            return result

        raise ValueError(f"Unknown node type: {node['type']}")

    return execute(ast), environment

def run_program(code):
    #Run a program from source code.
    tokens = tokenize(code)
    ast = parse(tokens)
    return interpret(ast)

def interactive_mode():
    #Run the interpreter in interactive mode with persistent environment.
    print("Interactive Interpreter (Stage 1-6)")
    print("Type 'exit' or 'quit' to end the session")
    print("Examples:")
    print("  Variables: x = 10")
    print("  Lists: myList = [1, 2, 3]")
    print("  List access: myList[0]")
    print("  List append: myList.append(4)")
    print("  List length: len(myList)")
    print("  String/list length: len(\"hello\")")
    print("  Control: if (x > 5) { print \"x is greater than 5\" }")
    print("  Loops: while (x > 0) { print x; x = x - 1 }")

    environment = {'variables': {}, 'output': []}

    # Keep track of multiline input
    code_buffer = []

    while True:
        try:
            prompt = "... " if code_buffer else "> "
            line = input(prompt)

            if not code_buffer and line.lower() in ['exit', 'quit']:
                break

            code_buffer.append(line)

            # Try to run the accumulated code
            code = "\n".join(code_buffer)

            try:
                tokens = tokenize(code)
                ast = parse(tokens)
                result, environment = interpret(ast, environment)
                code_buffer = []  # Reset buffer on successful execution

                if result is not None and ast['body'] and ast['body'][-1]['type'] != 'print':
                    print(f"Result: {result}")

            except Exception as e:
                # If the error is about unexpected end of file, continue reading input
                if "Unexpected end of file" in str(e):
                    continue
                # Otherwise report the error and reset
                print(f"Error: {e}")
                code_buffer = []

        except KeyboardInterrupt:
            print("\nKeyboard interrupt")
            code_buffer = []

        except EOFError:
            print("\nEOF")
            break

def process_file(file_path):
    #Read and execute a program from a file.
    try:
        with open(file_path, 'r') as file:
            code = file.read()

        try:
            result, environment = run_program(code)
            print("Program executed successfully.")
            # if environment['output']:
            #     print("Output:")
            #     for item in environment['output']:
            #         print(item)
        except Exception as e:
            print(f"Runtime error: {e}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")

def main():
    #Main entry point for the program.
    import sys

    if len(sys.argv) == 1:
        # No arguments, run in interactive mode
        interactive_mode()
    elif len(sys.argv) == 2:
        # One argument, process file
        process_file(sys.argv[1])
    else:
        print("Usage: python sigil.py [file_path]")
        print("  If file_path is provided, the program from the file will be executed.")
        print("  If no arguments are provided, interactive mode will be started.")

if __name__ == "__main__":
    main()