"""
Visitor Design Pattern - Gang of Four Implementation

Intent: Represent an operation to be performed on the elements of an object structure.
Visitor lets you define a new operation without changing the classes of the elements
on which it operates.

Structure:
- Visitor: declares a Visit operation for each class of ConcreteElement
- ConcreteVisitor: implements each operation declared by Visitor
- Element: defines an Accept operation that takes a visitor as an argument
- ConcreteElement: implements an Accept operation that takes a visitor as an argument
"""

from abc import ABC, abstractmethod
from typing import List, Any, Union


class Visitor(ABC):
    """
    The Visitor Interface declares a set of visiting methods that correspond to
    component classes. The signature of a visiting method allows the visitor to
    identify the exact class of the component that it's dealing with.
    """
    
    @abstractmethod
    def visit_concrete_component_a(self, element: 'ConcreteComponentA') -> str:
        pass
    
    @abstractmethod
    def visit_concrete_component_b(self, element: 'ConcreteComponentB') -> str:
        pass


class Component(ABC):
    """
    The Component interface declares an `accept` method that should take the
    base visitor interface as an argument.
    """
    
    @abstractmethod
    def accept(self, visitor: Visitor) -> str:
        pass


class ConcreteComponentA(Component):
    """
    Each Concrete Component must implement the `Accept` method in such a way
    that it calls the visitor's method corresponding to the component's class.
    """
    
    def accept(self, visitor: Visitor) -> str:
        """
        Note that we're calling `visit_concrete_component_a`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """
        return visitor.visit_concrete_component_a(self)
    
    def exclusive_method_of_concrete_component_a(self) -> str:
        """
        Concrete Components may have special methods that don't exist in their
        base class or interface. The Visitor is still able to use these methods
        since it's aware of the component's concrete class.
        """
        return "A"


class ConcreteComponentB(Component):
    """
    Same here: visit_concrete_component_b => ConcreteComponentB
    """
    
    def accept(self, visitor: Visitor) -> str:
        return visitor.visit_concrete_component_b(self)
    
    def special_method_of_concrete_component_b(self) -> str:
        """
        Concrete Components may have special methods that don't exist in their
        base class or interface. The Visitor is still able to use these methods
        since it's aware of the component's concrete class.
        """
        return "B"


class ConcreteVisitor1(Visitor):
    """
    Concrete Visitors implement several versions of the same algorithm, which
    can work with all concrete component classes.

    You can experience the biggest benefit of the Visitor pattern when using it
    with a complex object structure, such as a Composite tree. In this case, it
    might be helpful to store some intermediate state of the algorithm while
    executing visitor's methods over various objects of the structure.
    """
    
    def visit_concrete_component_a(self, element: ConcreteComponentA) -> str:
        return f"{element.exclusive_method_of_concrete_component_a()} + ConcreteVisitor1"
    
    def visit_concrete_component_b(self, element: ConcreteComponentB) -> str:
        return f"{element.special_method_of_concrete_component_b()} + ConcreteVisitor1"


class ConcreteVisitor2(Visitor):
    """
    Another concrete visitor implementing a different algorithm.
    """
    
    def visit_concrete_component_a(self, element: ConcreteComponentA) -> str:
        return f"{element.exclusive_method_of_concrete_component_a()} + ConcreteVisitor2"
    
    def visit_concrete_component_b(self, element: ConcreteComponentB) -> str:
        return f"{element.special_method_of_concrete_component_b()} + ConcreteVisitor2"


def client_code(components: List[Component], visitor: Visitor) -> None:
    """
    The client code can run visitor operations over any set of elements without
    figuring out their concrete classes. The accept operation directs a call to
    the appropriate operation in the visitor object.
    """
    results = []
    for component in components:
        result = component.accept(visitor)
        results.append(result)
    
    print(f"Results: {results}")


# More practical example: Document structure
class DocumentElement(ABC):
    """
    Abstract base class for document elements.
    """
    
    @abstractmethod
    def accept(self, visitor: 'DocumentVisitor') -> Any:
        pass


class Paragraph(DocumentElement):
    """
    Paragraph element.
    """
    
    def __init__(self, text: str):
        self.text = text
    
    def accept(self, visitor: 'DocumentVisitor') -> Any:
        return visitor.visit_paragraph(self)


class Header(DocumentElement):
    """
    Header element.
    """
    
    def __init__(self, text: str, level: int):
        self.text = text
        self.level = level
    
    def accept(self, visitor: 'DocumentVisitor') -> Any:
        return visitor.visit_header(self)


