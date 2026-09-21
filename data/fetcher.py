import os
import json
import requests
import urllib.request
from dotenv import load_dotenv
from data.logger import get_logger

# Load environment variables from the .env file
load_dotenv()

logger = get_logger(__name__)

# Pull the URL from the environment, with the current mirror as a fallback
DEFAULT_URL = "https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data/"
BASE_URL = os.environ.get("FIVE_E_TOOLS_BASE_URL", DEFAULT_URL)
CACHE_DIR = "temp"

def fetch_json(endpoint):
    """Fetches a JSON file from the 5etools mirror with local caching."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    filename = endpoint.split("/")[-1]
    cache_path = os.path.join(CACHE_DIR, filename)

    if os.path.exists(cache_path):
        logger.debug(f"Cache hit for {filename}. Loading locally from {cache_path}")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Corrupted cache file: {filename}. Refetching...")

    url = f"{BASE_URL}{endpoint}"
    logger.info(f"Fetching data from {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return data
        
    except requests.RequestException as e:
        logger.error(f"Network error fetching {endpoint}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {endpoint}: {e}")
        return None

def get_2024_class_data(class_endpoint):
    """Fetches class data and filters it for the 2024 rules (XPHB)."""
    data = fetch_json(class_endpoint)
    if not data:
        return None, None
        
    class_data_2024 = next(
        (cls for cls in data.get("class", []) if cls.get("source") == "XPHB"), 
        None
    )
    
    if class_data_2024:
        logger.info(f"Successfully extracted 2024 {class_data_2024['name']} data.")
        return class_data_2024, data.get("classFeature", [])
    else:
        logger.warning(f"No 2024 rules (XPHB) found in {class_endpoint}.")
        return None, None

def fetch_spell_class_map():
    """Builds a mapping of spells to classes using the highly stable 5e SRD API."""
    map_path = "temp/spell_class_map.json"
    
    # 1. Load from cache if we already built it
    if os.path.exists(map_path):
        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass

    print("Building Class Spell Maps from 5e API (This only happens once)...")
    core_classes = ["bard", "cleric", "druid", "paladin", "ranger", "sorcerer", "warlock", "wizard"]
    spell_map = {}
    
    # 2. Fetch the spell list for each class directly from the API
    for cls in core_classes:
        try:
            res = requests.get(f"https://www.dnd5eapi.co/api/classes/{cls}/spells", timeout=5)
            if res.status_code == 200:
                for spell in res.json().get("results", []):
                    spell_name = spell["name"].lower()
                    if spell_name not in spell_map:
                        spell_map[spell_name] = []
                    spell_map[spell_name].append(cls.capitalize())
        except Exception as e:
            print(f"Failed to fetch {cls} spells from API: {e}")
            
    # 3. Cache it so we never have to download it again
    if spell_map:
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump(spell_map, f, indent=4)
            
    return spell_map

def get_spell_data(filepath="temp/spells-xphb.json"):
    """Loads 2024 spells, merges 2014 data, and injects API class lists."""
    
    url_xphb = "https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data/spells/spells-xphb.json"
    url_phb = "https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data/spells/spells-phb.json"
    phb_path = "temp/spells-phb.json"
    
    os.makedirs("temp", exist_ok=True)
    
    # 1. Download XPHB (2024)
    if not os.path.exists(filepath):
        print("Downloading 2024 Spells...")
        try: urllib.request.urlretrieve(url_xphb, filepath)
        except: return []
        
    # 2. Download PHB (2014) Fallback
    if not os.path.exists(phb_path):
        print("Downloading 2014 Reference Library...")
        try: urllib.request.urlretrieve(url_phb, phb_path)
        except: pass

    # 3. Load the 2014 Base Spells
    phb_data = {}
    if os.path.exists(phb_path):
        with open(phb_path, 'r', encoding='utf-8') as f:
            for s in json.load(f).get("spell", []):
                phb_data[s["name"].lower()] = s

    # 4. Fetch the SRD Class Map (Our Magic Bullet)
    class_map = fetch_spell_class_map()

    # 5. Load the 2024 Spells
    with open(filepath, 'r', encoding='utf-8') as f:
        xphb_data = json.load(f).get("spell", [])

    parsed_spells = []
    
    for spell in xphb_data:
        name = spell.get("name", "Unknown Spell")
        
        # Merge with 2014 Base for missing spell mechanics
        copy_data = spell.get("_copy", {})
        base_name = copy_data.lower() if isinstance(copy_data, str) else copy_data.get("name", name).lower()
        base_spell = phb_data.get(base_name, {})
            
        level = spell.get("level", base_spell.get("level", 0))
        school = spell.get("school", base_spell.get("school", "A"))
        
        time_list = spell.get("time") or base_spell.get("time") or [{}]
        time_data = time_list[0] if time_list else {}
        casting_time = f"{time_data.get('number', 1)} {time_data.get('unit', 'action')}"
        
        range_obj = spell.get("range") or base_spell.get("range") or {}
        range_dist = range_obj.get("distance", {})
        if range_dist.get("type") == "touch": spell_range = "Touch"
        elif range_dist.get("type") == "self": spell_range = "Self"
        else: spell_range = f"{range_dist.get('amount', '')} {range_dist.get('type', '')}".strip()

        # --- THE FIX: INJECT CLASSES DIRECTLY FROM OUR MAP ---
        classes = class_map.get(name.lower(), [])
        
        entries = spell.get("entries") or base_spell.get("entries", [])

        parsed_spells.append({
            "name": name,
            "level": level,
            "school": school,
            "casting_time": casting_time,
            "range": spell_range,
            "classes": classes,
            "entries": entries
        })

    return parsed_spells
        
        