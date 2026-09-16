from data.character import Character
from data.fetcher import get_2024_class_data

def main():
    print("--- Starting Phase 2 Data Layer Test ---\n")
    
    # 1. Initialize our character
    hero = Character(name="Bellamy")
    
    # 2. Fetch the 2024 monk data
    print("Fetching 5.5e monk data from 5etools...")
    monk_data = get_2024_class_data("class/class-monk.json")
    
    if not monk_data:
        print("Failed to fetch monk data. Check your connection or .env file.")
        return

    print(f"Success! Loaded: {monk_data.get('name')} (Source: {monk_data.get('source')})\n")
    
    # 3. Level up the character to Level 1
    hero.level_up_class("monk")
    
    # 4. Extract Level 1 features safely
    class_features = monk_data.get("classFeatures", [])
    
    print("Extracting Level 1 Features...")
    for item in class_features:
        # 5etools sometimes wraps references in a dict, or uses direct strings
        feature_ref = item.get("classFeature") if isinstance(item, dict) else item
            
        if isinstance(feature_ref, str):
            parts = feature_ref.split("|")
            
            # Strings can look like "classFeature|Martial Arts|Monk|XPHB|1" 
            # OR just "Martial Arts|Monk|XPHB|1". We handle both formats.
            if parts[0] == "classFeature":
                feature_name = parts[1]
                feature_level = parts[4] if len(parts) >= 5 else None
            else:
                feature_name = parts[0]
                feature_level = parts[3] if len(parts) >= 4 else None
                
            # If the feature belongs to Level 1, add it to our character
            if str(feature_level) == "1":
                hero.add_feature(feature_name, source="XPHB")
    
    # 5. Print the character state
    print("\n" + "="*30)
    print("      CHARACTER SHEET      ")
    print("="*30)
    print(f"Name:              {hero.name}")
    print(f"Total Level:       {hero.total_level}")
    print(f"Proficiency Bonus: +{hero.proficiency_bonus}")
    print("-" * 30)
    print("Active Features:")
    for feat in hero.features:
        print(f"  - {feat['name']}")
    print("="*30)

if __name__ == "__main__":
    main()