class Image(DocumentElement):
    """
    Image element.
    """
    
    def __init__(self, src: str, alt: str, width: int, height: int):
        self.src = src
        self.alt = alt
        self.width = width
        self.height = height
    
    def accept(self, visitor: 'DocumentVisitor') -> Any:
        return visitor.visit_image(self)


class Table(DocumentElement):
    """
    Table element.
    """
    
    def __init__(self, rows: List[List[str]]):
        self.rows = rows
    
    def accept(self, visitor: 'DocumentVisitor') -> Any:
        return visitor.visit_table(self)
    
    def get_cell_count(self) -> int:
        return sum(len(row) for row in self.rows)


class Document:
    """
    Document containing multiple elements.
    """
    
    def __init__(self):
        self.elements: List[DocumentElement] = []
    
    def add_element(self, element: DocumentElement) -> None:
        self.elements.append(element)
    
    def accept(self, visitor: 'DocumentVisitor') -> Any:
        results = []
        for element in self.elements:
            result = element.accept(visitor)
            if result is not None:
                results.append(result)
        return results


class DocumentVisitor(ABC):
    """
    Abstract visitor for document elements.
    """
    
    @abstractmethod
    def visit_paragraph(self, paragraph: Paragraph) -> Any:
        pass
    
    @abstractmethod
    def visit_header(self, header: Header) -> Any:
        pass
    
    @abstractmethod
    def visit_image(self, image: Image) -> Any:
        pass
    
    @abstractmethod
    def visit_table(self, table: Table) -> Any:
        pass


class HTMLExporter(DocumentVisitor):
    """
    Visitor that exports document to HTML.
    """
    
    def visit_paragraph(self, paragraph: Paragraph) -> str:
        return f"<p>{paragraph.text}</p>"
    
    def visit_header(self, header: Header) -> str:
        return f"<h{header.level}>{header.text}</h{header.level}>"
    
    def visit_image(self, image: Image) -> str:
        return f'<img src="{image.src}" alt="{image.alt}" width="{image.width}" height="{image.height}">'
    
    def visit_table(self, table: Table) -> str:
        html = "<table>"
        for row in table.rows:
            html += "<tr>"
            for cell in row:
                html += f"<td>{cell}</td>"
            html += "</tr>"
        html += "</table>"
        return html


class MarkdownExporter(DocumentVisitor):
    """
    Visitor that exports document to Markdown.
    """
    
    def visit_paragraph(self, paragraph: Paragraph) -> str:
        return f"{paragraph.text}\n"
    
    def visit_header(self, header: Header) -> str:
        return f"{'#' * header.level} {header.text}\n"
    
    def visit_image(self, image: Image) -> str:
        return f"![{image.alt}]({image.src})\n"
    
    def visit_table(self, table: Table) -> str:
        if not table.rows:
            return ""
        
        markdown = ""
        # Header row
        if table.rows:
            markdown += "| " + " | ".join(table.rows[0]) + " |\n"
            markdown += "| " + " | ".join(["---"] * len(table.rows[0])) + " |\n"
            
            # Data rows
            for row in table.rows[1:]:
                markdown += "| " + " | ".join(row) + " |\n"
        
        return markdown


class WordCountVisitor(DocumentVisitor):
    """
    Visitor that counts words in the document.
    """
    
    def __init__(self):
        self.word_count = 0
    
    def visit_paragraph(self, paragraph: Paragraph) -> None:
        self.word_count += len(paragraph.text.split())
    
    def visit_header(self, header: Header) -> None:
        self.word_count += len(header.text.split())
    
    def visit_image(self, image: Image) -> None:
        # Count alt text words
        self.word_count += len(image.alt.split())
    
    def visit_table(self, table: Table) -> None:
        for row in table.rows:
            for cell in row:
                self.word_count += len(cell.split())
    
    def get_word_count(self) -> int:
        return self.word_count


