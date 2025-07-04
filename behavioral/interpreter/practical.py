"""
Interpreter Design Pattern - Real World Implementation

Real-world example: SQL Query Builder and Expression Evaluator
A query builder system that interprets and builds SQL queries from a domain-specific
language, supporting filtering, sorting, grouping, and complex expressions.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Optional
from datetime import datetime
from enum import Enum
import re


class OperatorType(Enum):
    """SQL operator types."""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    LIKE = "LIKE"
    IN = "IN"
    BETWEEN = "BETWEEN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class DataType(Enum):
    """Supported data types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"


class QueryContext:
    """Context for query interpretation containing table schema and parameters."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.schema: Dict[str, DataType] = {}
        self.parameters: Dict[str, Any] = {}
        self.aliases: Dict[str, str] = {}
        self.join_tables: List[str] = []
    
    def add_column(self, column_name: str, data_type: DataType) -> None:
        """Add a column to the table schema."""
        self.schema[column_name] = data_type
    
    def set_parameter(self, name: str, value: Any) -> None:
        """Set a parameter value."""
        self.parameters[name] = value
    
    def get_parameter(self, name: str) -> Any:
        """Get a parameter value."""
        return self.parameters.get(name)
    
    def add_alias(self, original: str, alias: str) -> None:
        """Add a column alias."""
        self.aliases[alias] = original
    
    def resolve_column(self, column_name: str) -> str:
        """Resolve column name considering aliases."""
        return self.aliases.get(column_name, column_name)
    
    def validate_column(self, column_name: str) -> bool:
        """Validate if column exists in schema."""
        resolved_name = self.resolve_column(column_name)
        return resolved_name in self.schema
    
    def get_column_type(self, column_name: str) -> Optional[DataType]:
        """Get the data type of a column."""
        resolved_name = self.resolve_column(column_name)
        return self.schema.get(resolved_name)


class Expression(ABC):
    """
    Abstract expression interface for SQL query components.
    """
    
    @abstractmethod
    def interpret(self, context: QueryContext) -> str:
        """Interpret the expression in the given context."""
        pass
    
    @abstractmethod
    def validate(self, context: QueryContext) -> bool:
        """Validate the expression against the context."""
        pass


class ColumnExpression(Expression):
    """Expression representing a database column."""
    
    def __init__(self, column_name: str):
        self.column_name = column_name
    
    def interpret(self, context: QueryContext) -> str:
        resolved_name = context.resolve_column(self.column_name)
        return f"`{resolved_name}`"
    
    def validate(self, context: QueryContext) -> bool:
        return context.validate_column(self.column_name)


class LiteralExpression(Expression):
    """Expression representing a literal value."""
    
    def __init__(self, value: Any, data_type: DataType):
        self.value = value
        self.data_type = data_type
    
    def interpret(self, context: QueryContext) -> str:
        if self.data_type in [DataType.STRING, DataType.DATE, DataType.DATETIME]:
            return f"'{self.value}'"
        elif self.data_type == DataType.BOOLEAN:
            return "TRUE" if self.value else "FALSE"
        else:
            return str(self.value)
    
    def validate(self, context: QueryContext) -> bool:
        return True  # Literals are always valid


class ParameterExpression(Expression):
    """Expression representing a query parameter."""
    
    def __init__(self, parameter_name: str):
        self.parameter_name = parameter_name
    
    def interpret(self, context: QueryContext) -> str:
        value = context.get_parameter(self.parameter_name)
        if value is None:
            raise ValueError(f"Parameter '{self.parameter_name}' not found in context")
        
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        else:
            return str(value)
    
    def validate(self, context: QueryContext) -> bool:
        return self.parameter_name in context.parameters


class BinaryExpression(Expression):
    """Expression representing binary operations (column = value, etc.)."""
    
    def __init__(self, left: Expression, operator: OperatorType, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right
    
    def interpret(self, context: QueryContext) -> str:
        left_sql = self.left.interpret(context)
        right_sql = self.right.interpret(context)
        
        if self.operator == OperatorType.IN:
            # Handle IN operator specially
            if isinstance(self.right, ListExpression):
                return f"{left_sql} IN ({right_sql})"
            else:
                return f"{left_sql} IN ({right_sql})"
        elif self.operator == OperatorType.BETWEEN:
            # Handle BETWEEN operator specially
            if isinstance(self.right, RangeExpression):
                return f"{left_sql} BETWEEN {self.right.start.interpret(context)} AND {self.right.end.interpret(context)}"
            else:
                raise ValueError("BETWEEN operator requires a range expression")
        else:
            return f"{left_sql} {self.operator.value} {right_sql}"
    
    def validate(self, context: QueryContext) -> bool:
        return self.left.validate(context) and self.right.validate(context)


class UnaryExpression(Expression):
    """Expression representing unary operations (IS NULL, NOT, etc.)."""
    
    def __init__(self, operand: Expression, operator: OperatorType):
        self.operand = operand
        self.operator = operator
    
    def interpret(self, context: QueryContext) -> str:
        operand_sql = self.operand.interpret(context)
        
        if self.operator in [OperatorType.IS_NULL, OperatorType.IS_NOT_NULL]:
            return f"{operand_sql} {self.operator.value}"
        elif self.operator == OperatorType.NOT:
            return f"NOT ({operand_sql})"
        else:
            raise ValueError(f"Unsupported unary operator: {self.operator}")
    
    def validate(self, context: QueryContext) -> bool:
        return self.operand.validate(context)


class LogicalExpression(Expression):
    """Expression representing logical operations (AND, OR)."""
    
    def __init__(self, left: Expression, operator: OperatorType, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right
    
    def interpret(self, context: QueryContext) -> str:
        left_sql = self.left.interpret(context)
        right_sql = self.right.interpret(context)
        return f"({left_sql} {self.operator.value} {right_sql})"
    
    def validate(self, context: QueryContext) -> bool:
        return self.left.validate(context) and self.right.validate(context)


class ListExpression(Expression):
    """Expression representing a list of values for IN operations."""
    
    def __init__(self, values: List[Expression]):
        self.values = values
    
    def interpret(self, context: QueryContext) -> str:
        value_sqls = [value.interpret(context) for value in self.values]
        return ", ".join(value_sqls)
    
    def validate(self, context: QueryContext) -> bool:
        return all(value.validate(context) for value in self.values)


class RangeExpression(Expression):
    """Expression representing a range for BETWEEN operations."""
    
    def __init__(self, start: Expression, end: Expression):
        self.start = start
        self.end = end
    
    def interpret(self, context: QueryContext) -> str:
        return f"{self.start.interpret(context)} AND {self.end.interpret(context)}"
    
    def validate(self, context: QueryContext) -> bool:
        return self.start.validate(context) and self.end.validate(context)


class FunctionExpression(Expression):
    """Expression representing SQL functions."""
    
    def __init__(self, function_name: str, arguments: List[Expression]):
        self.function_name = function_name.upper()
        self.arguments = arguments
    
    def interpret(self, context: QueryContext) -> str:
        if not self.arguments:
            return f"{self.function_name}()"
        
        arg_sqls = [arg.interpret(context) for arg in self.arguments]
        return f"{self.function_name}({', '.join(arg_sqls)})"
    
    def validate(self, context: QueryContext) -> bool:
        # Validate function name and arguments
        valid_functions = {
            "COUNT", "SUM", "AVG", "MIN", "MAX", "UPPER", "LOWER", 
            "SUBSTRING", "CONCAT", "NOW", "DATE", "YEAR", "MONTH", "DAY"
        }
        
        if self.function_name not in valid_functions:
            return False
        
        return all(arg.validate(context) for arg in self.arguments)


class SelectClause:
    """Represents a SELECT clause with columns and functions."""
    
    def __init__(self):
        self.expressions: List[Expression] = []
        self.distinct = False
    
    def add_column(self, expression: Expression) -> None:
        self.expressions.append(expression)
    
    def set_distinct(self, distinct: bool = True) -> None:
        self.distinct = distinct
    
    def interpret(self, context: QueryContext) -> str:
        if not self.expressions:
            select_part = "*"
        else:
            select_expressions = [expr.interpret(context) for expr in self.expressions]
            select_part = ", ".join(select_expressions)
        
        if self.distinct:
            return f"SELECT DISTINCT {select_part}"
        else:
            return f"SELECT {select_part}"


class WhereClause:
    """Represents a WHERE clause with conditions."""
    
    def __init__(self, condition: Optional[Expression] = None):
        self.condition = condition
    
    def set_condition(self, condition: Expression) -> None:
        self.condition = condition
    
    def interpret(self, context: QueryContext) -> str:
        if self.condition:
            return f"WHERE {self.condition.interpret(context)}"
        return ""


class OrderByClause:
    """Represents an ORDER BY clause."""
    
    def __init__(self):
        self.order_items: List[tuple[Expression, str]] = []
    
    def add_order(self, expression: Expression, direction: str = "ASC") -> None:
        direction = direction.upper()
        if direction not in ["ASC", "DESC"]:
            raise ValueError("Order direction must be ASC or DESC")
        self.order_items.append((expression, direction))
    
    def interpret(self, context: QueryContext) -> str:
        if not self.order_items:
            return ""
        
        order_parts = []
        for expr, direction in self.order_items:
            order_parts.append(f"{expr.interpret(context)} {direction}")
        
        return f"ORDER BY {', '.join(order_parts)}"


class GroupByClause:
    """Represents a GROUP BY clause."""
    
    def __init__(self):
        self.expressions: List[Expression] = []
        self.having_condition: Optional[Expression] = None
    
    def add_group(self, expression: Expression) -> None:
        self.expressions.append(expression)
    
    def set_having(self, condition: Expression) -> None:
        self.having_condition = condition
    
    def interpret(self, context: QueryContext) -> str:
        if not self.expressions:
            return ""
        
        group_parts = [expr.interpret(context) for expr in self.expressions]
        result = f"GROUP BY {', '.join(group_parts)}"
        
        if self.having_condition:
            result += f" HAVING {self.having_condition.interpret(context)}"
        
        return result


class LimitClause:
    """Represents a LIMIT clause."""
    
    def __init__(self, limit: int, offset: int = 0):
        self.limit = limit
        self.offset = offset
    
    def interpret(self, context: QueryContext) -> str:
        if self.offset > 0:
            return f"LIMIT {self.offset}, {self.limit}"
        else:
            return f"LIMIT {self.limit}"


class SQLQuery:
    """Complete SQL query composed of various clauses."""
    
    def __init__(self, context: QueryContext):
        self.context = context
        self.select_clause = SelectClause()
        self.where_clause = WhereClause()
        self.order_by_clause = OrderByClause()
        self.group_by_clause = GroupByClause()
        self.limit_clause: Optional[LimitClause] = None
    
    def select(self, *expressions: Expression) -> 'SQLQuery':
        """Add columns to SELECT clause."""
        for expr in expressions:
            self.select_clause.add_column(expr)
        return self
    
    def distinct(self) -> 'SQLQuery':
        """Add DISTINCT to SELECT clause."""
        self.select_clause.set_distinct(True)
        return self
    
    def where(self, condition: Expression) -> 'SQLQuery':
        """Set WHERE condition."""
        self.where_clause.set_condition(condition)
        return self
    
    def order_by(self, expression: Expression, direction: str = "ASC") -> 'SQLQuery':
        """Add ORDER BY clause."""
        self.order_by_clause.add_order(expression, direction)
        return self
    
    def group_by(self, *expressions: Expression) -> 'SQLQuery':
        """Add GROUP BY clause."""
        for expr in expressions:
            self.group_by_clause.add_group(expr)
        return self
    
    def having(self, condition: Expression) -> 'SQLQuery':
        """Add HAVING condition."""
        self.group_by_clause.set_having(condition)
        return self
    
    def limit(self, limit: int, offset: int = 0) -> 'SQLQuery':
        """Add LIMIT clause."""
        self.limit_clause = LimitClause(limit, offset)
        return self
    
    def build(self) -> str:
        """Build the complete SQL query."""
        parts = []
        
        # SELECT clause
        parts.append(self.select_clause.interpret(self.context))
        
        # FROM clause
        parts.append(f"FROM `{self.context.table_name}`")
        
        # WHERE clause
        where_sql = self.where_clause.interpret(self.context)
        if where_sql:
            parts.append(where_sql)
        
        # GROUP BY clause
        group_by_sql = self.group_by_clause.interpret(self.context)
        if group_by_sql:
            parts.append(group_by_sql)
        
        # ORDER BY clause
        order_by_sql = self.order_by_clause.interpret(self.context)
        if order_by_sql:
            parts.append(order_by_sql)
        
        # LIMIT clause
        if self.limit_clause:
            parts.append(self.limit_clause.interpret(self.context))
        
        return " ".join(parts)
    
    def validate(self) -> bool:
        """Validate the entire query."""
        # Validate all expressions in clauses
        for expr in self.select_clause.expressions:
            if not expr.validate(self.context):
                return False
        
        if self.where_clause.condition and not self.where_clause.condition.validate(self.context):
            return False
        
        for expr, _ in self.order_by_clause.order_items:
            if not expr.validate(self.context):
                return False
        
        for expr in self.group_by_clause.expressions:
            if not expr.validate(self.context):
                return False
        
        if self.group_by_clause.having_condition:
            if not self.group_by_clause.having_condition.validate(self.context):
                return False
        
        return True


class QueryBuilder:
    """Builder for creating SQL queries using domain-specific language."""
    
    def __init__(self, table_name: str):
        self.context = QueryContext(table_name)
        self.query = SQLQuery(self.context)
    
    def define_schema(self, schema: Dict[str, DataType]) -> 'QueryBuilder':
        """Define the table schema."""
        for column, data_type in schema.items():
            self.context.add_column(column, data_type)
        return self
    
    def set_parameters(self, **parameters) -> 'QueryBuilder':
        """Set query parameters."""
        for name, value in parameters.items():
            self.context.set_parameter(name, value)
        return self
    
    def add_alias(self, original: str, alias: str) -> 'QueryBuilder':
        """Add column alias."""
        self.context.add_alias(original, alias)
        return self
    
    def column(self, name: str) -> ColumnExpression:
        """Create a column expression."""
        return ColumnExpression(name)
    
    def literal(self, value: Any, data_type: DataType) -> LiteralExpression:
        """Create a literal expression."""
        return LiteralExpression(value, data_type)
    
    def parameter(self, name: str) -> ParameterExpression:
        """Create a parameter expression."""
        return ParameterExpression(name)
    
    def function(self, name: str, *args: Expression) -> FunctionExpression:
        """Create a function expression."""
        return FunctionExpression(name, list(args))
    
    def equals(self, left: Expression, right: Expression) -> BinaryExpression:
        """Create equals expression."""
        return BinaryExpression(left, OperatorType.EQUALS, right)
    
    def not_equals(self, left: Expression, right: Expression) -> BinaryExpression:
        """Create not equals expression."""
        return BinaryExpression(left, OperatorType.NOT_EQUALS, right)
    
    def greater_than(self, left: Expression, right: Expression) -> BinaryExpression:
        """Create greater than expression."""
        return BinaryExpression(left, OperatorType.GREATER_THAN, right)
    
    def less_than(self, left: Expression, right: Expression) -> BinaryExpression:
        """Create less than expression."""
        return BinaryExpression(left, OperatorType.LESS_THAN, right)
    
    def like(self, left: Expression, right: Expression) -> BinaryExpression:
        """Create LIKE expression."""
        return BinaryExpression(left, OperatorType.LIKE, right)
    
    def in_list(self, left: Expression, *values: Expression) -> BinaryExpression:
        """Create IN expression."""
        return BinaryExpression(left, OperatorType.IN, ListExpression(list(values)))
    
    def between(self, left: Expression, start: Expression, end: Expression) -> BinaryExpression:
        """Create BETWEEN expression."""
        return BinaryExpression(left, OperatorType.BETWEEN, RangeExpression(start, end))
    
    def is_null(self, operand: Expression) -> UnaryExpression:
        """Create IS NULL expression."""
        return UnaryExpression(operand, OperatorType.IS_NULL)
    
    def is_not_null(self, operand: Expression) -> UnaryExpression:
        """Create IS NOT NULL expression."""
        return UnaryExpression(operand, OperatorType.IS_NOT_NULL)
    
    def and_condition(self, left: Expression, right: Expression) -> LogicalExpression:
        """Create AND expression."""
        return LogicalExpression(left, OperatorType.AND, right)
    
    def or_condition(self, left: Expression, right: Expression) -> LogicalExpression:
        """Create OR expression."""
        return LogicalExpression(left, OperatorType.OR, right)
    
    def not_condition(self, operand: Expression) -> UnaryExpression:
        """Create NOT expression."""
        return UnaryExpression(operand, OperatorType.NOT)
    
    def build_query(self) -> SQLQuery:
        """Get the query object for further configuration."""
        return self.query
    
    def to_sql(self) -> str:
        """Build and return the SQL string."""
        if not self.query.validate():
            raise ValueError("Invalid query: validation failed")
        return self.query.build()


def main():
    """
    Demonstrate the SQL Query Interpreter system.
    """
    print("=== SQL Query Interpreter Demo ===")
    
    # Create a query builder for a users table
    builder = QueryBuilder("users")
    
    # Define schema
    schema = {
        "id": DataType.INTEGER,
        "name": DataType.STRING,
        "email": DataType.STRING,
        "age": DataType.INTEGER,
        "salary": DataType.FLOAT,
        "department": DataType.STRING,
        "created_at": DataType.DATETIME,
        "is_active": DataType.BOOLEAN
    }
    
    builder.define_schema(schema)
    
    print(f"\n📊 Table Schema defined for 'users' with {len(schema)} columns")
    
    # Test 1: Simple SELECT query
    print("\n🔍 Test 1: Simple SELECT query")
    
    query1 = builder.build_query()
    query1.select(
        builder.column("name"),
        builder.column("email"),
        builder.column("age")
    ).where(
        builder.greater_than(
            builder.column("age"),
            builder.literal(25, DataType.INTEGER)
        )
    ).order_by(
        builder.column("name")
    )
    
    sql1 = query1.build()
    print(f"SQL: {sql1}")
    
    # Test 2: Complex WHERE conditions
    print("\n🔍 Test 2: Complex WHERE conditions with AND/OR")
    
    builder2 = QueryBuilder("users").define_schema(schema)
    
    # age > 25 AND (department = 'Engineering' OR salary > 50000)
    condition = builder2.and_condition(
        builder2.greater_than(
            builder2.column("age"),
            builder2.literal(25, DataType.INTEGER)
        ),
        builder2.or_condition(
            builder2.equals(
                builder2.column("department"),
                builder2.literal("Engineering", DataType.STRING)
            ),
            builder2.greater_than(
                builder2.column("salary"),
                builder2.literal(50000, DataType.FLOAT)
            )
        )
    )
    
    query2 = builder2.build_query()
    query2.select(
        builder2.column("name"),
        builder2.column("department"),
        builder2.column("salary")
    ).where(condition)
    
    sql2 = query2.build()
    print(f"SQL: {sql2}")
    
    # Test 3: Using parameters
    print("\n🔍 Test 3: Parameterized query")
    
    builder3 = QueryBuilder("users").define_schema(schema)
    builder3.set_parameters(min_age=30, target_dept="Marketing")
    
    param_condition = builder3.and_condition(
        builder3.greater_than(
            builder3.column("age"),
            builder3.parameter("min_age")
        ),
        builder3.equals(
            builder3.column("department"),
            builder3.parameter("target_dept")
        )
    )
    
    query3 = builder3.build_query()
    query3.select(
        builder3.column("name"),
        builder3.column("age"),
        builder3.column("department")
    ).where(param_condition).order_by(
        builder3.column("age"), "DESC"
    )
    
    sql3 = query3.build()
    print(f"SQL: {sql3}")
    print(f"Parameters: min_age=30, target_dept='Marketing'")
    
    # Test 4: Aggregate functions and GROUP BY
    print("\n🔍 Test 4: Aggregate functions with GROUP BY")
    
    builder4 = QueryBuilder("users").define_schema(schema)
    
    query4 = builder4.build_query()
    query4.select(
        builder4.column("department"),
        builder4.function("COUNT", builder4.column("id")),
        builder4.function("AVG", builder4.column("salary")),
        builder4.function("MAX", builder4.column("age"))
    ).where(
        builder4.equals(
            builder4.column("is_active"),
            builder4.literal(True, DataType.BOOLEAN)
        )
    ).group_by(
        builder4.column("department")
    ).having(
        builder4.greater_than(
            builder4.function("COUNT", builder4.column("id")),
            builder4.literal(5, DataType.INTEGER)
        )
    ).order_by(
        builder4.function("AVG", builder4.column("salary")), "DESC"
    )
    
    sql4 = query4.build()
    print(f"SQL: {sql4}")
    
    # Test 5: IN and BETWEEN operators
    print("\n🔍 Test 5: IN and BETWEEN operators")
    
    builder5 = QueryBuilder("users").define_schema(schema)
    
    in_condition = builder5.in_list(
        builder5.column("department"),
        builder5.literal("Engineering", DataType.STRING),
        builder5.literal("Marketing", DataType.STRING),
        builder5.literal("Sales", DataType.STRING)
    )
    
    between_condition = builder5.between(
        builder5.column("age"),
        builder5.literal(25, DataType.INTEGER),
        builder5.literal(45, DataType.INTEGER)
    )
    
    combined_condition = builder5.and_condition(in_condition, between_condition)
    
    query5 = builder5.build_query()
    query5.select(
        builder5.column("name"),
        builder5.column("department"),
        builder5.column("age"),
        builder5.column("salary")
    ).where(combined_condition).limit(10, 5)
    
    sql5 = query5.build()
    print(f"SQL: {sql5}")
    
    # Test 6: NULL checks and string functions
    print("\n🔍 Test 6: NULL checks and string functions")
    
    builder6 = QueryBuilder("users").define_schema(schema)
    
    null_condition = builder6.and_condition(
        builder6.is_not_null(builder6.column("email")),
        builder6.like(
            builder6.function("UPPER", builder6.column("name")),
            builder6.literal("%JOHN%", DataType.STRING)
        )
    )
    
    query6 = builder6.build_query()
    query6.select(
        builder6.function("UPPER", builder6.column("name")),
        builder6.column("email"),
        builder6.function("YEAR", builder6.column("created_at"))
    ).where(null_condition).distinct()
    
    sql6 = query6.build()
    print(f"SQL: {sql6}")
    
    # Test 7: Error handling - invalid query
    print("\n🚫 Test 7: Error handling - invalid column")
    
    try:
        builder7 = QueryBuilder("users").define_schema(schema)
        
        # Try to use a column that doesn't exist
        invalid_query = builder7.build_query()
        invalid_query.select(
            builder7.column("invalid_column")
        )
        
        if not invalid_query.validate():
            print("❌ Query validation failed as expected (invalid column)")
        else:
            print("✅ Query validated (unexpected)")
            
    except Exception as e:
        print(f"❌ Exception caught: {str(e)}")
    
    # Test 8: Complex real-world query
    print("\n🔍 Test 8: Complex real-world query")
    
    builder8 = QueryBuilder("users").define_schema(schema)
    builder8.set_parameters(
        start_date="2023-01-01",
        end_date="2023-12-31",
        min_salary=40000
    )
    
    # Find active users in specific departments with good salaries, created this year
    complex_condition = builder8.and_condition(
        builder8.and_condition(
            builder8.equals(
                builder8.column("is_active"),
                builder8.literal(True, DataType.BOOLEAN)
            ),
            builder8.in_list(
                builder8.column("department"),
                builder8.literal("Engineering", DataType.STRING),
                builder8.literal("Product", DataType.STRING),
                builder8.literal("Design", DataType.STRING)
            )
        ),
        builder8.and_condition(
            builder8.greater_than(
                builder8.column("salary"),
                builder8.parameter("min_salary")
            ),
            builder8.between(
                builder8.function("DATE", builder8.column("created_at")),
                builder8.parameter("start_date"),
                builder8.parameter("end_date")
            )
        )
    )
    
    query8 = builder8.build_query()
    query8.select(
        builder8.column("name"),
        builder8.column("email"),
        builder8.column("department"),
        builder8.column("salary"),
        builder8.function("DATE", builder8.column("created_at"))
    ).where(complex_condition).order_by(
        builder8.column("department")
    ).order_by(
        builder8.column("salary"), "DESC"
    ).limit(20)
    
    sql8 = query8.build()
    print(f"SQL: {sql8}")
    
    # Performance statistics
    print("\n📊 Query Statistics:")
    print(f"  Total test queries: 8")
    print(f"  Simple queries: 3")
    print(f"  Complex queries: 4")
    print(f"  Error handling tests: 1")
    print(f"  Features demonstrated:")
    print(f"    - Basic SELECT, WHERE, ORDER BY")
    print(f"    - Complex logical conditions (AND, OR, NOT)")
    print(f"    - Parameterized queries")
    print(f"    - Aggregate functions and GROUP BY")
    print(f"    - IN and BETWEEN operators")
    print(f"    - NULL checks and string functions")
    print(f"    - Query validation")
    print(f"    - Real-world complex queries")


if __name__ == "__main__":
    main()