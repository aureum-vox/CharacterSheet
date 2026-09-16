from data.logger import get_logger

logger = get_logger(__name__)

class Character:
    def __init__(self, name="Unknown Hero"):
        self.name = name
        
        # Base Ability Scores
        self.abilities = {
            "STR": 10,
            "DEX": 10,
            "CON": 10,
            "INT": 10,
            "WIS": 10,
            "CHA": 10
        }
        
        # Class tracking, supports multiclassing: { "Fighter": 5, "Wizard": 2 }
        self.classes = {}
        
        # Features gained from classes, species, backgrounds, and feats
        self.features = []
        
        logger.info(f"Initialized new character: {self.name}")

    @property
    def total_level(self):
        """Calculates total character level by summing all class levels."""
        return sum(self.classes.values())

    @property
    def proficiency_bonus(self):
        """Calculates proficiency bonus based on total level."""
        level = self.total_level
        if level == 0:
            return 0
        # 5e math: Levels 1-4 = +2, 5-8 = +3, 9-12 = +4, 13-16 = +5, 17-20 = +6
        return ((level - 1) // 4) + 2

    def get_modifier(self, ability):
        """Calculates the standard D&D modifier (e.g., 14 -> +2, 8 -> -1)."""
        score = self.abilities.get(ability.upper(), 10)
        return (score - 10) // 2

    def set_ability(self, ability, score):
        """Updates a base ability score."""
        ability = ability.upper()
        if ability in self.abilities:
            self.abilities[ability] = score
            logger.debug(f"{self.name}'s {ability} set to {score} (Mod: {self.get_modifier(ability)})")

    def level_up_class(self, class_name):
        """Increments a class level and triggers feature fetching logic."""
        if class_name in self.classes:
            self.classes[class_name] += 1
        else:
            self.classes[class_name] = 1
            
        new_level = self.classes[class_name]
        logger.info(f"{self.name} leveled up {class_name} to level {new_level}. Total level: {self.total_level}")
        
        # Placeholder: This is where we will hook in the JSON parser 
        # to fetch and append the new features for this specific class and level.

    def add_feature(self, feature_name, source, description="", uses=0, choices=None):
        """Appends a new feature to the character."""
        feature = {
            "name": feature_name, 
            "source": source, 
            "description": description,
            "uses": uses,
            "choices": choices or [] 
        }
        # DEBUG LOG 2: Check what is actually saved in memory
        print(f"[DEBUG 2] Saved to memory -> {feature_name} | Desc length: {len(feature['description'])}")
        
        self.features.append(feature)