class StatisticsVisitor(DocumentVisitor):
    """
    Visitor that collects document statistics.
    """
    
    def __init__(self):
        self.stats = {
            "paragraphs": 0,
            "headers": 0,
            "images": 0,
            "tables": 0,
            "total_elements": 0,
            "header_levels": {},
            "image_sizes": [],
            "table_cells": 0
        }
    
    def visit_paragraph(self, paragraph: Paragraph) -> None:
        self.stats["paragraphs"] += 1
        self.stats["total_elements"] += 1
    
    def visit_header(self, header: Header) -> None:
        self.stats["headers"] += 1
        self.stats["total_elements"] += 1
        
        level = header.level
        if level in self.stats["header_levels"]:
            self.stats["header_levels"][level] += 1
        else:
            self.stats["header_levels"][level] = 1
    
    def visit_image(self, image: Image) -> None:
        self.stats["images"] += 1
        self.stats["total_elements"] += 1
        self.stats["image_sizes"].append((image.width, image.height))
    
    def visit_table(self, table: Table) -> None:
        self.stats["tables"] += 1
        self.stats["total_elements"] += 1
        self.stats["table_cells"] += table.get_cell_count()
    
    def get_statistics(self) -> dict:
        return self.stats.copy()


# Expression tree example
class Expression(ABC):
    """
    Abstract expression for mathematical expressions.
    """
    
    @abstractmethod
    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        pass


class Number(Expression):
    """
    Number expression.
    """
    
    def __init__(self, value: float):
        self.value = value
    
    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        return visitor.visit_number(self)


class BinaryOperation(Expression):
    """
    Binary operation expression.
    """
    
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        return visitor.visit_binary_operation(self)


class UnaryOperation(Expression):
    """
    Unary operation expression.
    """
    
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand
    
    def accept(self, visitor: 'ExpressionVisitor') -> Any:
        return visitor.visit_unary_operation(self)


class ExpressionVisitor(ABC):
    """
    Abstract visitor for expressions.
    """
    
    @abstractmethod
    def visit_number(self, number: Number) -> Any:
        pass
    
    @abstractmethod
    def visit_binary_operation(self, operation: BinaryOperation) -> Any:
        pass
    
    @abstractmethod
    def visit_unary_operation(self, operation: UnaryOperation) -> Any:
        pass


class ExpressionEvaluator(ExpressionVisitor):
    """
    Visitor that evaluates expressions.
    """
    
    def visit_number(self, number: Number) -> float:
        return number.value
    
    def visit_binary_operation(self, operation: BinaryOperation) -> float:
        left_val = operation.left.accept(self)
        right_val = operation.right.accept(self)
        
        if operation.operator == "+":
            return left_val + right_val
        elif operation.operator == "-":
            return left_val - right_val
        elif operation.operator == "*":
            return left_val * right_val
        elif operation.operator == "/":
            if right_val == 0:
                raise ValueError("Division by zero")
            return left_val / right_val
        else:
            raise ValueError(f"Unknown operator: {operation.operator}")
    
    def visit_unary_operation(self, operation: UnaryOperation) -> float:
        operand_val = operation.operand.accept(self)
        
        if operation.operator == "-":
            return -operand_val
        elif operation.operator == "+":
            return operand_val
        else:
            raise ValueError(f"Unknown unary operator: {operation.operator}")


class ExpressionPrinter(ExpressionVisitor):
    """
    Visitor that prints expressions in infix notation.
    """
    
    def visit_number(self, number: Number) -> str:
        return str(number.value)
    
    def visit_binary_operation(self, operation: BinaryOperation) -> str:
        left_str = operation.left.accept(self)
        right_str = operation.right.accept(self)
        return f"({left_str} {operation.operator} {right_str})"
    
    def visit_unary_operation(self, operation: UnaryOperation) -> str:
        operand_str = operation.operand.accept(self)
        return f"{operation.operator}{operand_str}"


class ExpressionPostfixPrinter(ExpressionVisitor):
    """
    Visitor that prints expressions in postfix notation.
    """
    
    def visit_number(self, number: Number) -> str:
        return str(number.value)
    
    def visit_binary_operation(self, operation: BinaryOperation) -> str:
        left_str = operation.left.accept(self)
        right_str = operation.right.accept(self)
        return f"{left_str} {right_str} {operation.operator}"
    
    def visit_unary_operation(self, operation: UnaryOperation) -> str:
        operand_str = operation.operand.accept(self)
        return f"{operand_str} {operation.operator}"


