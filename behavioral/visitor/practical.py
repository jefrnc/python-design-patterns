"""
Visitor Design Pattern - Real World Implementation

Real-world example: Abstract Syntax Tree (AST) Compiler and Code Analysis System
A comprehensive compiler system that uses visitors to perform different operations
on an Abstract Syntax Tree: code generation, optimization, static analysis, and formatting.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Set
from datetime import datetime
from enum import Enum
import re


class DataType(Enum):
    """Data types supported by the language."""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    FUNCTION = "function"
    VOID = "void"


class Operator(Enum):
    """Operators supported by the language."""
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    EQUALS = "=="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    AND = "&&"
    OR = "||"
    NOT = "!"
    ASSIGN = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="


class Visitor(ABC):
    """
    Abstract visitor interface for AST operations.
    """
    
    @abstractmethod
    def visit_program(self, node: 'ProgramNode') -> Any:
        pass
    
    @abstractmethod
    def visit_function_declaration(self, node: 'FunctionDeclarationNode') -> Any:
        pass
    
    @abstractmethod
    def visit_variable_declaration(self, node: 'VariableDeclarationNode') -> Any:
        pass
    
    @abstractmethod
    def visit_assignment(self, node: 'AssignmentNode') -> Any:
        pass
    
    @abstractmethod
    def visit_binary_expression(self, node: 'BinaryExpressionNode') -> Any:
        pass
    
    @abstractmethod
    def visit_unary_expression(self, node: 'UnaryExpressionNode') -> Any:
        pass
    
    @abstractmethod
    def visit_function_call(self, node: 'FunctionCallNode') -> Any:
        pass
    
    @abstractmethod
    def visit_if_statement(self, node: 'IfStatementNode') -> Any:
        pass
    
    @abstractmethod
    def visit_while_loop(self, node: 'WhileLoopNode') -> Any:
        pass
    
    @abstractmethod
    def visit_for_loop(self, node: 'ForLoopNode') -> Any:
        pass
    
    @abstractmethod
    def visit_return_statement(self, node: 'ReturnStatementNode') -> Any:
        pass
    
    @abstractmethod
    def visit_block_statement(self, node: 'BlockStatementNode') -> Any:
        pass
    
    @abstractmethod
    def visit_literal(self, node: 'LiteralNode') -> Any:
        pass
    
    @abstractmethod
    def visit_identifier(self, node: 'IdentifierNode') -> Any:
        pass
    
    @abstractmethod
    def visit_array_access(self, node: 'ArrayAccessNode') -> Any:
        pass


class ASTNode(ABC):
    """
    Abstract base class for all AST nodes.
    """
    
    def __init__(self, line_number: int = 0, column: int = 0):
        self.line_number = line_number
        self.column = column
        self.parent: Optional['ASTNode'] = None
        self.metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def accept(self, visitor: Visitor) -> Any:
        """Accept a visitor and delegate to the appropriate visit method."""
        pass
    
    def get_position(self) -> str:
        return f"line {self.line_number}, column {self.column}"


class ProgramNode(ASTNode):
    """Root node of the AST representing the entire program."""
    
    def __init__(self, statements: List[ASTNode]):
        super().__init__()
        self.statements = statements
        for stmt in statements:
            stmt.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_program(self)


class FunctionDeclarationNode(ASTNode):
    """Function declaration node."""
    
    def __init__(self, name: str, parameters: List[tuple], return_type: DataType, 
                 body: 'BlockStatementNode', line_number: int = 0):
        super().__init__(line_number)
        self.name = name
        self.parameters = parameters  # List of (name, type) tuples
        self.return_type = return_type
        self.body = body
        body.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_function_declaration(self)


class VariableDeclarationNode(ASTNode):
    """Variable declaration node."""
    
    def __init__(self, name: str, data_type: DataType, 
                 initializer: Optional[ASTNode] = None, line_number: int = 0):
        super().__init__(line_number)
        self.name = name
        self.data_type = data_type
        self.initializer = initializer
        if initializer:
            initializer.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_variable_declaration(self)


class AssignmentNode(ASTNode):
    """Assignment statement node."""
    
    def __init__(self, target: ASTNode, operator: Operator, 
                 value: ASTNode, line_number: int = 0):
        super().__init__(line_number)
        self.target = target
        self.operator = operator
        self.value = value
        target.parent = self
        value.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_assignment(self)


class BinaryExpressionNode(ASTNode):
    """Binary expression node (e.g., a + b, x > y)."""
    
    def __init__(self, left: ASTNode, operator: Operator, 
                 right: ASTNode, line_number: int = 0):
        super().__init__(line_number)
        self.left = left
        self.operator = operator
        self.right = right
        left.parent = self
        right.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_binary_expression(self)


class UnaryExpressionNode(ASTNode):
    """Unary expression node (e.g., -x, !flag)."""
    
    def __init__(self, operator: Operator, operand: ASTNode, line_number: int = 0):
        super().__init__(line_number)
        self.operator = operator
        self.operand = operand
        operand.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_unary_expression(self)


class FunctionCallNode(ASTNode):
    """Function call node."""
    
    def __init__(self, function_name: str, arguments: List[ASTNode], line_number: int = 0):
        super().__init__(line_number)
        self.function_name = function_name
        self.arguments = arguments
        for arg in arguments:
            arg.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_function_call(self)


class IfStatementNode(ASTNode):
    """If statement node."""
    
    def __init__(self, condition: ASTNode, then_statement: ASTNode, 
                 else_statement: Optional[ASTNode] = None, line_number: int = 0):
        super().__init__(line_number)
        self.condition = condition
        self.then_statement = then_statement
        self.else_statement = else_statement
        condition.parent = self
        then_statement.parent = self
        if else_statement:
            else_statement.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_if_statement(self)


class WhileLoopNode(ASTNode):
    """While loop node."""
    
    def __init__(self, condition: ASTNode, body: ASTNode, line_number: int = 0):
        super().__init__(line_number)
        self.condition = condition
        self.body = body
        condition.parent = self
        body.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_while_loop(self)


class ForLoopNode(ASTNode):
    """For loop node."""
    
    def __init__(self, initialization: Optional[ASTNode], condition: Optional[ASTNode],
                 increment: Optional[ASTNode], body: ASTNode, line_number: int = 0):
        super().__init__(line_number)
        self.initialization = initialization
        self.condition = condition
        self.increment = increment
        self.body = body
        
        if initialization:
            initialization.parent = self
        if condition:
            condition.parent = self
        if increment:
            increment.parent = self
        body.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_for_loop(self)


class ReturnStatementNode(ASTNode):
    """Return statement node."""
    
    def __init__(self, value: Optional[ASTNode] = None, line_number: int = 0):
        super().__init__(line_number)
        self.value = value
        if value:
            value.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_return_statement(self)


class BlockStatementNode(ASTNode):
    """Block statement node (compound statement)."""
    
    def __init__(self, statements: List[ASTNode]):
        super().__init__()
        self.statements = statements
        for stmt in statements:
            stmt.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_block_statement(self)


class LiteralNode(ASTNode):
    """Literal value node."""
    
    def __init__(self, value: Any, data_type: DataType, line_number: int = 0):
        super().__init__(line_number)
        self.value = value
        self.data_type = data_type
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_literal(self)


class IdentifierNode(ASTNode):
    """Identifier (variable/function name) node."""
    
    def __init__(self, name: str, line_number: int = 0):
        super().__init__(line_number)
        self.name = name
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_identifier(self)


class ArrayAccessNode(ASTNode):
    """Array access node (e.g., arr[index])."""
    
    def __init__(self, array: ASTNode, index: ASTNode, line_number: int = 0):
        super().__init__(line_number)
        self.array = array
        self.index = index
        array.parent = self
        index.parent = self
    
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_array_access(self)


class CodeGeneratorVisitor(Visitor):
    """
    Visitor that generates target code (JavaScript) from the AST.
    """
    
    def __init__(self, target_language: str = "javascript"):
        self.target_language = target_language
        self.output_lines: List[str] = []
        self.indent_level = 0
        self.symbol_table: Dict[str, DataType] = {}
    
    def _emit(self, code: str) -> None:
        """Emit code with proper indentation."""
        indent = "  " * self.indent_level
        self.output_lines.append(indent + code)
    
    def _emit_inline(self, code: str) -> str:
        """Return code without adding to output (for expressions)."""
        return code
    
    def get_generated_code(self) -> str:
        """Get the complete generated code."""
        return "\n".join(self.output_lines)
    
    def visit_program(self, node: ProgramNode) -> Any:
        self._emit("// Generated code")
        self._emit(f"// Target: {self.target_language}")
        self._emit(f"// Generated at: {datetime.now().isoformat()}")
        self._emit("")
        
        for statement in node.statements:
            statement.accept(self)
        
        return self.get_generated_code()
    
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> Any:
        # Generate parameter list
        params = ", ".join([name for name, _ in node.parameters])
        
        self._emit(f"function {node.name}({params}) {{")
        self.indent_level += 1
        
        # Store parameters in symbol table
        for param_name, param_type in node.parameters:
            self.symbol_table[param_name] = param_type
        
        node.body.accept(self)
        
        self.indent_level -= 1
        self._emit("}")
        self._emit("")
    
    def visit_variable_declaration(self, node: VariableDeclarationNode) -> Any:
        self.symbol_table[node.name] = node.data_type
        
        if node.initializer:
            initializer_code = node.initializer.accept(self)
            self._emit(f"let {node.name} = {initializer_code};")
        else:
            default_value = self._get_default_value(node.data_type)
            self._emit(f"let {node.name} = {default_value};")
    
    def visit_assignment(self, node: AssignmentNode) -> Any:
        target_code = node.target.accept(self)
        value_code = node.value.accept(self)
        
        operator_map = {
            Operator.ASSIGN: "=",
            Operator.PLUS_ASSIGN: "+=",
            Operator.MINUS_ASSIGN: "-="
        }
        
        op = operator_map.get(node.operator, "=")
        self._emit(f"{target_code} {op} {value_code};")
    
    def visit_binary_expression(self, node: BinaryExpressionNode) -> Any:
        left_code = node.left.accept(self)
        right_code = node.right.accept(self)
        
        operator_map = {
            Operator.ADD: "+",
            Operator.SUBTRACT: "-",
            Operator.MULTIPLY: "*",
            Operator.DIVIDE: "/",
            Operator.MODULO: "%",
            Operator.EQUALS: "===",
            Operator.NOT_EQUALS: "!==",
            Operator.LESS_THAN: "<",
            Operator.GREATER_THAN: ">",
            Operator.LESS_EQUAL: "<=",
            Operator.GREATER_EQUAL: ">=",
            Operator.AND: "&&",
            Operator.OR: "||"
        }
        
        op = operator_map.get(node.operator, node.operator.value)
        return f"({left_code} {op} {right_code})"
    
    def visit_unary_expression(self, node: UnaryExpressionNode) -> Any:
        operand_code = node.operand.accept(self)
        
        operator_map = {
            Operator.NOT: "!",
            Operator.SUBTRACT: "-"
        }
        
        op = operator_map.get(node.operator, node.operator.value)
        return f"{op}{operand_code}"
    
    def visit_function_call(self, node: FunctionCallNode) -> Any:
        args = [arg.accept(self) for arg in node.arguments]
        args_str = ", ".join(args)
        return f"{node.function_name}({args_str})"
    
    def visit_if_statement(self, node: IfStatementNode) -> Any:
        condition_code = node.condition.accept(self)
        self._emit(f"if ({condition_code}) {{")
        self.indent_level += 1
        node.then_statement.accept(self)
        self.indent_level -= 1
        
        if node.else_statement:
            self._emit("} else {")
            self.indent_level += 1
            node.else_statement.accept(self)
            self.indent_level -= 1
        
        self._emit("}")
    
    def visit_while_loop(self, node: WhileLoopNode) -> Any:
        condition_code = node.condition.accept(self)
        self._emit(f"while ({condition_code}) {{")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self._emit("}")
    
    def visit_for_loop(self, node: ForLoopNode) -> Any:
        init_code = node.initialization.accept(self) if node.initialization else ""
        condition_code = node.condition.accept(self) if node.condition else "true"
        increment_code = node.increment.accept(self) if node.increment else ""
        
        # Remove semicolon from init if it's a statement
        if init_code.endswith(";"):
            init_code = init_code[:-1]
        
        self._emit(f"for ({init_code}; {condition_code}; {increment_code}) {{")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self._emit("}")
    
    def visit_return_statement(self, node: ReturnStatementNode) -> Any:
        if node.value:
            value_code = node.value.accept(self)
            self._emit(f"return {value_code};")
        else:
            self._emit("return;")
    
    def visit_block_statement(self, node: BlockStatementNode) -> Any:
        for statement in node.statements:
            statement.accept(self)
    
    def visit_literal(self, node: LiteralNode) -> Any:
        if node.data_type == DataType.STRING:
            return f'"{node.value}"'
        elif node.data_type == DataType.BOOLEAN:
            return "true" if node.value else "false"
        else:
            return str(node.value)
    
    def visit_identifier(self, node: IdentifierNode) -> Any:
        return node.name
    
    def visit_array_access(self, node: ArrayAccessNode) -> Any:
        array_code = node.array.accept(self)
        index_code = node.index.accept(self)
        return f"{array_code}[{index_code}]"
    
    def _get_default_value(self, data_type: DataType) -> str:
        """Get default value for a data type."""
        defaults = {
            DataType.INTEGER: "0",
            DataType.FLOAT: "0.0",
            DataType.STRING: '""',
            DataType.BOOLEAN: "false",
            DataType.ARRAY: "[]",
            DataType.OBJECT: "{}"
        }
        return defaults.get(data_type, "null")


class StaticAnalyzerVisitor(Visitor):
    """
    Visitor that performs static analysis on the AST.
    """
    
    def __init__(self):
        self.warnings: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.symbol_table: Dict[str, Dict[str, Any]] = {}
        self.current_function: Optional[str] = None
        self.used_variables: Set[str] = set()
        self.declared_variables: Set[str] = set()
        self.function_calls: List[str] = []
        self.complexity_score = 0
    
    def _add_warning(self, node: ASTNode, message: str, category: str = "general") -> None:
        """Add a warning to the analysis results."""
        self.warnings.append({
            "message": message,
            "category": category,
            "line": node.line_number,
            "position": node.get_position(),
            "severity": "warning"
        })
    
    def _add_error(self, node: ASTNode, message: str, category: str = "general") -> None:
        """Add an error to the analysis results."""
        self.errors.append({
            "message": message,
            "category": category,
            "line": node.line_number,
            "position": node.get_position(),
            "severity": "error"
        })
    
    def get_analysis_report(self) -> Dict[str, Any]:
        """Get complete static analysis report."""
        unused_variables = self.declared_variables - self.used_variables
        
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "declared_variables": len(self.declared_variables),
                "used_variables": len(self.used_variables),
                "unused_variables": len(unused_variables),
                "function_calls": len(self.function_calls),
                "complexity_score": self.complexity_score
            },
            "unused_variables": list(unused_variables),
            "function_calls": self.function_calls,
            "symbol_table": self.symbol_table
        }
    
    def visit_program(self, node: ProgramNode) -> Any:
        for statement in node.statements:
            statement.accept(self)
        return self.get_analysis_report()
    
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> Any:
        self.current_function = node.name
        
        # Check for function name conventions
        if not re.match(r'^[a-z][a-zA-Z0-9]*$', node.name):
            self._add_warning(node, f"Function name '{node.name}' doesn't follow camelCase convention", "naming")
        
        # Add function to symbol table
        self.symbol_table[node.name] = {
            "type": "function",
            "return_type": node.return_type,
            "parameters": node.parameters,
            "line": node.line_number
        }
        
        # Analyze function body
        old_declared = self.declared_variables.copy()
        old_used = self.used_variables.copy()
        
        # Add parameters to declared variables
        for param_name, param_type in node.parameters:
            self.declared_variables.add(param_name)
        
        node.body.accept(self)
        
        # Check for unused parameters
        for param_name, _ in node.parameters:
            if param_name not in self.used_variables:
                self._add_warning(node, f"Parameter '{param_name}' is declared but never used", "unused")
        
        # Restore previous scope
        self.declared_variables = old_declared
        self.used_variables = old_used
        self.current_function = None
    
    def visit_variable_declaration(self, node: VariableDeclarationNode) -> Any:
        # Check for variable name conventions
        if not re.match(r'^[a-z][a-zA-Z0-9]*$', node.name):
            self._add_warning(node, f"Variable name '{node.name}' doesn't follow camelCase convention", "naming")
        
        # Check for redeclaration
        if node.name in self.declared_variables:
            self._add_error(node, f"Variable '{node.name}' is already declared", "redeclaration")
        
        self.declared_variables.add(node.name)
        
        # Add to symbol table
        self.symbol_table[node.name] = {
            "type": "variable",
            "data_type": node.data_type,
            "line": node.line_number,
            "initialized": node.initializer is not None
        }
        
        if node.initializer:
            node.initializer.accept(self)
    
    def visit_assignment(self, node: AssignmentNode) -> Any:
        node.target.accept(self)
        node.value.accept(self)
        
        # Check for self-assignment
        if (isinstance(node.target, IdentifierNode) and 
            isinstance(node.value, IdentifierNode) and
            node.target.name == node.value.name and
            node.operator == Operator.ASSIGN):
            self._add_warning(node, f"Self-assignment detected: {node.target.name} = {node.value.name}", "logic")
    
    def visit_binary_expression(self, node: BinaryExpressionNode) -> Any:
        node.left.accept(self)
        node.right.accept(self)
        
        # Check for potential division by zero
        if (node.operator == Operator.DIVIDE and 
            isinstance(node.right, LiteralNode) and 
            node.right.value == 0):
            self._add_error(node, "Division by zero detected", "runtime")
        
        # Check for comparison with boolean literals
        if (node.operator in [Operator.EQUALS, Operator.NOT_EQUALS] and
            isinstance(node.right, LiteralNode) and
            node.right.data_type == DataType.BOOLEAN):
            self._add_warning(node, "Comparison with boolean literal can be simplified", "style")
    
    def visit_unary_expression(self, node: UnaryExpressionNode) -> Any:
        node.operand.accept(self)
    
    def visit_function_call(self, node: FunctionCallNode) -> Any:
        self.function_calls.append(node.function_name)
        
        # Check if function is declared
        if node.function_name not in self.symbol_table:
            self._add_error(node, f"Function '{node.function_name}' is not declared", "undefined")
        
        for arg in node.arguments:
            arg.accept(self)
    
    def visit_if_statement(self, node: IfStatementNode) -> Any:
        self.complexity_score += 1  # Cyclomatic complexity
        
        node.condition.accept(self)
        node.then_statement.accept(self)
        
        if node.else_statement:
            node.else_statement.accept(self)
        
        # Check for constant conditions
        if isinstance(node.condition, LiteralNode):
            if node.condition.data_type == DataType.BOOLEAN:
                if node.condition.value:
                    self._add_warning(node, "If condition is always true", "logic")
                else:
                    self._add_warning(node, "If condition is always false", "logic")
    
    def visit_while_loop(self, node: WhileLoopNode) -> Any:
        self.complexity_score += 1  # Cyclomatic complexity
        
        node.condition.accept(self)
        node.body.accept(self)
        
        # Check for infinite loops
        if (isinstance(node.condition, LiteralNode) and 
            node.condition.data_type == DataType.BOOLEAN and
            node.condition.value):
            self._add_warning(node, "Potential infinite loop detected", "logic")
    
    def visit_for_loop(self, node: ForLoopNode) -> Any:
        self.complexity_score += 1  # Cyclomatic complexity
        
        if node.initialization:
            node.initialization.accept(self)
        if node.condition:
            node.condition.accept(self)
        if node.increment:
            node.increment.accept(self)
        
        node.body.accept(self)
    
    def visit_return_statement(self, node: ReturnStatementNode) -> Any:
        if node.value:
            node.value.accept(self)
    
    def visit_block_statement(self, node: BlockStatementNode) -> Any:
        for statement in node.statements:
            statement.accept(self)
    
    def visit_literal(self, node: LiteralNode) -> Any:
        # Check for magic numbers
        if (node.data_type in [DataType.INTEGER, DataType.FLOAT] and 
            node.value not in [0, 1, -1] and
            abs(node.value) > 1):
            self._add_warning(node, f"Magic number detected: {node.value}", "style")
    
    def visit_identifier(self, node: IdentifierNode) -> Any:
        # Mark variable as used
        self.used_variables.add(node.name)
        
        # Check if variable is declared
        if node.name not in self.declared_variables and node.name not in self.symbol_table:
            self._add_error(node, f"Variable '{node.name}' is not declared", "undefined")
    
    def visit_array_access(self, node: ArrayAccessNode) -> Any:
        node.array.accept(self)
        node.index.accept(self)


class CodeFormatterVisitor(Visitor):
    """
    Visitor that formats code with proper indentation and style.
    """
    
    def __init__(self, indent_size: int = 2, max_line_length: int = 80):
        self.indent_size = indent_size
        self.max_line_length = max_line_length
        self.output_lines: List[str] = []
        self.indent_level = 0
        self.current_line_length = 0
    
    def _emit(self, code: str, add_newline: bool = True) -> None:
        """Emit formatted code with proper indentation."""
        indent = " " * (self.indent_level * self.indent_size)
        formatted_line = indent + code
        
        if add_newline:
            self.output_lines.append(formatted_line)
        else:
            if self.output_lines:
                self.output_lines[-1] += code
            else:
                self.output_lines.append(formatted_line)
        
        self.current_line_length = len(formatted_line)
    
    def _should_break_line(self, additional_content: str) -> bool:
        """Check if line should be broken."""
        return self.current_line_length + len(additional_content) > self.max_line_length
    
    def get_formatted_code(self) -> str:
        """Get the complete formatted code."""
        return "\n".join(self.output_lines)
    
    def visit_program(self, node: ProgramNode) -> Any:
        for i, statement in enumerate(node.statements):
            if i > 0:
                self._emit("")  # Add blank line between top-level statements
            statement.accept(self)
        return self.get_formatted_code()
    
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> Any:
        # Format parameter list
        params = []
        for name, param_type in node.parameters:
            params.append(f"{name}: {param_type.value}")
        
        param_str = ", ".join(params)
        
        # Check if function signature should be broken
        signature = f"function {node.name}({param_str}): {node.return_type.value} {{"
        
        if self._should_break_line(signature):
            self._emit(f"function {node.name}(")
            self.indent_level += 1
            for i, param in enumerate(params):
                comma = "," if i < len(params) - 1 else ""
                self._emit(f"{param}{comma}")
            self.indent_level -= 1
            self._emit(f"): {node.return_type.value} {{")
        else:
            self._emit(signature)
        
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self._emit("}")
    
    def visit_variable_declaration(self, node: VariableDeclarationNode) -> Any:
        if node.initializer:
            initializer_code = node.initializer.accept(self)
            self._emit(f"{node.data_type.value} {node.name} = {initializer_code};")
        else:
            self._emit(f"{node.data_type.value} {node.name};")
    
    def visit_assignment(self, node: AssignmentNode) -> Any:
        target_code = node.target.accept(self)
        value_code = node.value.accept(self)
        self._emit(f"{target_code} {node.operator.value} {value_code};")
    
    def visit_binary_expression(self, node: BinaryExpressionNode) -> Any:
        left_code = node.left.accept(self)
        right_code = node.right.accept(self)
        
        # Add spaces around operators for readability
        return f"{left_code} {node.operator.value} {right_code}"
    
    def visit_unary_expression(self, node: UnaryExpressionNode) -> Any:
        operand_code = node.operand.accept(self)
        return f"{node.operator.value}{operand_code}"
    
    def visit_function_call(self, node: FunctionCallNode) -> Any:
        args = [arg.accept(self) for arg in node.arguments]
        
        # Format arguments based on length
        args_str = ", ".join(args)
        call_str = f"{node.function_name}({args_str})"
        
        if len(call_str) > 40:  # Break long function calls
            result = f"{node.function_name}(\n"
            self.indent_level += 1
            for i, arg in enumerate(args):
                comma = "," if i < len(args) - 1 else ""
                result += " " * (self.indent_level * self.indent_size) + f"{arg}{comma}\n"
            self.indent_level -= 1
            result += " " * (self.indent_level * self.indent_size) + ")"
            return result
        else:
            return call_str
    
    def visit_if_statement(self, node: IfStatementNode) -> Any:
        condition_code = node.condition.accept(self)
        self._emit(f"if ({condition_code}) {{")
        
        self.indent_level += 1
        node.then_statement.accept(self)
        self.indent_level -= 1
        
        if node.else_statement:
            self._emit("} else {")
            self.indent_level += 1
            node.else_statement.accept(self)
            self.indent_level -= 1
        
        self._emit("}")
    
    def visit_while_loop(self, node: WhileLoopNode) -> Any:
        condition_code = node.condition.accept(self)
        self._emit(f"while ({condition_code}) {{")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self._emit("}")
    
    def visit_for_loop(self, node: ForLoopNode) -> Any:
        init_code = node.initialization.accept(self) if node.initialization else ""
        condition_code = node.condition.accept(self) if node.condition else ""
        increment_code = node.increment.accept(self) if node.increment else ""
        
        self._emit(f"for ({init_code}; {condition_code}; {increment_code}) {{")
        self.indent_level += 1
        node.body.accept(self)
        self.indent_level -= 1
        self._emit("}")
    
    def visit_return_statement(self, node: ReturnStatementNode) -> Any:
        if node.value:
            value_code = node.value.accept(self)
            self._emit(f"return {value_code};")
        else:
            self._emit("return;")
    
    def visit_block_statement(self, node: BlockStatementNode) -> Any:
        for statement in node.statements:
            statement.accept(self)
    
    def visit_literal(self, node: LiteralNode) -> Any:
        if node.data_type == DataType.STRING:
            return f'"{node.value}"'
        elif node.data_type == DataType.BOOLEAN:
            return "true" if node.value else "false"
        else:
            return str(node.value)
    
    def visit_identifier(self, node: IdentifierNode) -> Any:
        return node.name
    
    def visit_array_access(self, node: ArrayAccessNode) -> Any:
        array_code = node.array.accept(self)
        index_code = node.index.accept(self)
        return f"{array_code}[{index_code}]"


class OptimizationVisitor(Visitor):
    """
    Visitor that performs code optimizations on the AST.
    """
    
    def __init__(self):
        self.optimizations_applied: List[str] = []
        self.constants: Dict[str, Any] = {}
    
    def _add_optimization(self, description: str) -> None:
        """Record an optimization that was applied."""
        self.optimizations_applied.append(description)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get report of optimizations applied."""
        return {
            "optimizations_applied": self.optimizations_applied,
            "optimization_count": len(self.optimizations_applied),
            "constants_folded": len(self.constants)
        }
    
    def visit_program(self, node: ProgramNode) -> Any:
        optimized_statements = []
        for statement in node.statements:
            result = statement.accept(self)
            if result is not None:
                optimized_statements.append(result)
        
        node.statements = optimized_statements
        return node
    
    def visit_function_declaration(self, node: FunctionDeclarationNode) -> Any:
        node.body = node.body.accept(self)
        return node
    
    def visit_variable_declaration(self, node: VariableDeclarationNode) -> Any:
        if node.initializer:
            node.initializer = node.initializer.accept(self)
            
            # Constant folding for literals
            if isinstance(node.initializer, LiteralNode):
                self.constants[node.name] = node.initializer.value
                self._add_optimization(f"Marked {node.name} as constant")
        
        return node
    
    def visit_assignment(self, node: AssignmentNode) -> Any:
        node.target = node.target.accept(self)
        node.value = node.value.accept(self)
        
        # Update constants
        if (isinstance(node.target, IdentifierNode) and 
            isinstance(node.value, LiteralNode) and
            node.operator == Operator.ASSIGN):
            self.constants[node.target.name] = node.value.value
        
        return node
    
    def visit_binary_expression(self, node: BinaryExpressionNode) -> Any:
        node.left = node.left.accept(self)
        node.right = node.right.accept(self)
        
        # Constant folding
        if (isinstance(node.left, LiteralNode) and 
            isinstance(node.right, LiteralNode)):
            
            left_val = node.left.value
            right_val = node.right.value
            
            if node.operator == Operator.ADD:
                result = left_val + right_val
            elif node.operator == Operator.SUBTRACT:
                result = left_val - right_val
            elif node.operator == Operator.MULTIPLY:
                result = left_val * right_val
            elif node.operator == Operator.DIVIDE and right_val != 0:
                result = left_val / right_val
            elif node.operator == Operator.EQUALS:
                result = left_val == right_val
            elif node.operator == Operator.LESS_THAN:
                result = left_val < right_val
            else:
                return node
            
            # Determine result type
            if isinstance(result, bool):
                result_type = DataType.BOOLEAN
            elif isinstance(result, int):
                result_type = DataType.INTEGER
            elif isinstance(result, float):
                result_type = DataType.FLOAT
            else:
                return node
            
            self._add_optimization(f"Constant folding: {left_val} {node.operator.value} {right_val} = {result}")
            return LiteralNode(result, result_type, node.line_number)
        
        # Algebraic simplifications
        if node.operator == Operator.MULTIPLY:
            # x * 0 = 0
            if ((isinstance(node.left, LiteralNode) and node.left.value == 0) or
                (isinstance(node.right, LiteralNode) and node.right.value == 0)):
                self._add_optimization("Multiplication by zero simplified to 0")
                return LiteralNode(0, DataType.INTEGER, node.line_number)
            
            # x * 1 = x
            if isinstance(node.right, LiteralNode) and node.right.value == 1:
                self._add_optimization("Multiplication by one eliminated")
                return node.left
            if isinstance(node.left, LiteralNode) and node.left.value == 1:
                self._add_optimization("Multiplication by one eliminated")
                return node.right
        
        if node.operator == Operator.ADD:
            # x + 0 = x
            if isinstance(node.right, LiteralNode) and node.right.value == 0:
                self._add_optimization("Addition of zero eliminated")
                return node.left
            if isinstance(node.left, LiteralNode) and node.left.value == 0:
                self._add_optimization("Addition of zero eliminated")
                return node.right
        
        return node
    
    def visit_unary_expression(self, node: UnaryExpressionNode) -> Any:
        node.operand = node.operand.accept(self)
        
        # Constant folding for unary expressions
        if isinstance(node.operand, LiteralNode):
            if node.operator == Operator.NOT and node.operand.data_type == DataType.BOOLEAN:
                result = not node.operand.value
                self._add_optimization(f"Constant folding: !{node.operand.value} = {result}")
                return LiteralNode(result, DataType.BOOLEAN, node.line_number)
            elif node.operator == Operator.SUBTRACT and node.operand.data_type in [DataType.INTEGER, DataType.FLOAT]:
                result = -node.operand.value
                self._add_optimization(f"Constant folding: -{node.operand.value} = {result}")
                return LiteralNode(result, node.operand.data_type, node.line_number)
        
        return node
    
    def visit_function_call(self, node: FunctionCallNode) -> Any:
        optimized_args = []
        for arg in node.arguments:
            optimized_args.append(arg.accept(self))
        node.arguments = optimized_args
        return node
    
    def visit_if_statement(self, node: IfStatementNode) -> Any:
        node.condition = node.condition.accept(self)
        
        # Dead code elimination
        if isinstance(node.condition, LiteralNode) and node.condition.data_type == DataType.BOOLEAN:
            if node.condition.value:
                # Condition is always true, replace with then statement
                self._add_optimization("Dead code elimination: if(true) replaced with then branch")
                return node.then_statement.accept(self)
            else:
                # Condition is always false, replace with else statement
                if node.else_statement:
                    self._add_optimization("Dead code elimination: if(false) replaced with else branch")
                    return node.else_statement.accept(self)
                else:
                    self._add_optimization("Dead code elimination: if(false) with no else removed")
                    return None  # Remove the entire if statement
        
        node.then_statement = node.then_statement.accept(self)
        if node.else_statement:
            node.else_statement = node.else_statement.accept(self)
        
        return node
    
    def visit_while_loop(self, node: WhileLoopNode) -> Any:
        node.condition = node.condition.accept(self)
        
        # Dead code elimination for while loops
        if (isinstance(node.condition, LiteralNode) and 
            node.condition.data_type == DataType.BOOLEAN and
            not node.condition.value):
            self._add_optimization("Dead code elimination: while(false) loop removed")
            return None
        
        node.body = node.body.accept(self)
        return node
    
    def visit_for_loop(self, node: ForLoopNode) -> Any:
        if node.initialization:
            node.initialization = node.initialization.accept(self)
        if node.condition:
            node.condition = node.condition.accept(self)
        if node.increment:
            node.increment = node.increment.accept(self)
        
        node.body = node.body.accept(self)
        return node
    
    def visit_return_statement(self, node: ReturnStatementNode) -> Any:
        if node.value:
            node.value = node.value.accept(self)
        return node
    
    def visit_block_statement(self, node: BlockStatementNode) -> Any:
        optimized_statements = []
        for statement in node.statements:
            result = statement.accept(self)
            if result is not None:
                optimized_statements.append(result)
        
        node.statements = optimized_statements
        return node
    
    def visit_literal(self, node: LiteralNode) -> Any:
        return node
    
    def visit_identifier(self, node: IdentifierNode) -> Any:
        # Constant propagation
        if node.name in self.constants:
            value = self.constants[node.name]
            if isinstance(value, bool):
                data_type = DataType.BOOLEAN
            elif isinstance(value, int):
                data_type = DataType.INTEGER
            elif isinstance(value, float):
                data_type = DataType.FLOAT
            elif isinstance(value, str):
                data_type = DataType.STRING
            else:
                return node
            
            self._add_optimization(f"Constant propagation: {node.name} replaced with {value}")
            return LiteralNode(value, data_type, node.line_number)
        
        return node
    
    def visit_array_access(self, node: ArrayAccessNode) -> Any:
        node.array = node.array.accept(self)
        node.index = node.index.accept(self)
        return node


