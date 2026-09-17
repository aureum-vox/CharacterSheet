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
        self.hp_max = 0
        self.current_hp = 0
        self.hit_dice_total = 0

        # Class tracking, supports multiclassing: { "Fighter": 5, "Wizard": 2 }
        self.classes = {}

        # Tracks subclass choices: { "Monk": "Warrior of the Open Hand" }
        self.subclasses = {}

        # --- PROFICIENCIES & SKILLS ---
        # Starting with standard Monk proficiencies for testing
        self.saving_throw_proficiencies = []
        self.skill_proficiencies = []
        
        self.skill_ability_map = {
            "Acrobatics": "DEX", "Animal Handling": "WIS", "Arcana": "INT",
            "Athletics": "STR", "Deception": "CHA", "History": "INT",
            "Insight": "WIS", "Intimidation": "CHA", "Investigation": "INT",
            "Medicine": "WIS", "Nature": "INT", "Perception": "WIS",
            "Performance": "CHA", "Persuasion": "CHA", "Religion": "INT",
            "Sleight of Hand": "DEX", "Stealth": "DEX", "Survival": "WIS"
        }
        
        # Features gained from classes, species, backgrounds, and feats
        self.features = []
        self.coins = {"CP": 0, "SP": 0, "EP": 0, "GP": 15, "PP": 0}
        self.inventory = []
        
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

    def level_up_class(self, class_name, selected_skills=None, subclass_name=None):
        """Appends a class level, handles multiclassing, and calculates HP."""
        if class_name in self.classes:
            self.classes[class_name] += 1
        else:
            self.classes[class_name] = 1
            
        # --- NEW: Store Subclass ---
        if subclass_name:
            self.subclasses[class_name] = subclass_name
            
        total_level = sum(self.classes.values())
        
        # --- Level 1 Proficiencies ---
        if total_level == 1:
            # Map out standard class saving throws
            save_map = {
                "Barbarian": ["STR", "CON"], "Bard": ["DEX", "CHA"], "Cleric": ["WIS", "CHA"],
                "Druid": ["INT", "WIS"], "Fighter": ["STR", "CON"], "Monk": ["STR", "DEX"],
                "Paladin": ["WIS", "CHA"], "Ranger": ["STR", "DEX"], "Rogue": ["DEX", "INT"],
                "Sorcerer": ["CON", "CHA"], "Warlock": ["WIS", "CHA"], "Wizard": ["INT", "WIS"]
            }
            self.saving_throw_proficiencies = save_map.get(class_name, [])
            
            if selected_skills:
                self.skill_proficiencies = selected_skills
        # ----------------------------------
        
        # Determine Hit Die based on class
        # ... (keep your existing hit die and HP math below here!) ...

       # Determine Hit Die based on class 
        hit_die_map = {"Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10, 
                       "Monk": 8, "Cleric": 8, "Druid": 8, "Bard": 8, "Rogue": 8, 
                       "Warlock": 8, "Sorcerer": 6, "Wizard": 6}
        die_size = hit_die_map.get(class_name, 8)
        
        con_mod = self.get_modifier("CON")
        
        if total_level == 1:
            # Max hit die at level 1 + Con modifier
            hp_gain = die_size + con_mod
        else:
            # Average roll + Con modifier (minimum 1 gain)
            average_roll = (die_size // 2) + 1
            hp_gain = max(1, average_roll + con_mod)
            
        self.hp_max += hp_gain
        self.current_hp = self.hp_max
        self.hit_dice_total = total_level

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

    def add_item(self, name, quantity, weight):
        """Appends a new item to the character's inventory."""
        self.inventory.append({
            "name": name, 
            "quantity": quantity, 
            "weight": weight
        })

    def get_modifier(self, stat_name):
        """Calculates the D&D ability modifier for a given stat (e.g., 'CON')."""
        score = self.abilities.get(stat_name, 10)
        return (score - 10) // 2

    def get_hit_dice_string(self):
        """Generates a formatted hit dice string (e.g., '2d8 + 1d10')."""
        hit_die_map = {"Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10, 
                       "Monk": 8, "Cleric": 8, "Druid": 8, "Bard": 8, "Rogue": 8, 
                       "Warlock": 8, "Sorcerer": 6, "Wizard": 6}
        
        dice_counts = {}
        for class_name, level in self.classes.items():
            die = hit_die_map.get(class_name.capitalize(), 8)
            dice_counts[f"d{die}"] = dice_counts.get(f"d{die}", 0) + level
            
        if not dice_counts:
            return "0"
            
        return " + ".join([f"{count}{die}" for die, count in dice_counts.items()])

    def get_prof_bonus(self):
        """Calculates proficiency bonus based on total character level."""
        total_level = sum(self.classes.values())
        if total_level == 0:
            return 2 # Base PB for a level 0/1 character
        return 2 + ((total_level - 1) // 4)

    def get_save_modifier(self, stat_name):
        """Returns the total save modifier (Ability Mod + PB if proficient)."""
        mod = self.get_modifier(stat_name)
        if stat_name in self.saving_throw_proficiencies:
            mod += self.get_prof_bonus()
        return mod

    def get_skill_modifier(self, skill_name):
        """Returns the total skill modifier (Ability Mod + PB if proficient)."""
        stat = self.skill_ability_map.get(skill_name, "STR")
        mod = self.get_modifier(stat)
        if skill_name in self.skill_proficiencies:
            mod += self.get_prof_bonus()
        return mod

    def toggle_save_proficiency(self, stat_name):
        """Toggles proficiency for a saving throw."""
        if stat_name in self.saving_throw_proficiencies:
            self.saving_throw_proficiencies.remove(stat_name)
        else:
            self.saving_throw_proficiencies.append(stat_name)

    def toggle_skill_proficiency(self, skill_name):
        """Toggles proficiency for a skill."""
        if skill_name in self.skill_proficiencies:
            self.skill_proficiencies.remove(skill_name)
        else:
            self.skill_proficiencies.append(skill_name)