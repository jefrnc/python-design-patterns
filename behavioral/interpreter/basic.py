"""
Interpreter Design Pattern - Gang of Four Implementation

Intent: Given a language, define a representation for its grammar along with an
interpreter that uses the representation to interpret sentences in the language.

Structure:
- AbstractExpression: declares an abstract Interpret operation
- TerminalExpression: implements an Interpret operation for terminal symbols
- NonterminalExpression: implements an Interpret operation for nonterminal symbols
- Context: contains information that's global to the interpreter
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Union


class Context:
    """
    The Context contains information that's global to the interpreter.
    """
    
    def __init__(self):
        self._variables: Dict[str, int] = {}
    
    def set_variable(self, name: str, value: int) -> None:
        """
        Set a variable value in the context.
        """
        self._variables[name] = value
    
    def get_variable(self, name: str) -> int:
        """
        Get a variable value from the context.
        """
        return self._variables.get(name, 0)
    
    def has_variable(self, name: str) -> bool:
        """
        Check if a variable exists in the context.
        """
        return name in self._variables
    
    def get_all_variables(self) -> Dict[str, int]:
        """
        Get all variables in the context.
        """
        return self._variables.copy()


class AbstractExpression(ABC):
    """
    The Abstract Expression declares an abstract Interpret operation that is
    common to all nodes in the abstract syntax tree.
    """
    
    @abstractmethod
    def interpret(self, context: Context) -> int:
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass


class NumberExpression(AbstractExpression):
    """
    Terminal Expression for numbers.
    """
    
    def __init__(self, number: int):
        self._number = number
    
    def interpret(self, context: Context) -> int:
        return self._number
    
    def __str__(self) -> str:
        return str(self._number)


class VariableExpression(AbstractExpression):
    """
    Terminal Expression for variables.
    """
    
    def __init__(self, name: str):
        self._name = name
    
    def interpret(self, context: Context) -> int:
        return context.get_variable(self._name)
    
    def __str__(self) -> str:
        return self._name


class AddExpression(AbstractExpression):
    """
    Nonterminal Expression for addition.
    """
    
    def __init__(self, left: AbstractExpression, right: AbstractExpression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Context) -> int:
        return self._left.interpret(context) + self._right.interpret(context)
    
    def __str__(self) -> str:
        return f"({self._left} + {self._right})"


class SubtractExpression(AbstractExpression):
    """
    Nonterminal Expression for subtraction.
    """
    
    def __init__(self, left: AbstractExpression, right: AbstractExpression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Context) -> int:
        return self._left.interpret(context) - self._right.interpret(context)
    
    def __str__(self) -> str:
        return f"({self._left} - {self._right})"


class MultiplyExpression(AbstractExpression):
    """
    Nonterminal Expression for multiplication.
    """
    
    def __init__(self, left: AbstractExpression, right: AbstractExpression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Context) -> int:
        return self._left.interpret(context) * self._right.interpret(context)
    
    def __str__(self) -> str:
        return f"({self._left} * {self._right})"


class DivideExpression(AbstractExpression):
    """
    Nonterminal Expression for division.
    """
    
    def __init__(self, left: AbstractExpression, right: AbstractExpression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Context) -> int:
        right_value = self._right.interpret(context)
        if right_value == 0:
            raise ValueError("Division by zero")
        return self._left.interpret(context) // right_value
    
    def __str__(self) -> str:
        return f"({self._left} / {self._right})"


# More complex example: Boolean expressions
class BooleanExpression(ABC):
    """
    Abstract expression for boolean operations.
    """
    
    @abstractmethod
    def interpret(self, context: Context) -> bool:
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass


class BooleanVariable(BooleanExpression):
    """
    Terminal expression for boolean variables.
    """
    
    def __init__(self, name: str):
        self._name = name
    
    def interpret(self, context: Context) -> bool:
        return bool(context.get_variable(self._name))
    
    def __str__(self) -> str:
        return self._name


class BooleanConstant(BooleanExpression):
    """
    Terminal expression for boolean constants.
    """
    
    def __init__(self, value: bool):
        self._value = value
    
    def interpret(self, context: Context) -> bool:
        return self._value
    
    def __str__(self) -> str:
        return str(self._value).lower()


class AndExpression(BooleanExpression):
    """
    Nonterminal expression for AND operation.
    """
    
    def __init__(self, left: BooleanExpression, right: BooleanExpression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Context) -> bool:
        return self._left.interpret(context) and self._right.interpret(context)
    
    def __str__(self) -> str:
        return f"({self._left} AND {self._right})"


class OrExpression(BooleanExpression):
    """
    Nonterminal expression for OR operation.
    """
    
    def __init__(self, left: BooleanExpression, right: BooleanExpression):
        self._left = left
        self._right = right
    
    def interpret(self, context: Context) -> bool:
        return self._left.interpret(context) or self._right.interpret(context)
    
    def __str__(self) -> str:
        return f"({self._left} OR {self._right})"


class NotExpression(BooleanExpression):
    """
    Nonterminal expression for NOT operation.
    """
    
    def __init__(self, expression: BooleanExpression):
        self._expression = expression
    
    def interpret(self, context: Context) -> bool:
        return not self._expression.interpret(context)
    
    def __str__(self) -> str:
        return f"(NOT {self._expression})"


# Simple parser for arithmetic expressions
class ArithmeticParser:
    """
    Simple parser for arithmetic expressions.
    Supports: numbers, variables, +, -, *, /, parentheses
    """
    
    def __init__(self, expression: str):
        self._tokens = self._tokenize(expression)
        self._position = 0
    
    def _tokenize(self, expression: str) -> List[str]:
        """
        Tokenize the expression string.
        """
        tokens = []
        i = 0
        while i < len(expression):
            char = expression[i]
            
            if char.isspace():
                i += 1
                continue
            elif char.isdigit():
                # Parse number
                num = ""
                while i < len(expression) and expression[i].isdigit():
                    num += expression[i]
                    i += 1
                tokens.append(num)
            elif char.isalpha():
                # Parse variable
                var = ""
                while i < len(expression) and (expression[i].isalnum() or expression[i] == '_'):
                    var += expression[i]
                    i += 1
                tokens.append(var)
            elif char in "+-*/()":
                tokens.append(char)
                i += 1
            else:
                raise ValueError(f"Invalid character: {char}")
        
        return tokens
    
    def parse(self) -> AbstractExpression:
        """
        Parse the tokens into an expression tree.
        """
        return self._parse_expression()
    
    def _parse_expression(self) -> AbstractExpression:
        """
        Parse an expression (handles + and -)
        """
        left = self._parse_term()
        
        while self._position < len(self._tokens):
            token = self._tokens[self._position]
            if token == '+':
                self._position += 1
                right = self._parse_term()
                left = AddExpression(left, right)
            elif token == '-':
                self._position += 1
                right = self._parse_term()
                left = SubtractExpression(left, right)
            else:
                break
        
        return left
    
    def _parse_term(self) -> AbstractExpression:
        """
        Parse a term (handles * and /)
        """
        left = self._parse_factor()
        
        while self._position < len(self._tokens):
            token = self._tokens[self._position]
            if token == '*':
                self._position += 1
                right = self._parse_factor()
                left = MultiplyExpression(left, right)
            elif token == '/':
                self._position += 1
                right = self._parse_factor()
                left = DivideExpression(left, right)
            else:
                break
        
        return left
    
    def _parse_factor(self) -> AbstractExpression:
        """
        Parse a factor (numbers, variables, parenthesized expressions)
        """
        if self._position >= len(self._tokens):
            raise ValueError("Unexpected end of expression")
        
        token = self._tokens[self._position]
        
        if token == '(':
            self._position += 1
            expr = self._parse_expression()
            if self._position >= len(self._tokens) or self._tokens[self._position] != ')':
                raise ValueError("Missing closing parenthesis")
            self._position += 1
            return expr
        elif token.isdigit():
            self._position += 1
            return NumberExpression(int(token))
        elif token.isalpha():
            self._position += 1
            return VariableExpression(token)
        else:
            raise ValueError(f"Unexpected token: {token}")


# SQL-like query interpreter
class QueryExpression(ABC):
    """
    Abstract expression for SQL-like queries.
    """
    
    @abstractmethod
    def interpret(self, data: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[str, int]]]:
        pass


class SelectExpression(QueryExpression):
    """
    Expression for SELECT operations.
    """
    
    def __init__(self, columns: List[str], from_expr: QueryExpression):
        self._columns = columns
        self._from_expr = from_expr
    
    def interpret(self, data: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[str, int]]]:
        # Get data from source
        source_data = self._from_expr.interpret(data)
        
        # Select specified columns
        if self._columns == ['*']:
            return source_data
        
        result = []
        for row in source_data:
            selected_row = {}
            for col in self._columns:
                if col in row:
                    selected_row[col] = row[col]
            result.append(selected_row)
        
        return result


class TableExpression(QueryExpression):
    """
    Terminal expression for table data.
    """
    
    def __init__(self, table_name: str):
        self._table_name = table_name
    
    def interpret(self, data: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[str, int]]]:
        # In a real implementation, this would fetch data from a database
        # For demo purposes, we'll return the provided data
        return data


class WhereExpression(QueryExpression):
    """
    Expression for WHERE filtering.
    """
    
    def __init__(self, source: QueryExpression, condition: callable):
        self._source = source
        self._condition = condition
    
    def interpret(self, data: List[Dict[str, Union[str, int]]]) -> List[Dict[str, Union[str, int]]]:
        source_data = self._source.interpret(data)
        return [row for row in source_data if self._condition(row)]


def main():
    """
    The client code demonstrates the Interpreter pattern.
    """
    print("=== Interpreter Pattern Demo ===")
    
    # Basic arithmetic interpreter
    print("\n1. Arithmetic Expression Interpreter:")
    
    context = Context()
    context.set_variable("x", 10)
    context.set_variable("y", 5)
    context.set_variable("z", 2)
    
    print(f"Context variables: {context.get_all_variables()}")
    
    # Manual expression construction
    # Expression: (x + y) * z - 3
    expr1 = SubtractExpression(
        MultiplyExpression(
            AddExpression(
                VariableExpression("x"),
                VariableExpression("y")
            ),
            VariableExpression("z")
        ),
        NumberExpression(3)
    )
    
    print(f"Expression: {expr1}")
    print(f"Result: {expr1.interpret(context)}")
    
    # Using parser
    print("\n2. Arithmetic Parser:")
    
    expressions = [
        "x + y",
        "x * y + z",
        "(x + y) * z",
        "x + y * z - 3",
        "(x - y) / z + 1"
    ]
    
    for expr_str in expressions:
        try:
            parser = ArithmeticParser(expr_str)
            expr = parser.parse()
            result = expr.interpret(context)
            print(f"{expr_str} = {result}")
        except Exception as e:
            print(f"{expr_str} = Error: {e}")
    
    # Boolean expressions
    print("\n3. Boolean Expression Interpreter:")
    
    bool_context = Context()
    bool_context.set_variable("a", 1)  # True
    bool_context.set_variable("b", 0)  # False
    bool_context.set_variable("c", 1)  # True
    
    print(f"Boolean context: a={bool(bool_context.get_variable('a'))}, "
          f"b={bool(bool_context.get_variable('b'))}, "
          f"c={bool(bool_context.get_variable('c'))}")
    
    # Boolean expression: (a AND b) OR (NOT b AND c)
    bool_expr = OrExpression(
        AndExpression(
            BooleanVariable("a"),
            BooleanVariable("b")
        ),
        AndExpression(
            NotExpression(BooleanVariable("b")),
            BooleanVariable("c")
        )
    )
    
    print(f"Expression: {bool_expr}")
    print(f"Result: {bool_expr.interpret(bool_context)}")
    
    # More boolean expressions
    bool_exprs = [
        AndExpression(BooleanVariable("a"), BooleanVariable("c")),
        OrExpression(BooleanVariable("a"), BooleanVariable("b")),
        NotExpression(BooleanVariable("b")),
        AndExpression(
            BooleanVariable("a"),
            NotExpression(BooleanVariable("b"))
        )
    ]
    
    for expr in bool_exprs:
        result = expr.interpret(bool_context)
        print(f"{expr} = {result}")
    
    # SQL-like query interpreter
    print("\n4. SQL-like Query Interpreter:")
    
    # Sample data
    employees = [
        {"name": "Alice", "age": 30, "department": "Engineering"},
        {"name": "Bob", "age": 25, "department": "Marketing"},
        {"name": "Charlie", "age": 35, "department": "Engineering"},
        {"name": "Diana", "age": 28, "department": "Sales"},
        {"name": "Eve", "age": 32, "department": "Engineering"}
    ]
    
    print("Sample data:")
    for emp in employees:
        print(f"  {emp}")
    
    # Query: SELECT name, age FROM employees WHERE department = 'Engineering'
    query = SelectExpression(
        ["name", "age"],
        WhereExpression(
            TableExpression("employees"),
            lambda row: row.get("department") == "Engineering"
        )
    )
    
    result = query.interpret(employees)
    print(f"\nQuery result (Engineering employees):")
    for row in result:
        print(f"  {row}")
    
    # Query: SELECT * FROM employees WHERE age > 30
    query2 = SelectExpression(
        ["*"],
        WhereExpression(
            TableExpression("employees"),
            lambda row: row.get("age", 0) > 30
        )
    )
    
    result2 = query2.interpret(employees)
    print(f"\nQuery result (age > 30):")
    for row in result2:
        print(f"  {row}")
    
    # Complex arithmetic with different contexts
    print("\n5. Different Contexts:")
    
    # Create expression once
    complex_expr = AddExpression(
        MultiplyExpression(VariableExpression("a"), VariableExpression("b")),
        DivideExpression(VariableExpression("c"), VariableExpression("d"))
    )
    
    print(f"Expression: {complex_expr}")
    
    # Different contexts
    contexts = [
        {"a": 2, "b": 3, "c": 10, "d": 2},
        {"a": 5, "b": 4, "c": 15, "d": 3},
        {"a": 1, "b": 7, "c": 20, "d": 4}
    ]
    
    for i, ctx_vars in enumerate(contexts):
        ctx = Context()
        for var, value in ctx_vars.items():
            ctx.set_variable(var, value)
        
        result = complex_expr.interpret(ctx)
        print(f"Context {i+1} {ctx_vars}: {result}")


if __name__ == "__main__":
    main()