def create_sample_ast() -> ProgramNode:
    """Create a sample AST for demonstration."""
    
    # Function: factorial(n: integer): integer
    factorial_param = [("n", DataType.INTEGER)]
    
    # if (n <= 1) return 1; else return n * factorial(n - 1);
    condition = BinaryExpressionNode(
        IdentifierNode("n", 2),
        Operator.LESS_EQUAL,
        LiteralNode(1, DataType.INTEGER, 2),
        2
    )
    
    then_stmt = ReturnStatementNode(LiteralNode(1, DataType.INTEGER, 3), 3)
    
    recursive_call = FunctionCallNode(
        "factorial",
        [BinaryExpressionNode(
            IdentifierNode("n", 4),
            Operator.SUBTRACT,
            LiteralNode(1, DataType.INTEGER, 4),
            4
        )],
        4
    )
    
    else_stmt = ReturnStatementNode(
        BinaryExpressionNode(
            IdentifierNode("n", 4),
            Operator.MULTIPLY,
            recursive_call,
            4
        ),
        4
    )
    
    if_stmt = IfStatementNode(condition, then_stmt, else_stmt, 2)
    factorial_body = BlockStatementNode([if_stmt])
    
    factorial_func = FunctionDeclarationNode(
        "factorial",
        factorial_param,
        DataType.INTEGER,
        factorial_body,
        1
    )
    
    # Variable declarations
    var_x = VariableDeclarationNode(
        "x",
        DataType.INTEGER,
        LiteralNode(5, DataType.INTEGER, 6),
        6
    )
    
    var_result = VariableDeclarationNode(
        "result",
        DataType.INTEGER,
        FunctionCallNode("factorial", [IdentifierNode("x", 7)], 7),
        7
    )
    
    # Constant expression that can be optimized
    const_expr = VariableDeclarationNode(
        "constantValue",
        DataType.INTEGER,
        BinaryExpressionNode(
            LiteralNode(10, DataType.INTEGER, 8),
            Operator.MULTIPLY,
            LiteralNode(0, DataType.INTEGER, 8),
            8
        ),
        8
    )
    
    # Program
    return ProgramNode([factorial_func, var_x, var_result, const_expr])


