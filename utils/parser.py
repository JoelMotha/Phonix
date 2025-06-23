import re

INTENT_KEYWORDS = {
    "gaming": [
        "game", "gaming", "fps", "processor", "lag free", "smooth", "pubg", "call of duty", "gamer",
        "multiplayer", "high frame", "fast refresh", "streaming", "graphics", "frame rate", "heat", 
        "cooling", "performance mode", "battle royale", "touch response", "no lag", "thermal control",
        "gaming mode", "game center", "vapor chamber", "game turbo", "game booster", "adaptive sync"
    ],
    "camera": [
        "camera", "photography", "photo", "selfie", "portrait", "macro", "night mode", "picture", 
        "snap", "lens", "optical zoom", "hdr photo", "ultra wide", "zoom", "video", "record", "cinematic",
        "vlogging", "rear cam", "night vision", "dslr", "camera quality", "depth sensor", "quad cam"
    ],
    "battery": [
        "battery", "charging", "mah", "charge", "fast charging", "power", "long battery", 
        "strong battery", "battery backup", "type c", "overnight", "battery saver", "quick charge",
        "power saving", "endurance", "charge speed", "long lasting", "usb c", "turbo charge"
    ],
    "display": [
        "display", "screen", "amoled", "refresh", "resolution", "hdr", "oled", "lcd", "brightness", 
        "watch", "video", "visual", "sharp", "big screen", "crisp", "viewing", "touchscreen", "fullscreen",
        "vivid", "contrast", "color accurate", "bezels", "curved display", "infinity display"
    ],
    "budget": [
        "cheap", "budget", "affordable", "value", "low cost", "mid range", "inexpensive", 
        "entry-level", "under 10000", "under 20k", "deal", "economical", "student", "pocket friendly",
        "cost effective", "best price", "bang for buck", "value for money", "below 15k"
    ],
    "performance": [
        "top specs", "high specs", "high-end", "flagship", "powerful", "best specs", "snappy", 
        "lag-free", "beast", "spec monster", "top tier", "fast", "elite performance", "high speed",
        "fluid experience", "speedy", "responsive", "performance beast", "no stutter"
    ]
}

SUPPORTING_FEATURES = {
    "connectivity": [
        "5g", "4g", "wifi", "nfc", "dual sim", "bluetooth", "network", "internet", "volte",
        "usb c", "ir blaster", "hotspot", "airplane mode", "sim slot", "connectivity", "roaming",
        "mobile data", "ethernet", "dongle", "tethering"
    ],
    "storage": [
        "expandable", "sd card", "storage", "rom", "memory", "internal storage", "128gb", 
        "256gb", "512gb", "storage expansion", "cloud backup", "micro sd", "file transfer",
        "memory card", "storage space", "media storage", "backup"
    ],
    "performance": [
        "ram", "fast", "performance", "processor", "smooth", "speed", "snapdragon", 
        "mediatek", "powerful", "multitask", "no lag", "octa core", "chipset", "benchmark",
        "hardware", "thermal", "cooling system", "speed test", "core", "refresh rate"
    ]
}

def parse_prompt(prompt):
    prompt = prompt.lower()
    result = {"intent": None, "budget": None, "keywords": [], "supporting_features": []}

    # Budget detection
    k_budget_match = re.search(r"(?:under|below|less than|upto|within)?\s*(\d{1,2})\s*k\b", prompt)
    if k_budget_match:
        try:
            result["budget"] = int(k_budget_match.group(1)) * 1000
        except ValueError:
            pass
    else:
        budget_match = re.search(r"(?:under|below|less than|upto|within|under rs\.?|\u20b9|inr)?\s*[₹\u20b9rs\.]?\s*([0-9]{1,3}(?:,?[0-9]{2,3})+|[0-9]{4,6})(?!g)\b", prompt)
        if budget_match:
            num_str = budget_match.group(1).replace(",", "")
            try:
                result["budget"] = int(num_str)
            except ValueError:
                pass

    matched_keywords = set()
    matched_supporting = set()
    intent_scores = {intent: 0 for intent in INTENT_KEYWORDS}

    full_phrases = prompt

    # Check for multi-word keywords first
    for feature, keywords in SUPPORTING_FEATURES.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", full_phrases):
                matched_keywords.add(kw)
                matched_supporting.add(feature)

    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", full_phrases):
                matched_keywords.add(kw)
                intent_scores[intent] += 1

    # Fallback to individual words
    words = re.findall(r"\w+", full_phrases)
    for word in words:
        for feature, keywords in SUPPORTING_FEATURES.items():
            if word in keywords:
                matched_keywords.add(word)
                matched_supporting.add(feature)
        for intent, keywords in INTENT_KEYWORDS.items():
            if word in keywords:
                matched_keywords.add(word)
                intent_scores[intent] += 1

    result["keywords"] = list(matched_keywords)
    result["supporting_features"] = list(matched_supporting)

    top_score = max(intent_scores.values())
    top_intents = [intent for intent, score in intent_scores.items() if score == top_score and score > 0]
    if top_intents:
        result["intent"] = top_intents[0]

    return result

# Sample prompts
samples = [
    "I want a gaming phone under 25000",
    "Best phone for photography under ₹30,000",
    "Need a phone with great battery and fast charging",
    "Budget phone with good display",
    "Affordable phone for daily use",
    "Looking for a smooth phone to play PUBG",
    "Need a camera that works well in night mode",
    "Need a phone with 5G and NFC support",
    "I want good storage and RAM under 20k",
    "I want a gaming phone with 5G and good RAM under ₹30,000",
    "Best phone for smooth PUBG, with ample storage and dual SIM",
    "Looking for a photography-focused phone with NFC and expandable memory",
    "Need a phone with excellent camera and 5G support for quick uploads",
    "Battery champion phone with dual SIM and SD card support",
    "Long-lasting battery phone with good RAM and 5G support",
    "OLED display phone with storage expansion and smooth performance",
    "Affordable phone with enough RAM and expandable storage",
    "Budget phone under 15k with 5G and smooth gaming experience",
    "Mid-range phone with good camera, 5G, and storage",
    "Need a powerful phone for gaming and streaming under ₹35k",
    "Something with a crisp display and a strong battery",
    "Decent phone with 5G, good camera, and expandable storage",
    "A reliable camera phone for travel with good RAM and 256GB storage",
    "Entry-level Android with decent performance and big screen"
]

for s in samples:
    print(f"\nPrompt: {s}")
    print(parse_prompt(s))