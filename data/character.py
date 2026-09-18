from data.logger import get_logger
from data.fetcher import get_spell_data
import math
import json
import os
import re

logger = get_logger(__name__)

class Character:
    def __init__(self, name="Unknown Hero"):
        self.name = name
        self.species = ""
        self.subspecies = {}

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

        # --- SPELLCASTING ---
        # Tracks the maximum and current spell slots: { 1: [4, 4], 2: [3, 3] }
        self.spell_slots = {}
        
        # Warlock Pact Magic tracks completely separately
        self.pact_slots = [0, 0] 
        self.pact_level = 0      
        
        # Stores prepared/known spells organized by spell level (0 = Cantrips)
        self.spells = {
            0: [], 1: [], 2: [], 3: [], 4: [], 
            5: [], 6: [], 7: [], 8: [], 9: []
        }
        # --------------------
        
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

    def level_up_class(self, class_name, selected_skills=None, subclass_name=None, species_name=None, subspecies_name=None):
        """Appends a class level, handles multiclassing, and calculates HP."""
        if species_name:
            self.species = species_name
        if subspecies_name and species_name:
            self.subspecies[species_name] = subspecies_name

        if class_name in self.classes:
            self.classes[class_name] += 1
        else:
            self.classes[class_name] = 1
            
        # --- Store Subclass ---
        if subclass_name:
            self.subclasses[class_name] = subclass_name
            
        total_level = sum(self.classes.values())

        # --- Level 1 Proficiencies ---
        if total_level == 1:
            save_map = {
                "Barbarian": ["STR", "CON"], "Bard": ["DEX", "CHA"], "Cleric": ["WIS", "CHA"],
                "Druid": ["INT", "WIS"], "Fighter": ["STR", "CON"], "Monk": ["STR", "DEX"],
                "Paladin": ["WIS", "CHA"], "Ranger": ["STR", "DEX"], "Rogue": ["DEX", "INT"],
                "Sorcerer": ["CON", "CHA"], "Warlock": ["WIS", "CHA"], "Wizard": ["INT", "WIS"]
            }
            self.saving_throw_proficiencies = save_map.get(class_name, [])
            
            if selected_skills:
                self.skill_proficiencies = selected_skills

        # --- TRIGGER SPECIES FEATURES & SPELLS ---
        self.grant_species_spells()
        self.grant_species_features()
        self.grant_class_features()
        self.grant_subclass_spells()
        
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

        # Calculate spell slots based on the new level safely!
        self.calculate_spell_slots()

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

    def prepare_spell(self, spell_dict):
        """Adds a spell to the character's prepared list based on its level."""
        level = spell_dict.get("level", 0)
        
        # Prevent adding duplicates
        if not any(s.get("name") == spell_dict.get("name") for s in self.spells[level]):
            self.spells[level].append(spell_dict)

    def unprepare_spell(self, spell_name, level):
        """Removes a spell from the character's prepared list."""
        self.spells[level] = [s for s in self.spells[level] if s.get("name") != spell_name]

    def calculate_spell_slots(self):
        """Calculates multiclass spell slots and Warlock pact slots."""
        
        # 1. The Master Spell Slot Table (Levels 1-20)
        # Each array represents spell slots for levels 1st through 9th
        multiclass_table = {
            0: [0, 0, 0, 0, 0, 0, 0, 0, 0],
            1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
            2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
            3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
            4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
            5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
            6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
            7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
            8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
            9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
            10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
            11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
            12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
            13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
            14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
            15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
            16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
            17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
            18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
            19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
            20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
        }

        caster_level = 0
        has_standard_caster = False
        
        # 2. Calculate Total Spellcaster Level
        for cls, level in self.classes.items():
            if cls in ["Bard", "Cleric", "Druid", "Sorcerer", "Wizard"]:
                caster_level += level
                has_standard_caster = True
            elif cls in ["Paladin", "Ranger"]:
                # 2024 Rules: Half-casters round UP for multiclassing
                caster_level += math.ceil(level / 2.0)
                has_standard_caster = True
            elif cls == "Fighter" and self.subclasses.get("Fighter") == "Eldritch Knight":
                caster_level += level // 3
                has_standard_caster = True
            elif cls == "Rogue" and self.subclasses.get("Rogue") == "Arcane Trickster":
                caster_level += level // 3
                has_standard_caster = True

        # Cap the lookup at 20
        caster_level = min(caster_level, 20)

        # 3. Apply to standard spell slots
        if has_standard_caster:
            max_slots = multiclass_table.get(caster_level, multiclass_table[0])
            for i, mx in enumerate(max_slots):
                spell_level = i + 1
                # Format: { spell_level: [max_slots, current_slots] }
                # Preserve current slots if they already exist, otherwise fill to max
                if mx > 0:
                    current = self.spell_slots.get(spell_level, [mx, mx])[1]
                    self.spell_slots[spell_level] = [mx, min(current, mx)]
                elif spell_level in self.spell_slots:
                    del self.spell_slots[spell_level]

        # 4. Handle Warlock Pact Magic Independently
        warlock_level = self.classes.get("Warlock", 0)
        if warlock_level > 0:
            if warlock_level >= 17:
                self.pact_slots[0] = 4
                self.pact_level = 5
            elif warlock_level >= 11:
                self.pact_slots[0] = 3
                self.pact_level = 5
            elif warlock_level >= 2:
                self.pact_slots[0] = 2
                self.pact_level = math.ceil(warlock_level / 2.0)
            else:
                self.pact_slots[0] = 1
                self.pact_level = 1
            
            # Fill current pact slots
            self.pact_slots[1] = self.pact_slots[0]

    def toggle_spell_slot(self, level, pact_magic=False):
        """Uses or restores a spell slot for a given level."""
        if pact_magic:
            max_slots, current = self.pact_slots
            self.pact_slots[1] = current - 1 if current > 0 else max_slots
        else:
            if level in self.spell_slots:
                max_slots, current = self.spell_slots[level]
                # If we have slots, use one. If we are at 0, "restoring" loops it back to max.
                self.spell_slots[level][1] = current - 1 if current > 0 else max_slots

    def grant_species_spells(self):
        if not self.species:
            return
            
        total_level = sum(self.classes.values()) if self.classes else 1
        
        # Get the specific lineage (e.g., "Forest Gnome" or "High Elf")
        lineage = self.subspecies.get(self.species, self.species)
        
        species_spells_map = {
            "Tiefling": [
                {"name": "Thaumaturgy", "level": 0, "min_level": 1},
                {"name": "Hellish Rebuke", "level": 1, "min_level": 3},
                {"name": "Darkness", "level": 2, "min_level": 5},
            ],
            "Forest Gnome": [ # Targeted specifically to Forest Gnomes!
                {"name": "Minor Illusion", "level": 0, "min_level": 1},
            ],
            "High Elf": [ # Targeted specifically to High Elves!
                {"name": "Prestidigitation", "level": 0, "min_level": 1},
            ],
            "Aasimar": [
                {"name": "Light", "level": 0, "min_level": 1},
                {"name": "Lesser Restoration", "level": 2, "min_level": 3},
                {"name": "Daylight", "level": 3, "min_level": 5},
            ],
        }
        
        # Check the lineage first; fall back to base species if not found
        granted_list = species_spells_map.get(lineage, species_spells_map.get(self.species, []))
        
        for spell_info in granted_list:
            if total_level >= spell_info["min_level"]:
                lvl = spell_info["level"]
                spell_name = spell_info["name"]
                
                existing_names = [s["name"].lower() for s in self.spells.get(lvl, [])]
                if spell_name.lower() not in existing_names:
                    from data.fetcher import get_spell_data
                    all_spells = get_spell_data("temp/spells-xphb.json")
                    full_spell_data = next((s for s in all_spells if s["name"].lower() == spell_name.lower()), None)
                    
                    if full_spell_data:
                        # 1. Create a copy and add flags to the JSON data
                        spell_copy = full_spell_data.copy()
                        spell_copy["always_prepared"] = True
                        spell_copy["source_feature"] = lineage 
                        
                        # Note: we check if spell_copy is in the list, not full_spell_data
                        if spell_copy not in self.spells[lvl]:
                            self.spells[lvl].append(spell_copy)
                    else:
                        # 2. Add the flags directly to the fallback dictionary
                        fallback = {
                            "name": spell_name, 
                            "level": lvl, 
                            "casting_time": "1 action", 
                            "range": "Self", 
                            "school": "Illusion", 
                            "entries": ["Species-granted innate magic."],
                            "always_prepared": True,
                            "source_feature": lineage
                        }
                        if fallback not in self.spells[lvl]:
                            self.spells[lvl].append(fallback)

    def grant_species_features(self):
        """Automatically provisions traits and features granted by the character's species."""
        if not self.species:
            return
  
        total_level = sum(self.classes.values()) if self.classes else 1

        # Get the specific lineage (e.g., "Forest Gnome" or "High Elf")
        lineage = self.subspecies.get(self.species, self.species) 

        # Comprehensive 2024 Species Traits Map
        species_traits_map = {
            "Tiefling": [
                {
                    "name": "Darkvision", 
                    "min_level": 1, 
                    "desc": "You have darkvision with a range of 60 feet."
                },
                {
                    "name": "Otherworldly Resistance", 
                    "min_level": 1, 
                    "desc": "You have Resistance to Fire damage."
                },
                {
                    "name": "Fiendish Legacy", 
                    "min_level": 1, 
                    "desc": "You know the Thaumaturgy cantrip. At level 3, you can cast Hellish Rebuke, and at level 5, Darkness."
                }
            ],
            "Aasimar": [
                {
                    "name": "Darkvision", 
                    "min_level": 1, 
                    "desc": "You have darkvision with a range of 60 feet."
                },
                {
                    "name": "Celestial Resistance", 
                    "min_level": 1, 
                    "desc": "You have Resistance to Necrotic and Radiant damage."
                },
                {
                    "name": "Healing Hands", 
                    "min_level": 1, 
                    "desc": "As a magic action, you can touch a creature and roll a number of d4s equal to your proficiency bonus, restoring that amount of HP."
                },
                {
                    "name": "Celestial Revelation", 
                    "min_level": 3, 
                    "desc": "Starting at 3rd level, you can transform to unleash celestial energy (Heavenly Wings, Inner Radiance, or Necrotic Shroud)."
                }
            ],
            "Dwarf": [
                {
                    "name": "Darkvision", 
                    "min_level": 1, 
                    "desc": "You have darkvision with a range of 60 feet."
                },
                {
                    "name": "Dwarven Resilience", 
                    "min_level": 1, 
                    "desc": "You have Resistance to Poison damage and Advantage on saving throws against poison."
                },
                {
                    "name": "Dwarven Toughness", 
                    "min_level": 1, 
                    "desc": "Your hit point maximum increases by 1, and it increases by 1 every time you gain a level."
                }
            ],
            "Elf": [
                {
                    "name": "Darkvision", 
                    "min_level": 1, 
                    "desc": "You have darkvision with a range of 60 feet."
                },
                {
                    "name": "Fey Ancestry", 
                    "min_level": 1, 
                    "desc": "You have Advantage on saving throws you make to avoid or end the Charmed condition."
                },
                {
                    "name": "Trance", 
                    "min_level": 1, 
                    "desc": "You don't need to sleep. Instead, you meditate deeply for 4 hours a long rest."
                }
            ],
            "Goliath": [
                {
                    "name": "Large Form", 
                    "min_level": 5, 
                    "desc": "Starting at 5th level, you can change your size to Large as a Bonus Action once per long rest."
                },
                {
                    "name": "Powerful Build", 
                    "min_level": 1, 
                    "desc": "You have Advantage on checks to escape a grapple, and you count as one size larger when determining carrying capacity."
                },
                {
                    "name": "Giant Ancestry", 
                    "min_level": 1, 
                    "desc": "You manifest the power of a giant ancestor (Cloud, Fire, Frost, Hill, Stone, or Storm Juggernaut abilities)."
                }
            ],
            "Halfling": [
                {
                    "name": "Brave", 
                    "min_level": 1, 
                    "desc": "You have Advantage on saving throws against being Frightened."
                },
                {
                    "name": "Halfling Nimbleness", 
                    "min_level": 1, 
                    "desc": "You can move through the space of any creature that is of a size larger than yours."
                },
                {
                    "name": "Naturally Lucky", 
                    "min_level": 1, 
                    "desc": "When you roll a 1 on the d20 for a D20 Test, you can reroll the die and must use the new roll."
                }
            ],
            "Human": [
                {
                    "name": "Resourceful", 
                    "min_level": 1, 
                    "desc": "You gain Inspiration whenever you finish a Long Rest."
                },
                {
                    "name": "Skilled", 
                    "min_level": 1, 
                    "desc": "You gain proficiency in one skill of your choice."
                },
                {
                    "name": "Versatile", 
                    "min_level": 1, 
                    "desc": "You gain an Origin Feat of your choice."
                }
            ],
            "Dragonborn": [
                {
                    "name": "Draconic Ancestry", 
                    "min_level": 1, 
                    "desc": "You have a draconic ancestor granting a specific damage type and breath weapon."
                },
                {
                    "name": "Breath Weapon", 
                    "min_level": 1, 
                    "desc": "You can exhale destructive energy in a 15-foot cone or 30-foot line (deals d10s matching your proficiency bonus)."
                },
                {
                    "name": "Damage Resistance", 
                    "min_level": 1, 
                    "desc": "You have Resistance to the damage type associated with your Draconic Ancestry."
                },
                {
                    "name": "Draconic Flight", 
                    "min_level": 5, 
                    "desc": "Starting at 5th level, you can sprout spectral wings to gain a Fly speed equal to your Speed."
                }
            ],
            "Orc": [
                {
                    "name": "Adrenaline Rush", 
                    "min_level": 1, 
                    "desc": "You can take the Dash action as a Bonus Action a number of times equal to your proficiency bonus per short rest."
                },
                {
                    "name": "Relentless Endurance", 
                    "min_level": 1, 
                    "desc": "When you are reduced to 0 HP but not killed outright, you can drop to 1 HP instead once per long rest."
                },
                {
                    "name": "Darkvision", 
                    "min_level": 1, 
                    "desc": "You have darkvision with a range of 60 feet."
                }
            ]
        }

        granted_traits = species_traits_map.get(self.species, [])

        for trait in granted_traits:
            if total_level >= trait["min_level"]:
                existing_names = [f["name"].lower() for f in self.features]
                if trait["name"].lower() not in existing_names:
                    # Pass the name and source positionally!
                    self.add_feature(
                        trait["name"], 
                        "XPHB", 
                        description=trait["desc"]
                    )

    def grant_subclass_spells(self):
        """Dynamically provisions 'Always Prepared' spells from 5etools subclass JSON data."""
        from data.fetcher import get_spell_data
        all_spells = get_spell_data("temp/spells-xphb.json")
        
        for class_name, subclass_name in self.subclasses.items():
            class_level = self.classes.get(class_name, 0)
            
            # 1. Load the raw class file directly
            file_path = f"temp/class/class-{class_name.lower()}.json"
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            except Exception as e:
                print(f"Failed to load JSON for {class_name}: {e}")
                continue
                
            # 2. Find the specific subclass object
            subclasses = raw_data.get("subclass", [])
            # Try to match the 2024 XPHB version first, fallback to any matching name
            target_subclass = next((sc for sc in subclasses if sc.get("name") == subclass_name and sc.get("source") == "XPHB"), None)
            if not target_subclass:
                target_subclass = next((sc for sc in subclasses if sc.get("name") == subclass_name), None)
                
            if not target_subclass:
                continue
                
            # 3. Parse the additionalSpells block
            additional_spells_list = target_subclass.get("additionalSpells", [])
            for spell_block in additional_spells_list:
                
                # We check common 5etools key structures for granted spells
                for grant_type, level_map in spell_block.items():
                    if grant_type in ["prepared", "known", "alwaysPrepared"]: 
                        
                        # level_map is usually {"3": ["bless", "cure wounds"]}
                        for req_level_str, spells in level_map.items():
                            try:
                                req_level = int(req_level_str)
                            except ValueError:
                                continue
                                
                            # If the character is high enough level in this specific class
                            if class_level >= req_level:
                                for spell_tag in spells:
                                    # 5etools spells are often formatted like "bless|xphb" or "{@spell bless}"
                                    spell_name = spell_tag.split("|")[0].replace("{@spell ", "").replace("}", "").strip()
                                    
                                    # Find the full spell to know what level dictionary array to put it in
                                    full_spell_data = next((s for s in all_spells if s["name"].lower() == spell_name.lower()), None)
                                    
                                    if full_spell_data:
                                        lvl = full_spell_data.get("level", 0)
                                        existing_names = [s["name"].lower() for s in self.spells.get(lvl, [])]
                                        
                                        if spell_name.lower() not in existing_names:
                                            spell_copy = full_spell_data.copy()
                                            spell_copy["always_prepared"] = True
                                            spell_copy["source_feature"] = subclass_name
                                            self.spells[lvl].append(spell_copy)

    def _extract_feature_text(self, entries):
        """Helper to convert 5etools nested entry data into a clean, readable string."""
        if not entries: return ""
        if isinstance(entries, str): 
            # Strip 5etools tags like {@condition Charmed} -> Charmed
            return re.sub(r'\{@[^\s]+\s([^}|]+)[^}]*\}', r'\1', entries)
            
        text = ""
        for entry in entries:
            if isinstance(entry, str):
                text += self._extract_feature_text(entry) + "\n\n"
            elif isinstance(entry, dict):
                if "name" in entry: 
                    text += f"{entry['name']}: "
                if "entries" in entry: 
                    text += self._extract_feature_text(entry["entries"])
                elif "items" in entry:
                    text += "\n" + "\n".join([f"  • {self._extract_feature_text(i)}" if isinstance(i, str) else "" for i in entry["items"]]) + "\n\n"
        return text.strip()

    def grant_class_features(self):
        """Dynamically parses and provisions class and subclass features from JSON."""
        for class_name, class_level in self.classes.items():
            file_path = f"temp/class/class-{class_name.lower()}.json"
            if not os.path.exists(file_path):
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            except Exception as e:
                print(f"Failed to load JSON for {class_name}: {e}")
                continue

            # 1. Parse Base Class Features (e.g., Action Surge, Rage, Cunning Action)
            class_features = raw_data.get("classFeature", [])
            for feat in class_features:
                if feat.get("className", "").lower() == class_name.lower():
                    if feat.get("level", 99) <= class_level:
                        feat_name = feat.get("name", "Unknown Feature")
                        
                        existing = [f["name"].lower() for f in self.features]
                        if feat_name.lower() not in existing:
                            desc = self._extract_feature_text(feat.get("entries", []))
                            self.add_feature(feat_name, feat.get("source", "XPHB"), description=desc)

            # 2. Parse Subclass Features (e.g., Disciple of Life, Vow of Enmity)
            subclass_name = self.subclasses.get(class_name)
            if subclass_name:
                subclass_features = raw_data.get("subclassFeature", [])
                for feat in subclass_features:
                    if feat.get("className", "").lower() == class_name.lower():
                        
                        # 5etools uses shortnames like "Life" for "Life Domain" or "Devotion" for "Oath of Devotion"
                        sc_short = feat.get("subclassShortName", "")
                        sc_full = feat.get("subclassName", "")
                        
                        # Check if the JSON shortname is inside the user's dropdown selection
                        if sc_short.lower() in subclass_name.lower() or sc_full.lower() == subclass_name.lower():
                            if feat.get("level", 99) <= class_level:
                                feat_name = feat.get("name", "Unknown Subclass Feature")
                                
                                existing = [f["name"].lower() for f in self.features]
                                if feat_name.lower() not in existing:
                                    desc = self._extract_feature_text(feat.get("entries", []))
                                    self.add_feature(feat_name, feat.get("source", "XPHB"), description=desc)