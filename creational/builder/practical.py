"""
Builder Design Pattern - Real World Implementation

Real-world example: Computer Configuration Builder
A computer store system that allows customers to build custom computers
by selecting different components step by step.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, field


class ComponentType(Enum):
    """Types of computer components."""
    CPU = "CPU"
    GPU = "GPU"
    RAM = "RAM"
    STORAGE = "Storage"
    MOTHERBOARD = "Motherboard"
    POWER_SUPPLY = "Power Supply"
    CASE = "Case"
    COOLING = "Cooling"


@dataclass
class Component:
    """Represents a computer component."""
    name: str
    component_type: ComponentType
    price: float
    power_consumption: int  # in watts
    specifications: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.name} (${self.price:.2f})"


@dataclass
class Computer:
    """Represents a complete computer configuration."""
    name: str
    components: List[Component] = field(default_factory=list)
    
    def add_component(self, component: Component) -> None:
        """Add a component to the computer."""
        # Check if component type already exists and replace it
        for i, existing in enumerate(self.components):
            if existing.component_type == component.component_type:
                print(f"Replacing {existing.name} with {component.name}")
                self.components[i] = component
                return
        
        self.components.append(component)
        print(f"Added {component.name} to {self.name}")
    
    def get_total_price(self) -> float:
        """Calculate total price of all components."""
        return sum(component.price for component in self.components)
    
    def get_total_power_consumption(self) -> int:
        """Calculate total power consumption."""
        return sum(component.power_consumption for component in self.components)
    
    def get_component_by_type(self, component_type: ComponentType) -> Optional[Component]:
        """Get component by type."""
        for component in self.components:
            if component.component_type == component_type:
                return component
        return None
    
    def get_specifications(self) -> Dict[str, Any]:
        """Get detailed specifications of the computer."""
        specs = {
            "name": self.name,
            "total_price": self.get_total_price(),
            "total_power_consumption": self.get_total_power_consumption(),
            "components": {}
        }
        
        for component in self.components:
            specs["components"][component.component_type.value] = {
                "name": component.name,
                "price": component.price,
                "power": component.power_consumption,
                "specs": component.specifications
            }
        
        return specs
    
    def __str__(self) -> str:
        """String representation of the computer."""
        if not self.components:
            return f"{self.name} - Empty configuration"
        
        component_list = []
        for component in self.components:
            component_list.append(f"  • {component}")
        
        return (f"{self.name} Configuration:\n" +
                "\n".join(component_list) +
                f"\nTotal Price: ${self.get_total_price():.2f}" +
                f"\nTotal Power: {self.get_total_power_consumption()}W")


class ComputerBuilder(ABC):
    """Abstract base class for computer builders."""
    
    def __init__(self, name: str):
        self.computer = Computer(name)
    
    @abstractmethod
    def add_cpu(self) -> None:
        """Add CPU to the computer."""
        pass
    
    @abstractmethod
    def add_gpu(self) -> None:
        """Add GPU to the computer."""
        pass
    
    @abstractmethod
    def add_ram(self) -> None:
        """Add RAM to the computer."""
        pass
    
    @abstractmethod
    def add_storage(self) -> None:
        """Add storage to the computer."""
        pass
    
    @abstractmethod
    def add_motherboard(self) -> None:
        """Add motherboard to the computer."""
        pass
    
    @abstractmethod
    def add_power_supply(self) -> None:
        """Add power supply to the computer."""
        pass
    
    @abstractmethod
    def add_case(self) -> None:
        """Add case to the computer."""
        pass
    
    @abstractmethod
    def add_cooling(self) -> None:
        """Add cooling system to the computer."""
        pass
    
    def get_computer(self) -> Computer:
        """Get the built computer."""
        return self.computer


class GamingComputerBuilder(ComputerBuilder):
    """Builder for high-end gaming computers."""
    
    def __init__(self):
        super().__init__("Gaming Beast")
    
    def add_cpu(self) -> None:
        cpu = Component(
            name="Intel Core i9-13900K",
            component_type=ComponentType.CPU,
            price=589.99,
            power_consumption=125,
            specifications={"cores": 24, "threads": 32, "base_clock": "3.0 GHz", "boost_clock": "5.8 GHz"}
        )
        self.computer.add_component(cpu)
    
    def add_gpu(self) -> None:
        gpu = Component(
            name="NVIDIA RTX 4090",
            component_type=ComponentType.GPU,
            price=1599.99,
            power_consumption=450,
            specifications={"memory": "24GB GDDR6X", "cuda_cores": 16384, "memory_bandwidth": "1008 GB/s"}
        )
        self.computer.add_component(gpu)
    
    def add_ram(self) -> None:
        ram = Component(
            name="Corsair Vengeance 32GB DDR5",
            component_type=ComponentType.RAM,
            price=299.99,
            power_consumption=15,
            specifications={"capacity": "32GB", "speed": "DDR5-5600", "modules": "2x16GB"}
        )
        self.computer.add_component(ram)
    
    def add_storage(self) -> None:
        storage = Component(
            name="Samsung 980 PRO 2TB NVMe SSD",
            component_type=ComponentType.STORAGE,
            price=199.99,
            power_consumption=8,
            specifications={"capacity": "2TB", "type": "NVMe M.2", "read_speed": "7,000 MB/s", "write_speed": "5,100 MB/s"}
        )
        self.computer.add_component(storage)
    
    def add_motherboard(self) -> None:
        motherboard = Component(
            name="ASUS ROG Strix Z790-E",
            component_type=ComponentType.MOTHERBOARD,
            price=449.99,
            power_consumption=50,
            specifications={"socket": "LGA1700", "chipset": "Z790", "form_factor": "ATX", "ram_slots": 4}
        )
        self.computer.add_component(motherboard)
    
    def add_power_supply(self) -> None:
        psu = Component(
            name="Corsair HX1000 80+ Platinum",
            component_type=ComponentType.POWER_SUPPLY,
            price=239.99,
            power_consumption=0,  # PSU provides power
            specifications={"wattage": "1000W", "efficiency": "80+ Platinum", "modular": "Fully Modular"}
        )
        self.computer.add_component(psu)
    
    def add_case(self) -> None:
        case = Component(
            name="Fractal Design Define 7",
            component_type=ComponentType.CASE,
            price=169.99,
            power_consumption=0,
            specifications={"form_factor": "Full Tower", "material": "Steel", "side_panel": "Tempered Glass"}
        )
        self.computer.add_component(case)
    
    def add_cooling(self) -> None:
        cooling = Component(
            name="Corsair H150i Elite AIO",
            component_type=ComponentType.COOLING,
            price=199.99,
            power_consumption=25,
            specifications={"type": "AIO Liquid Cooler", "radiator_size": "360mm", "fan_speed": "2400 RPM"}
        )
        self.computer.add_component(cooling)


class OfficeComputerBuilder(ComputerBuilder):
    """Builder for budget office computers."""
    
    def __init__(self):
        super().__init__("Office Workhorse")
    
    def add_cpu(self) -> None:
        cpu = Component(
            name="AMD Ryzen 5 5600G",
            component_type=ComponentType.CPU,
            price=139.99,
            power_consumption=65,
            specifications={"cores": 6, "threads": 12, "base_clock": "3.9 GHz", "boost_clock": "4.4 GHz", "integrated_gpu": "Radeon Graphics"}
        )
        self.computer.add_component(cpu)
    
    def add_gpu(self) -> None:
        # Office computer uses integrated graphics, no dedicated GPU
        pass
    
    def add_ram(self) -> None:
        ram = Component(
            name="Crucial 16GB DDR4",
            component_type=ComponentType.RAM,
            price=49.99,
            power_consumption=10,
            specifications={"capacity": "16GB", "speed": "DDR4-3200", "modules": "2x8GB"}
        )
        self.computer.add_component(ram)
    
    def add_storage(self) -> None:
        storage = Component(
            name="Kingston NV2 500GB SSD",
            component_type=ComponentType.STORAGE,
            price=29.99,
            power_consumption=5,
            specifications={"capacity": "500GB", "type": "NVMe M.2", "read_speed": "3,500 MB/s", "write_speed": "2,100 MB/s"}
        )
        self.computer.add_component(storage)
    
    def add_motherboard(self) -> None:
        motherboard = Component(
            name="MSI A520M-A PRO",
            component_type=ComponentType.MOTHERBOARD,
            price=54.99,
            power_consumption=30,
            specifications={"socket": "AM4", "chipset": "A520", "form_factor": "micro-ATX", "ram_slots": 2}
        )
        self.computer.add_component(motherboard)
    
    def add_power_supply(self) -> None:
        psu = Component(
            name="EVGA 450 BR 80+ Bronze",
            component_type=ComponentType.POWER_SUPPLY,
            price=49.99,
            power_consumption=0,
            specifications={"wattage": "450W", "efficiency": "80+ Bronze", "modular": "Non-Modular"}
        )
        self.computer.add_component(psu)
    
    def add_case(self) -> None:
        case = Component(
            name="Cooler Master MasterBox Q300L",
            component_type=ComponentType.CASE,
            price=39.99,
            power_consumption=0,
            specifications={"form_factor": "Mini Tower", "material": "Steel", "side_panel": "Acrylic"}
        )
        self.computer.add_component(case)
    
    def add_cooling(self) -> None:
        cooling = Component(
            name="AMD Wraith Stealth Cooler",
            component_type=ComponentType.COOLING,
            price=0.00,  # Included with CPU
            power_consumption=5,
            specifications={"type": "Air Cooler", "height": "54mm", "tdp": "65W"}
        )
        self.computer.add_component(cooling)


class ComputerStoreDirector:
    """
    Director that manages the computer building process.
    Provides different building strategies for different customer needs.
    """
    
    def __init__(self):
        self.builder: Optional[ComputerBuilder] = None
    
    def set_builder(self, builder: ComputerBuilder) -> None:
        """Set the builder to use."""
        self.builder = builder
    
    def build_basic_computer(self) -> Computer:
        """Build a basic computer with essential components."""
        if not self.builder:
            raise ValueError("Builder not set")
        
        self.builder.add_cpu()
        self.builder.add_ram()
        self.builder.add_storage()
        self.builder.add_motherboard()
        self.builder.add_power_supply()
        self.builder.add_case()
        self.builder.add_cooling()
        
        return self.builder.get_computer()
    
    def build_complete_computer(self) -> Computer:
        """Build a complete computer with all components."""
        if not self.builder:
            raise ValueError("Builder not set")
        
        self.builder.add_cpu()
        self.builder.add_gpu()
        self.builder.add_ram()
        self.builder.add_storage()
        self.builder.add_motherboard()
        self.builder.add_power_supply()
        self.builder.add_case()
        self.builder.add_cooling()
        
        return self.builder.get_computer()
    
    def build_custom_computer(self, components: List[str]) -> Computer:
        """Build a custom computer with specified components."""
        if not self.builder:
            raise ValueError("Builder not set")
        
        component_methods = {
            'cpu': self.builder.add_cpu,
            'gpu': self.builder.add_gpu,
            'ram': self.builder.add_ram,
            'storage': self.builder.add_storage,
            'motherboard': self.builder.add_motherboard,
            'power_supply': self.builder.add_power_supply,
            'case': self.builder.add_case,
            'cooling': self.builder.add_cooling
        }
        
        for component in components:
            if component.lower() in component_methods:
                component_methods[component.lower()]()
            else:
                print(f"Warning: Unknown component '{component}' requested")
        
        return self.builder.get_computer()


def main():
    """
    Real-world client code demonstrating computer building.
    """
    print("=== Computer Store Builder Demo ===")
    
    # Create director
    director = ComputerStoreDirector()
    
    # Build gaming computer
    print("\n--- Gaming Computer ---")
    gaming_builder = GamingComputerBuilder()
    director.set_builder(gaming_builder)
    
    gaming_pc = director.build_complete_computer()
    print(gaming_pc)
    
    # Build office computer
    print("\n--- Office Computer ---")
    office_builder = OfficeComputerBuilder()
    director.set_builder(office_builder)
    
    office_pc = director.build_basic_computer()
    print(office_pc)
    
    # Build custom computer
    print("\n--- Custom Computer ---")
    custom_builder = GamingComputerBuilder()
    director.set_builder(custom_builder)
    
    print("Building custom computer with selected components...")
    custom_pc = director.build_custom_computer(['cpu', 'ram', 'storage', 'motherboard', 'power_supply', 'case'])
    print(custom_pc)
    
    # Direct builder usage for fine-grained control
    print("\n--- Direct Builder Usage ---")
    manual_builder = OfficeComputerBuilder()
    manual_builder.computer.name = "Budget Workstation"
    
    # Add components manually
    manual_builder.add_cpu()
    manual_builder.add_ram()
    manual_builder.add_storage()
    manual_builder.add_motherboard()
    manual_builder.add_power_supply()
    manual_builder.add_case()
    manual_builder.add_cooling()
    
    # Add extra storage
    extra_storage = Component(
        name="Seagate BarraCuda 2TB HDD",
        component_type=ComponentType.STORAGE,
        price=49.99,
        power_consumption=8,
        specifications={"capacity": "2TB", "type": "SATA HDD", "rpm": "7200"}
    )
    manual_builder.computer.add_component(extra_storage)
    
    manual_pc = manual_builder.get_computer()
    print(manual_pc)
    
    # Show detailed specifications
    print("\n--- Detailed Specifications ---")
    gaming_specs = gaming_pc.get_specifications()
    print(f"Gaming PC Total Components: {len(gaming_specs['components'])}")
    print(f"Gaming PC Power Requirement: {gaming_specs['total_power_consumption']}W")
    
    office_specs = office_pc.get_specifications()
    print(f"Office PC Total Components: {len(office_specs['components'])}")
    print(f"Office PC Power Requirement: {office_specs['total_power_consumption']}W")
    
    # Cost comparison
    print(f"\nCost Comparison:")
    print(f"Gaming PC: ${gaming_pc.get_total_price():.2f}")
    print(f"Office PC: ${office_pc.get_total_price():.2f}")
    print(f"Custom PC: ${custom_pc.get_total_price():.2f}")
    print(f"Manual PC: ${manual_pc.get_total_price():.2f}")


if __name__ == "__main__":
    main()