def main():
    """
    The client code demonstrates the Visitor pattern.
    """
    print("=== Visitor Pattern Demo ===")
    
    # Basic visitor pattern
    print("\n1. Basic Visitor Pattern:")
    
    components = [ConcreteComponentA(), ConcreteComponentB()]
    
    print("The client code works with all visitors via the base Visitor interface:")
    visitor1 = ConcreteVisitor1()
    client_code(components, visitor1)
    
    print("It allows the same client code to work with different types of visitors:")
    visitor2 = ConcreteVisitor2()
    client_code(components, visitor2)
    
    # Document processing example
    print("\n2. Document Processing Visitor:")
    
    # Create a document
    doc = Document()
    doc.add_element(Header("Introduction", 1))
    doc.add_element(Paragraph("This is the introduction paragraph."))
    doc.add_element(Header("Main Content", 2))
    doc.add_element(Paragraph("This is the main content paragraph."))
    doc.add_element(Image("image.jpg", "Sample image", 300, 200))
    doc.add_element(Table([
        ["Name", "Age", "City"],
        ["Alice", "25", "New York"],
        ["Bob", "30", "San Francisco"]
    ]))
    
    # Export to HTML
    print("HTML Export:")
    html_exporter = HTMLExporter()
    html_results = doc.accept(html_exporter)
    for result in html_results:
        print(f"  {result}")
    
    # Export to Markdown
    print("\nMarkdown Export:")
    markdown_exporter = MarkdownExporter()
    markdown_results = doc.accept(markdown_exporter)
    for result in markdown_results:
        print(f"  {result.strip()}")
    
    # Count words
    print("\nWord Count:")
    word_counter = WordCountVisitor()
    doc.accept(word_counter)
    print(f"  Total words: {word_counter.get_word_count()}")
    
    # Collect statistics
    print("\nDocument Statistics:")
    stats_visitor = StatisticsVisitor()
    doc.accept(stats_visitor)
    stats = stats_visitor.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Expression evaluation example
    print("\n3. Expression Evaluation Visitor:")
    
    # Create expression: (5 + 3) * 2 - (-1)
    expr = BinaryOperation(
        BinaryOperation(
            Number(5),
            "+",
            Number(3)
        ),
        "*",
        BinaryOperation(
            Number(2),
            "-",
            UnaryOperation("-", Number(1))
        )
    )
    
    # Evaluate expression
    evaluator = ExpressionEvaluator()
    result = expr.accept(evaluator)
    print(f"Expression result: {result}")
    
    # Print expression in different formats
    infix_printer = ExpressionPrinter()
    infix_result = expr.accept(infix_printer)
    print(f"Infix notation: {infix_result}")
    
    postfix_printer = ExpressionPostfixPrinter()
    postfix_result = expr.accept(postfix_printer)
    print(f"Postfix notation: {postfix_result}")
    
    # More complex expression: ((10 / 2) + 3) * (4 - 1)
    complex_expr = BinaryOperation(
        BinaryOperation(
            BinaryOperation(Number(10), "/", Number(2)),
            "+",
            Number(3)
        ),
        "*",
        BinaryOperation(Number(4), "-", Number(1))
    )
    
    print(f"\nComplex expression:")
    complex_result = complex_expr.accept(evaluator)
    complex_infix = complex_expr.accept(infix_printer)
    complex_postfix = complex_expr.accept(postfix_printer)
    
    print(f"  Infix: {complex_infix}")
    print(f"  Postfix: {complex_postfix}")
    print(f"  Result: {complex_result}")
    
    # Demonstrate visitor pattern benefits
    print("\n4. Adding New Operations (Visitor Pattern Benefits):")
    
    # We can add new operations without modifying existing classes
    class ExpressionVariableCounter(ExpressionVisitor):
        """Count the number of variables/numbers in an expression."""
        
        def __init__(self):
            self.count = 0
        
        def visit_number(self, number: Number) -> None:
            self.count += 1
        
        def visit_binary_operation(self, operation: BinaryOperation) -> None:
            operation.left.accept(self)
            operation.right.accept(self)
        
        def visit_unary_operation(self, operation: UnaryOperation) -> None:
            operation.operand.accept(self)
        
        def get_count(self) -> int:
            return self.count
    
    variable_counter = ExpressionVariableCounter()
    complex_expr.accept(variable_counter)
    print(f"Number of operands in complex expression: {variable_counter.get_count()}")
    
    # Another new operation
    class ExpressionDepthCalculator(ExpressionVisitor):
        """Calculate the depth of an expression tree."""
        
        def visit_number(self, number: Number) -> int:
            return 1
        
        def visit_binary_operation(self, operation: BinaryOperation) -> int:
            left_depth = operation.left.accept(self)
            right_depth = operation.right.accept(self)
            return 1 + max(left_depth, right_depth)
        
        def visit_unary_operation(self, operation: UnaryOperation) -> int:
            return 1 + operation.operand.accept(self)
    
    depth_calculator = ExpressionDepthCalculator()
    depth = complex_expr.accept(depth_calculator)
    print(f"Depth of complex expression: {depth}")


if __name__ == "__main__":
    main()