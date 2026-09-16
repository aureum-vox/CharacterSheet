import os
import json
import requests
from dotenv import load_dotenv
from data.logger import get_logger

# Load environment variables from the .env file
load_dotenv()

logger = get_logger(__name__)

# Pull the URL from the environment, with the current mirror as a fallback
DEFAULT_URL = "https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data/"
BASE_URL = os.environ.get("FIVE_E_TOOLS_BASE_URL", DEFAULT_URL)
CACHE_DIR = "temp"

# ... (keep the fetch_json and get_2024_class_data functions exactly as they were)

def fetch_json(endpoint):
    """
    Fetches a JSON file from the 5etools mirror.
    Checks the local temp/ cache first to avoid unnecessary network calls.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Create a safe filename from the endpoint (e.g., "class/class-fighter.json" -> "class-fighter.json")
    filename = endpoint.split("/")[-1]
    cache_path = os.path.join(CACHE_DIR, filename)

    # 1. Check local cache
    if os.path.exists(cache_path):
        logger.debug(f"Cache hit for {filename}. Loading locally from {cache_path}")
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Corrupted cache file: {filename}. Refetching from network...")

    # 2. Fetch from Network if not cached
    url = f"{BASE_URL}{endpoint}"
    logger.info(f"Fetching data from {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an exception for 404s, 500s, etc.
        data = response.json()
        
        # 3. Save to cache for future runs
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.debug(f"Successfully cached {filename}")
        
        return data
        
    except requests.RequestException as e:
        logger.error(f"Network error fetching {endpoint}: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {endpoint}: {e}")
        return None

def get_2024_class_data(class_endpoint):
    """
    Fetches class data and filters it for the 2024 rules (XPHB).
    Returns a tuple: (class_data, feature_data_array)
    """
    data = fetch_json(class_endpoint)
    if not data:
        return None, None
        
    # Isolate the 2024 Player's Handbook version of the class
    class_data_2024 = next(
        (cls for cls in data.get("class", []) if cls.get("source") == "XPHB"), 
        None
    )
    
    if class_data_2024:
        logger.info(f"Successfully extracted 2024 {class_data_2024['name']} data.")
        # RETURN BOTH: The specific class object AND the root feature array
        return class_data_2024, data.get("classFeature", [])
    else:
        logger.warning(f"No 2024 rules (XPHB) found in {class_endpoint}.")
        return None, None