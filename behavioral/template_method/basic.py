"""
Template Method Design Pattern - Gang of Four Implementation

Intent: Define the skeleton of an algorithm in the base class, letting subclasses
override specific steps of the algorithm without changing its structure.

Structure:
- AbstractClass: defines abstract primitive operations that concrete subclasses implement
- ConcreteClass: implements the primitive operations to carry out subclass-specific steps
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class AbstractClass(ABC):
    """
    The Abstract Class defines a template method that contains a skeleton of
    some algorithm, composed of calls to (usually) abstract primitive operations.

    Concrete subclasses should implement these operations, but leave the
    template method itself intact.
    """
    
    def template_method(self) -> str:
        """
        The template method defines the skeleton of an algorithm.
        """
        result = []
        result.append("AbstractClass: Template method executing...")
        result.append(self.base_operation1())
        result.append(self.required_operation1())
        result.append(self.base_operation2())
        result.append(self.hook1())
        result.append(self.required_operation2())
        result.append(self.base_operation3())
        result.append(self.hook2())
        
        return "\n".join(result)
    
    # These operations already have implementations.
    def base_operation1(self) -> str:
        return "AbstractClass: I am doing the bulk of the work"
    
    def base_operation2(self) -> str:
        return "AbstractClass: But I let subclasses override some operations"
    
    def base_operation3(self) -> str:
        return "AbstractClass: But I am doing the bulk of the work anyway"
    
    # These operations have to be implemented in subclasses.
    @abstractmethod
    def required_operation1(self) -> str:
        pass
    
    @abstractmethod
    def required_operation2(self) -> str:
        pass
    
    # These are "hooks." Subclasses may override them, but it's not mandatory
    # since the hooks already have default (but empty) implementation. Hooks
    # provide additional extension points in some crucial places of the
    # algorithm.
    def hook1(self) -> str:
        return ""
    
    def hook2(self) -> str:
        return ""


class ConcreteClass1(AbstractClass):
    """
    Concrete classes have to implement all abstract operations of the base
    class. They can also override some operations with a default implementation.
    """
    
    def required_operation1(self) -> str:
        return "ConcreteClass1: Implemented Operation1"
    
    def required_operation2(self) -> str:
        return "ConcreteClass1: Implemented Operation2"


class ConcreteClass2(AbstractClass):
    """
    Usually, concrete classes override only a fraction of base class'
    operations.
    """
    
    def required_operation1(self) -> str:
        return "ConcreteClass2: Implemented Operation1"
    
    def required_operation2(self) -> str:
        return "ConcreteClass2: Implemented Operation2"
    
    def hook1(self) -> str:
        return "ConcreteClass2: Overridden Hook1"


# More practical example: Data mining
class DataMiner(ABC):
    """
    Abstract class that defines the template for data mining algorithms.
    """
    
    def mine_data(self, path: str) -> str:
        """
        Template method that defines the data mining process.
        """
        results = []
        results.append("Data Mining Process Started...")
        
        # Open file
        file_data = self.open_file(path)
        results.append(f"File opened: {file_data}")
        
        # Extract data
        raw_data = self.extract_data(file_data)
        results.append(f"Data extracted: {raw_data}")
        
        # Parse data
        parsed_data = self.parse_data(raw_data)
        results.append(f"Data parsed: {parsed_data}")
        
        # Analyze data
        analysis = self.analyze_data(parsed_data)
        results.append(f"Analysis: {analysis}")
        
        # Send report (hook - optional)
        report = self.send_report(analysis)
        if report:
            results.append(f"Report: {report}")
        
        # Close file
        close_result = self.close_file(file_data)
        results.append(f"File closed: {close_result}")
        
        results.append("Data Mining Process Completed!")
        return "\n".join(results)
    
    def open_file(self, path: str) -> str:
        """
        Common operation - same for all file types.
        """
        return f"Opening file: {path}"
    
    def close_file(self, file_data: str) -> str:
        """
        Common operation - same for all file types.
        """
        return "File closed successfully"
    
    @abstractmethod
    def extract_data(self, file_data: str) -> str:
        """
        Abstract method - must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def parse_data(self, raw_data: str) -> str:
        """
        Abstract method - must be implemented by subclasses.
        """
        pass
    
    def analyze_data(self, data: str) -> str:
        """
        Default analysis - can be overridden by subclasses.
        """
        return f"Basic analysis of: {data}"
    
    def send_report(self, analysis: str) -> Optional[str]:
        """
        Hook method - optional implementation.
        """
        return None


class PDFDataMiner(DataMiner):
    """
    Concrete implementation for PDF files.
    """
    
    def extract_data(self, file_data: str) -> str:
        return f"Extracting PDF data from: {file_data}"
    
    def parse_data(self, raw_data: str) -> str:
        return f"Parsing PDF data: {raw_data} -> Structured PDF content"
    
    def analyze_data(self, data: str) -> str:
        return f"PDF Analysis: Text patterns and document structure in {data}"


class CSVDataMiner(DataMiner):
    """
    Concrete implementation for CSV files.
    """
    
    def extract_data(self, file_data: str) -> str:
        return f"Extracting CSV data from: {file_data}"
    
    def parse_data(self, raw_data: str) -> str:
        return f"Parsing CSV data: {raw_data} -> Rows and columns"
    
    def analyze_data(self, data: str) -> str:
        return f"CSV Analysis: Statistical analysis and correlations in {data}"
    
    def send_report(self, analysis: str) -> str:
        return f"Email report sent: {analysis}"


