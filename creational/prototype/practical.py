"""
Prototype Design Pattern - Real World Implementation

Real-world example: Game Character Creation System
A game that allows players to create characters by cloning existing templates
and customizing them, rather than building from scratch each time.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import copy
import random


class CharacterClass(Enum):
    """Character classes in the game."""
    WARRIOR = "Warrior"
    MAGE = "Mage"
    ROGUE = "Rogue"
    ARCHER = "Archer"
    CLERIC = "Cleric"


class Race(Enum):
    """Character races in the game."""
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    ORC = "Orc"
    HALFLING = "Halfling"


@dataclass
class Stats:
    """Character statistics."""
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    constitution: int = 10
    wisdom: int = 10
    charisma: int = 10
    
    def total(self) -> int:
        """Calculate total stats."""
        return (self.strength + self.dexterity + self.intelligence + 
                self.constitution + self.wisdom + self.charisma)
    
    def __str__(self) -> str:
        return (f"STR:{self.strength} DEX:{self.dexterity} INT:{self.intelligence} "
                f"CON:{self.constitution} WIS:{self.wisdom} CHA:{self.charisma}")


@dataclass
class Equipment:
    """Character equipment."""
    weapon: str = "Fists"
    armor: str = "Clothes"
    accessories: List[str] = field(default_factory=list)
    
    def add_accessory(self, accessory: str) -> None:
        """Add an accessory."""
        if accessory not in self.accessories:
            self.accessories.append(accessory)
    
    def remove_accessory(self, accessory: str) -> None:
        """Remove an accessory."""
        if accessory in self.accessories:
            self.accessories.remove(accessory)
    
    def __str__(self) -> str:
        accessories_str = ", ".join(self.accessories) if self.accessories else "None"
        return f"Weapon: {self.weapon}, Armor: {self.armor}, Accessories: {accessories_str}"


@dataclass
class Skills:
    """Character skills."""
    combat: int = 0
    magic: int = 0
    stealth: int = 0
    diplomacy: int = 0
    crafting: int = 0
    
    def add_skill_points(self, skill: str, points: int) -> None:
        """Add skill points."""
        if hasattr(self, skill):
            current_value = getattr(self, skill)
            setattr(self, skill, current_value + points)
    
    def total_skill_points(self) -> int:
        """Calculate total skill points."""
        return self.combat + self.magic + self.stealth + self.diplomacy + self.crafting
    
    def __str__(self) -> str:
        return (f"Combat:{self.combat} Magic:{self.magic} Stealth:{self.stealth} "
                f"Diplomacy:{self.diplomacy} Crafting:{self.crafting}")


class GameCharacter(ABC):
    """
    Abstract base class for game characters.
    Implements the prototype pattern for character creation.
    """
    
    def __init__(self, name: str, character_class: CharacterClass, race: Race):
        self.name = name
        self.character_class = character_class
        self.race = race
        self.level = 1
        self.experience = 0
        self.health = 100
        self.mana = 50
        self.stats = Stats()
        self.equipment = Equipment()
        self.skills = Skills()
        self.abilities: List[str] = []
        self.background_story = ""
        self.custom_attributes: Dict[str, Any] = {}
    
    @abstractmethod
    def clone(self) -> 'GameCharacter':
        """Create a copy of this character."""
        pass
    
    def add_ability(self, ability: str) -> None:
        """Add a special ability."""
        if ability not in self.abilities:
            self.abilities.append(ability)
    
    def set_background_story(self, story: str) -> None:
        """Set character background story."""
        self.background_story = story
    
    def set_custom_attribute(self, key: str, value: Any) -> None:
        """Set a custom attribute."""
        self.custom_attributes[key] = value
    
    def level_up(self) -> None:
        """Level up the character."""
        self.level += 1
        self.health += 10
        self.mana += 5
        # Add some random stat increases
        stat_names = ['strength', 'dexterity', 'intelligence', 'constitution', 'wisdom', 'charisma']
        for _ in range(2):  # 2 random stat increases per level
            stat = random.choice(stat_names)
            current_value = getattr(self.stats, stat)
            setattr(self.stats, stat, current_value + 1)
    
    def get_character_summary(self) -> str:
        """Get a summary of the character."""
        return (f"{self.name} - Level {self.level} {self.race.value} {self.character_class.value}\n"
                f"Health: {self.health}, Mana: {self.mana}\n"
                f"Stats: {self.stats}\n"
                f"Equipment: {self.equipment}\n"
                f"Skills: {self.skills}\n"
                f"Abilities: {', '.join(self.abilities) if self.abilities else 'None'}")
    
    def __str__(self) -> str:
        return f"{self.name} ({self.race.value} {self.character_class.value}, Level {self.level})"


class Warrior(GameCharacter):
    """Warrior character implementation."""
    
    def __init__(self, name: str, race: Race):
        super().__init__(name, CharacterClass.WARRIOR, race)
        # Set warrior-specific stats
        self.stats.strength = 15
        self.stats.constitution = 14
        self.stats.dexterity = 12
        self.health = 120
        self.mana = 20
        
        # Set warrior equipment
        self.equipment.weapon = "Iron Sword"
        self.equipment.armor = "Leather Armor"
        
        # Set warrior skills
        self.skills.combat = 15
        self.skills.crafting = 5
        
        # Add warrior abilities
        self.add_ability("Power Strike")
        self.add_ability("Shield Block")
    
    def clone(self) -> 'Warrior':
        """Create a deep copy of this warrior."""
        cloned = Warrior(self.name, self.race)
        
        # Copy all attributes
        cloned.level = self.level
        cloned.experience = self.experience
        cloned.health = self.health
        cloned.mana = self.mana
        cloned.stats = copy.deepcopy(self.stats)
        cloned.equipment = copy.deepcopy(self.equipment)
        cloned.skills = copy.deepcopy(self.skills)
        cloned.abilities = self.abilities.copy()
        cloned.background_story = self.background_story
        cloned.custom_attributes = copy.deepcopy(self.custom_attributes)
        
        return cloned


class Mage(GameCharacter):
    """Mage character implementation."""
    
    def __init__(self, name: str, race: Race):
        super().__init__(name, CharacterClass.MAGE, race)
        # Set mage-specific stats
        self.stats.intelligence = 16
        self.stats.wisdom = 14
        self.stats.constitution = 8
        self.health = 80
        self.mana = 120
        
        # Set mage equipment
        self.equipment.weapon = "Magic Staff"
        self.equipment.armor = "Robes"
        self.equipment.add_accessory("Spell Component Pouch")
        
        # Set mage skills
        self.skills.magic = 20
        self.skills.diplomacy = 8
        
        # Add mage abilities
        self.add_ability("Fireball")
        self.add_ability("Magic Missile")
        self.add_ability("Mana Shield")
    
    def clone(self) -> 'Mage':
        """Create a deep copy of this mage."""
        cloned = Mage(self.name, self.race)
        
        # Copy all attributes
        cloned.level = self.level
        cloned.experience = self.experience
        cloned.health = self.health
        cloned.mana = self.mana
        cloned.stats = copy.deepcopy(self.stats)
        cloned.equipment = copy.deepcopy(self.equipment)
        cloned.skills = copy.deepcopy(self.skills)
        cloned.abilities = self.abilities.copy()
        cloned.background_story = self.background_story
        cloned.custom_attributes = copy.deepcopy(self.custom_attributes)
        
        return cloned


class Rogue(GameCharacter):
    """Rogue character implementation."""
    
    def __init__(self, name: str, race: Race):
        super().__init__(name, CharacterClass.ROGUE, race)
        # Set rogue-specific stats
        self.stats.dexterity = 16
        self.stats.intelligence = 12
        self.stats.charisma = 13
        self.health = 90
        self.mana = 60
        
        # Set rogue equipment
        self.equipment.weapon = "Daggers"
        self.equipment.armor = "Leather Armor"
        self.equipment.add_accessory("Lockpicks")
        self.equipment.add_accessory("Poison Vials")
        
        # Set rogue skills
        self.skills.stealth = 18
        self.skills.diplomacy = 10
        self.skills.crafting = 7
        
        # Add rogue abilities
        self.add_ability("Sneak Attack")
        self.add_ability("Lockpicking")
        self.add_ability("Poison Blade")
    
    def clone(self) -> 'Rogue':
        """Create a deep copy of this rogue."""
        cloned = Rogue(self.name, self.race)
        
        # Copy all attributes
        cloned.level = self.level
        cloned.experience = self.experience
        cloned.health = self.health
        cloned.mana = self.mana
        cloned.stats = copy.deepcopy(self.stats)
        cloned.equipment = copy.deepcopy(self.equipment)
        cloned.skills = copy.deepcopy(self.skills)
        cloned.abilities = self.abilities.copy()
        cloned.background_story = self.background_story
        cloned.custom_attributes = copy.deepcopy(self.custom_attributes)
        
        return cloned


class CharacterTemplateManager:
    """
    Manages character templates and provides character creation services.
    """
    
    def __init__(self):
        self.templates: Dict[str, GameCharacter] = {}
        self.created_characters: List[GameCharacter] = []
        self._initialize_default_templates()
    
    def _initialize_default_templates(self) -> None:
        """Initialize default character templates."""
        # Create warrior templates
        human_warrior = Warrior("Human Warrior Template", Race.HUMAN)
        human_warrior.set_background_story("A brave human warrior defending their homeland.")
        self.templates["human_warrior"] = human_warrior
        
        dwarf_warrior = Warrior("Dwarf Warrior Template", Race.DWARF)
        dwarf_warrior.stats.constitution += 2
        dwarf_warrior.stats.strength += 1
        dwarf_warrior.health += 20
        dwarf_warrior.equipment.weapon = "Dwarven Axe"
        dwarf_warrior.equipment.armor = "Chain Mail"
        dwarf_warrior.add_ability("Dwarven Resilience")
        dwarf_warrior.set_background_story("A sturdy dwarf warrior from the mountain halls.")
        self.templates["dwarf_warrior"] = dwarf_warrior
        
        # Create mage templates
        elf_mage = Mage("Elf Mage Template", Race.ELF)
        elf_mage.stats.intelligence += 2
        elf_mage.stats.dexterity += 1
        elf_mage.mana += 30
        elf_mage.equipment.weapon = "Elven Staff"
        elf_mage.equipment.add_accessory("Spell Scroll")
        elf_mage.add_ability("Elven Magic")
        elf_mage.set_background_story("An elegant elf mage studying ancient magic.")
        self.templates["elf_mage"] = elf_mage
        
        human_mage = Mage("Human Mage Template", Race.HUMAN)
        human_mage.set_background_story("A human mage seeking knowledge and power.")
        self.templates["human_mage"] = human_mage
        
        # Create rogue templates
        halfling_rogue = Rogue("Halfling Rogue Template", Race.HALFLING)
        halfling_rogue.stats.dexterity += 2
        halfling_rogue.stats.charisma += 1
        halfling_rogue.skills.stealth += 5
        halfling_rogue.add_ability("Halfling Luck")
        halfling_rogue.set_background_story("A nimble halfling rogue with a mischievous streak.")
        self.templates["halfling_rogue"] = halfling_rogue
        
        elf_rogue = Rogue("Elf Rogue Template", Race.ELF)
        elf_rogue.stats.dexterity += 1
        elf_rogue.stats.intelligence += 1
        elf_rogue.skills.stealth += 3
        elf_rogue.skills.magic += 5
        elf_rogue.add_ability("Elven Stealth")
        elf_rogue.set_background_story("A graceful elf rogue moving through shadows.")
        self.templates["elf_rogue"] = elf_rogue
    
    def register_template(self, name: str, character: GameCharacter) -> None:
        """Register a new character template."""
        self.templates[name] = character
    
    def get_template_names(self) -> List[str]:
        """Get all available template names."""
        return list(self.templates.keys())
    
    def create_character(self, template_name: str, character_name: str) -> GameCharacter:
        """Create a new character from a template."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Clone the template
        template = self.templates[template_name]
        character = template.clone()
        
        # Set the new character's name
        character.name = character_name
        
        # Add to created characters list
        self.created_characters.append(character)
        
        return character
    
    def get_template_info(self, template_name: str) -> str:
        """Get information about a template."""
        if template_name not in self.templates:
            return f"Template '{template_name}' not found"
        
        template = self.templates[template_name]
        return template.get_character_summary()
    
    def get_created_characters(self) -> List[GameCharacter]:
        """Get all created characters."""
        return self.created_characters.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get creation statistics."""
        stats = {
            "total_templates": len(self.templates),
            "total_created": len(self.created_characters),
            "characters_by_class": {},
            "characters_by_race": {}
        }
        
        for character in self.created_characters:
            # Count by class
            class_name = character.character_class.value
            stats["characters_by_class"][class_name] = stats["characters_by_class"].get(class_name, 0) + 1
            
            # Count by race
            race_name = character.race.value
            stats["characters_by_race"][race_name] = stats["characters_by_race"].get(race_name, 0) + 1
        
        return stats


def main():
    """
    Real-world client code demonstrating character creation system.
    """
    print("=== Game Character Creation System ===")
    
    # Create character manager
    char_manager = CharacterTemplateManager()
    
    # Show available templates
    print("\n--- Available Character Templates ---")
    template_names = char_manager.get_template_names()
    for template_name in template_names:
        print(f"• {template_name}")
    
    # Show template details
    print("\n--- Template Details ---")
    for template_name in template_names[:3]:  # Show first 3 templates
        print(f"\n{template_name.upper()}:")
        info = char_manager.get_template_info(template_name)
        print(info)
    
    # Create characters from templates
    print("\n--- Creating Characters ---")
    
    # Create multiple characters
    characters = []
    
    # Player 1 creates a warrior
    player1_char = char_manager.create_character("human_warrior", "Conan the Barbarian")
    player1_char.set_background_story("A fierce barbarian warrior seeking glory in battle.")
    player1_char.level_up()
    player1_char.level_up()
    characters.append(player1_char)
    
    # Player 2 creates a mage
    player2_char = char_manager.create_character("elf_mage", "Gandalf the Grey")
    player2_char.set_background_story("A wise wizard with ancient knowledge.")
    player2_char.level_up()
    player2_char.skills.add_skill_points("magic", 10)
    player2_char.add_ability("Teleport")
    characters.append(player2_char)
    
    # Player 3 creates a rogue
    player3_char = char_manager.create_character("halfling_rogue", "Bilbo Baggins")
    player3_char.set_background_story("A curious hobbit who loves adventures.")
    player3_char.equipment.add_accessory("Magic Ring")
    player3_char.set_custom_attribute("favorite_food", "Second Breakfast")
    characters.append(player3_char)
    
    # Player 4 creates another warrior with different customization
    player4_char = char_manager.create_character("dwarf_warrior", "Gimli Gloinsson")
    player4_char.set_background_story("A proud dwarf warrior with an axe to grind.")
    player4_char.level_up()
    player4_char.equipment.add_accessory("Dwarf Beard Oil")
    player4_char.skills.add_skill_points("crafting", 15)
    characters.append(player4_char)
    
    # Player 5 creates a customized mage
    player5_char = char_manager.create_character("elf_mage", "Elrond Halfelven")
    player5_char.set_background_story("An ancient elf lord with deep magical knowledge.")
    player5_char.level_up()
    player5_char.level_up()
    player5_char.level_up()
    player5_char.equipment.weapon = "Ancient Staff of Power"
    player5_char.equipment.add_accessory("Ring of Power")
    player5_char.add_ability("Foresight")
    characters.append(player5_char)
    
    # Show created characters
    print("\n--- Created Characters ---")
    for i, character in enumerate(characters, 1):
        print(f"\nPlayer {i}'s Character:")
        print(character.get_character_summary())
        print(f"Background: {character.background_story}")
        if character.custom_attributes:
            print(f"Custom Attributes: {character.custom_attributes}")
    
    # Demonstrate that characters are independent
    print("\n--- Independence Test ---")
    print("Modifying original template...")
    
    # Modify a template
    original_template = char_manager.templates["human_warrior"]
    original_template.add_ability("Template Modified Ability")
    original_template.skills.add_skill_points("combat", 50)
    
    print(f"Template abilities: {original_template.abilities}")
    print(f"Player 1 character abilities: {player1_char.abilities}")
    print("✓ Characters are independent of templates!")
    
    # Show statistics
    print("\n--- Creation Statistics ---")
    stats = char_manager.get_statistics()
    print(f"Total templates: {stats['total_templates']}")
    print(f"Total characters created: {stats['total_created']}")
    print(f"Characters by class: {stats['characters_by_class']}")
    print(f"Characters by race: {stats['characters_by_race']}")
    
    # Demonstrate rapid character creation
    print("\n--- Rapid Character Creation ---")
    print("Creating 10 characters quickly using templates...")
    
    rapid_chars = []
    for i in range(10):
        template_name = random.choice(template_names)
        char_name = f"TestChar_{i+1}"
        char = char_manager.create_character(template_name, char_name)
        rapid_chars.append(char)
    
    print(f"Created {len(rapid_chars)} characters:")
    for char in rapid_chars:
        print(f"  • {char}")
    
    # Show final statistics
    final_stats = char_manager.get_statistics()
    print(f"\nFinal total characters: {final_stats['total_created']}")
    
    # Demonstrate template benefits
    print("\n--- Template Benefits ---")
    print("Benefits of using character templates:")
    print("1. Fast character creation - clone instead of building from scratch")
    print("2. Consistent character archetypes - balanced stats and abilities")
    print("3. Customization flexibility - modify cloned characters as needed")
    print("4. Memory efficiency - templates serve as master copies")
    print("5. Easy to add new templates - just register new prototypes")


if __name__ == "__main__":
    main()