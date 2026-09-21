import json
import os

def run_class_diagnostics():
    path = "temp/class-wizard.json"
    
    if not os.path.exists(path):
        print(f"Cannot find {path}. Make sure you leveled up a Wizard first!")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Isolate the 2024 Wizard
    wizard_2024 = next((c for c in data.get("class", []) if c.get("source") == "XPHB"), {})
    
    print("--- 2024 WIZARD ROOT KEYS ---")
    print(list(wizard_2024.keys()))
    
    print("\n--- SEARCHING FOR SPELL LISTS ---")
    for key, value in wizard_2024.items():
        # Look for any key that contains a massive list of spells
        if isinstance(value, list) and len(value) > 20 and isinstance(value[0], str):
            print(f"POTENTIAL SPELL LIST FOUND IN KEY: '{key}' (Contains {len(value)} items)")
            print(f"Sample: {value[:5]}")

if __name__ == "__main__":
    run_class_diagnostics()