class XMLDataMiner(DataMiner):
    """
    Concrete implementation for XML files.
    """
    
    def extract_data(self, file_data: str) -> str:
        return f"Extracting XML data from: {file_data}"
    
    def parse_data(self, raw_data: str) -> str:
        return f"Parsing XML data: {raw_data} -> DOM tree structure"
    
    def analyze_data(self, data: str) -> str:
        return f"XML Analysis: Schema validation and node relationships in {data}"
    
    def send_report(self, analysis: str) -> str:
        return f"Dashboard updated with: {analysis}"


# Game AI example
class GameAI(ABC):
    """
    Abstract class for game AI template method.
    """
    
    def take_turn(self, player_name: str) -> str:
        """
        Template method for taking a turn in a game.
        """
        results = []
        results.append(f"=== {player_name}'s Turn ===")
        
        # Collect resources
        resources = self.collect_resources()
        results.append(f"Resources: {resources}")
        
        # Build structures
        structures = self.build_structures()
        results.append(f"Structures: {structures}")
        
        # Build units
        units = self.build_units()
        results.append(f"Units: {units}")
        
        # Attack (hook - not all AI types attack)
        attack = self.attack()
        if attack:
            results.append(f"Attack: {attack}")
        
        # End turn
        end_result = self.end_turn()
        results.append(f"End Turn: {end_result}")
        
        return "\n".join(results)
    
    @abstractmethod
    def collect_resources(self) -> str:
        pass
    
    @abstractmethod
    def build_structures(self) -> str:
        pass
    
    @abstractmethod
    def build_units(self) -> str:
        pass
    
    def attack(self) -> Optional[str]:
        """
        Hook method - not all AI strategies attack.
        """
        return None
    
    def end_turn(self) -> str:
        """
        Common operation for all AI types.
        """
        return "Turn ended"


class AggressiveAI(GameAI):
    """
    Aggressive AI strategy.
    """
    
    def collect_resources(self) -> str:
        return "Quickly gathering resources for military units"
    
    def build_structures(self) -> str:
        return "Building barracks and weapon factories"
    
    def build_units(self) -> str:
        return "Training soldiers and tanks"
    
    def attack(self) -> str:
        return "Launching aggressive attack on enemy base!"


class DefensiveAI(GameAI):
    """
    Defensive AI strategy.
    """
    
    def collect_resources(self) -> str:
        return "Steadily collecting resources for defenses"
    
    def build_structures(self) -> str:
        return "Building walls and defensive towers"
    
    def build_units(self) -> str:
        return "Training defensive units and archers"
    
    # Note: DefensiveAI doesn't override attack() - it uses the default (no attack)


class EconomicAI(GameAI):
    """
    Economic-focused AI strategy.
    """
    
    def collect_resources(self) -> str:
        return "Maximizing resource collection efficiency"
    
    def build_structures(self) -> str:
        return "Building resource processing facilities and markets"
    
    def build_units(self) -> str:
        return "Training workers and resource gatherers"
    
    def attack(self) -> str:
        return "Economic warfare - disrupting enemy trade routes"


def client_code(abstract_class: AbstractClass) -> None:
    """
    The client code calls the template method to execute the algorithm. Client
    code doesn't have to know the concrete class of an object it works with, as
    long as it works with objects through the interface of their base class.
    """
    result = abstract_class.template_method()
    print(result)


def main():
    """
    The client code demonstrates the Template Method pattern.
    """
    print("=== Template Method Pattern Demo ===")
    
    # Basic template method pattern
    print("\n1. Basic Template Method:")
    
    print("ConcreteClass1:")
    client_code(ConcreteClass1())
    
    print("\nConcreteClass2:")
    client_code(ConcreteClass2())
    
    # Data mining example
    print("\n2. Data Mining Template Method:")
    
    data_miners = [
        ("PDF", PDFDataMiner()),
        ("CSV", CSVDataMiner()),
        ("XML", XMLDataMiner())
    ]
    
    for file_type, miner in data_miners:
        print(f"\n{file_type} Data Mining:")
        result = miner.mine_data(f"data.{file_type.lower()}")
        print(result)
    
    # Game AI example
    print("\n3. Game AI Template Method:")
    
    ai_strategies = [
        ("Aggressive", AggressiveAI()),
        ("Defensive", DefensiveAI()),
        ("Economic", EconomicAI())
    ]
    
    for strategy_name, ai in ai_strategies:
        print(f"\n{strategy_name} AI Strategy:")
        result = ai.take_turn(f"{strategy_name} Player")
        print(result)
    
    # Demonstrate template method invariant
    print("\n4. Template Method Invariant:")
    print("All subclasses follow the same algorithm structure:")
    
    # Show that the template method defines the structure
    for strategy_name, ai in ai_strategies:
        print(f"\n{strategy_name} AI - Same structure, different implementation:")
        lines = ai.take_turn(f"{strategy_name} Bot").split('\n')
        structure = [line.split(':')[0] for line in lines if ':' in line]
        print(f"Algorithm steps: {' -> '.join(structure)}")


if __name__ == "__main__":
    main()