def main():
    """
    Demonstrate the AST Visitor System for compiler operations.
    """
    print("=== AST Visitor System Demo ===")
    
    # Create sample AST
    ast = create_sample_ast()
    print("\n🌳 Created sample AST (factorial function with variables)")
    
    # Test 1: Code Generation
    print("\n🔧 Test 1: Code Generation (JavaScript)")
    
    code_generator = CodeGeneratorVisitor("javascript")
    generated_code = ast.accept(code_generator)
    
    print("Generated JavaScript code:")
    print("=" * 50)
    print(generated_code)
    print("=" * 50)
    
    # Test 2: Static Analysis
    print("\n🔍 Test 2: Static Analysis")
    
    analyzer = StaticAnalyzerVisitor()
    analysis_report = ast.accept(analyzer)
    
    print("Static Analysis Report:")
    print(f"  Errors: {analysis_report['statistics']['total_errors']}")
    print(f"  Warnings: {analysis_report['statistics']['total_warnings']}")
    print(f"  Complexity Score: {analysis_report['statistics']['complexity_score']}")
    print(f"  Function Calls: {len(analysis_report['function_calls'])}")
    
    if analysis_report['warnings']:
        print("\nWarnings:")
        for warning in analysis_report['warnings']:
            print(f"  Line {warning['line']}: {warning['message']} ({warning['category']})")
    
    if analysis_report['errors']:
        print("\nErrors:")
        for error in analysis_report['errors']:
            print(f"  Line {error['line']}: {error['message']} ({error['category']})")
    
    print(f"\nSymbol Table:")
    for name, info in analysis_report['symbol_table'].items():
        print(f"  {name}: {info['type']} (line {info['line']})")
    
    # Test 3: Code Formatting
    print("\n🎨 Test 3: Code Formatting")
    
    formatter = CodeFormatterVisitor(indent_size=4, max_line_length=60)
    formatted_code = ast.accept(formatter)
    
    print("Formatted code:")
    print("=" * 50)
    print(formatted_code)
    print("=" * 50)
    
    # Test 4: Code Optimization
    print("\n⚡ Test 4: Code Optimization")
    
    optimizer = OptimizationVisitor()
    optimized_ast = ast.accept(optimizer)
    optimization_report = optimizer.get_optimization_report()
    
    print("Optimization Report:")
    print(f"  Optimizations applied: {optimization_report['optimization_count']}")
    print(f"  Constants folded: {optimization_report['constants_folded']}")
    
    print("\nOptimizations:")
    for optimization in optimization_report['optimizations_applied']:
        print(f"  • {optimization}")
    
    # Generate code from optimized AST
    optimized_generator = CodeGeneratorVisitor("javascript")
    optimized_code = optimized_ast.accept(optimized_generator)
    
    print("\nOptimized JavaScript code:")
    print("=" * 50)
    print(optimized_code)
    print("=" * 50)
    
    # Test 5: Creating a more complex AST with issues
    print("\n🧪 Test 5: Complex AST with Issues")
    
    # Create AST with various issues for analysis
    complex_statements = []
    
    # Unused variable
    unused_var = VariableDeclarationNode(
        "unusedVariable",
        DataType.INTEGER,
        LiteralNode(42, DataType.INTEGER, 10),
        10
    )
    complex_statements.append(unused_var)
    
    # Magic number
    magic_number_var = VariableDeclarationNode(
        "magicNumber",
        DataType.INTEGER,
        LiteralNode(3.14159, DataType.FLOAT, 11),
        11
    )
    complex_statements.append(magic_number_var)
    
    # Division by zero
    division_by_zero = VariableDeclarationNode(
        "divisionResult",
        DataType.FLOAT,
        BinaryExpressionNode(
            LiteralNode(10, DataType.INTEGER, 12),
            Operator.DIVIDE,
            LiteralNode(0, DataType.INTEGER, 12),
            12
        ),
        12
    )
    complex_statements.append(division_by_zero)
    
    # Always true condition
    always_true_if = IfStatementNode(
        LiteralNode(True, DataType.BOOLEAN, 13),
        BlockStatementNode([
            VariableDeclarationNode(
                "insideIf",
                DataType.STRING,
                LiteralNode("This will always execute", DataType.STRING, 14),
                14
            )
        ]),
        None,
        13
    )
    complex_statements.append(always_true_if)
    
    # Undefined function call
    undefined_call = FunctionCallNode(
        "undefinedFunction",
        [LiteralNode("test", DataType.STRING, 15)],
        15
    )
    complex_statements.append(undefined_call)
    
    complex_ast = ProgramNode(complex_statements)
    
    # Analyze complex AST
    complex_analyzer = StaticAnalyzerVisitor()
    complex_report = complex_ast.accept(complex_analyzer)
    
    print("Complex AST Analysis:")
    print(f"  Total errors: {complex_report['statistics']['total_errors']}")
    print(f"  Total warnings: {complex_report['statistics']['total_warnings']}")
    
    print("\nIssues found:")
    for error in complex_report['errors']:
        print(f"  ERROR Line {error['line']}: {error['message']}")
    
    for warning in complex_report['warnings']:
        print(f"  WARNING Line {warning['line']}: {warning['message']}")
    
    # Test 6: Multiple visitor passes
    print("\n🔄 Test 6: Multiple Visitor Passes")
    
    # First pass: optimization
    print("Pass 1: Optimization")
    pass1_optimizer = OptimizationVisitor()
    pass1_result = complex_ast.accept(pass1_optimizer)
    pass1_report = pass1_optimizer.get_optimization_report()
    print(f"  Optimizations in pass 1: {pass1_report['optimization_count']}")
    
    # Second pass: analysis of optimized code
    print("Pass 2: Analysis of optimized code")
    pass2_analyzer = StaticAnalyzerVisitor()
    pass2_report = pass1_result.accept(pass2_analyzer)
    print(f"  Errors after optimization: {pass2_report['statistics']['total_errors']}")
    print(f"  Warnings after optimization: {pass2_report['statistics']['total_warnings']}")
    
    # Third pass: formatting
    print("Pass 3: Code formatting")
    pass3_formatter = CodeFormatterVisitor()
    final_formatted = pass1_result.accept(pass3_formatter)
    
    print("Final formatted and optimized code:")
    print("=" * 50)
    print(final_formatted)
    print("=" * 50)
    
    # Performance comparison
    print("\n📊 Performance Summary:")
    print("Visitor Operations Performed:")
    print(f"  Code Generation: JavaScript output generated")
    print(f"  Static Analysis: {analysis_report['statistics']['total_errors'] + analysis_report['statistics']['total_warnings']} issues detected")
    print(f"  Code Formatting: Proper indentation and style applied")
    print(f"  Code Optimization: {optimization_report['optimization_count']} optimizations applied")
    print(f"  Multi-pass Processing: 3 visitor passes completed")
    
    print("\nVisitor Pattern Benefits Demonstrated:")
    print("  ✓ Separation of concerns (each visitor has single responsibility)")
    print("  ✓ Easy to add new operations without modifying AST nodes")
    print("  ✓ Clean traversal of complex tree structures")
    print("  ✓ Type-safe double dispatch pattern")
    print("  ✓ Composable operations (multiple passes)")


if __name__ == "__main__":
    main()