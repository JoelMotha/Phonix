import re
import pandas as pd

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

def add_spec_tags(row):
    tags = set()

    # RAM tag (rounded to common sizes)
    try:
        ram_gb = int(re.sub(r"\D", "", str(row.get('ram', ''))))
        for size in [2, 4, 6, 8, 12, 16]:
            if ram_gb <= size:
                tags.add(f"{size}gb")
                break
    except:
        pass

    # Storage tag (rounded to common sizes)
    try:
        storage_gb = int(re.sub(r"\D", "", str(row.get('storage', ''))))
        for size in [32, 64, 128, 256, 512]:
            if storage_gb <= size:
                tags.add(f"{size}gb")
                break
    except:
        pass

    # Battery tag (rounded to common sizes)
    try:
        battery_mah = int(re.sub(r"\D", "", str(row.get('battery', ''))))
        for size in [3000, 4000, 4500, 5000, 6000]:
            if battery_mah <= size:
                tags.add(f"{size}mah")
                break
    except:
        pass

    # Display size tag (rounded to 1 decimal place)
    try:
        display_size = float(re.search(r"\d+(\.\d+)?", str(row.get('display size', ''))).group())
        tags.add(str(round(display_size, 1)))
    except:
        pass

    # Refresh rate tag
    try:
        refresh_rate = int(re.sub(r"\D", "", str(row.get('refresh rate', ''))))
        if refresh_rate > 0:
            tags.add(f"{refresh_rate}hz")
    except:
        pass

    # 5G support tag
    try:
        if str(row.get('5G', '')).lower() in ['yes', 'true', 'supported', '1']:
            tags.add("5g")
    except:
        pass

    # Fast charging tag
    try:
        charging_desc = str(row.get('charging speed', '')).lower()
        if "fast" in charging_desc:
            tags.add("fast charging")
    except:
        pass

    # Dual SIM tag
    try:
        sim_slots = int(re.sub(r"\D", "", str(row.get('sim slots', '1'))))
        if sim_slots >= 2:
            tags.add("dual sim")
    except:
        pass

    # Rear camera megapixels tag
    try:
        rear_cams = re.findall(r"\d+", str(row.get('rear camera', '')))
        if rear_cams:
            max_rear_mp = max([int(mp) for mp in rear_cams])
            tags.add(f"{max_rear_mp}mp")
    except:
        pass

    # Front camera megapixels tag
    try:
        front_cams = re.findall(r"\d+", str(row.get('front camera', '')))
        if front_cams:
            max_front_mp = max([int(mp) for mp in front_cams])
            tags.add(f"{max_front_mp}mp front")
    except:
        pass

    return list(tags)


def tag_phone(row):
    tags = set()

    # Gaming tag
    try:
        ram = int(re.sub(r"\D", "", str(row['ram'])))
        refresh = int(re.sub(r"\D", "", str(row['refresh rate'])))
        processor = str(row['processor']).lower()
        if ram >= 6 and refresh >= 90 and any(p in processor for p in ['snapdragon', 'mediatek', 'a13', 'a14', 'a15', 'a16', 'a17']):
            tags.add("gaming")
    except:
        pass

    # Battery tag
    try:
        battery = int(re.sub(r"\D", "", str(row['battery'])))
        charging = str(row.get('charging speed', '')).lower()
        if battery >= 5000 or "fast" in charging:
            tags.add("battery")
    except:
        pass

    # Camera tag
    try:
        rear = re.findall(r"\d+", str(row['rear camera']))
        front = re.findall(r"\d+", str(row['front camera']))
        rear_max = max([int(x) for x in rear]) if rear else 0
        front_max = max([int(x) for x in front]) if front else 0
        if rear_max >= 12 and front_max >= 12:
            tags.add("camera")
    except:
        pass

    # Display tag
    try:
        resolution = str(row['display resolution']).lower()
        model = str(row['model']).lower()
        size = float(re.search(r"\d+(\.\d+)?", str(row['display size'])).group())
        if any(q in resolution for q in ['fhd', 'full hd', '1080', 'retina', 'oled']) or size >= 6.5 or "pro max" in model:
            tags.add("display")
    except:
        pass

    # Budget tag (basic example, adjust as needed)
    try:
        price = int(re.sub(r"\D", "", str(row['price'])))
        if price <= 10000:
            tags.add("10000")
        elif price <= 20000:
            tags.add("20000")
        elif price <= 30000:
            tags.add("30000")
        elif price <= 40000:
            tags.add("40000")
        elif price <= 50000:
            tags.add("50000")
        elif price <= 60000:
            tags.add("60000")
        elif price <= 70000:
            tags.add("70000")
        elif price <= 80000:
            tags.add("80000")
        elif price <= 90000:
            tags.add("90000")
        elif price <= 100000:
            tags.add("100000")
        elif price <= 110000:
            tags.add("110000")
        elif price <= 120000:
            tags.add("120000")
        elif price <= 130000:
            tags.add("130000")
        elif price <= 140000:
            tags.add("140000")
        elif price <= 150000:
            tags.add("150000")
        elif price <= 160000:
            tags.add("160000")
        elif price <= 170000:
            tags.add("170000")
        elif price <= 180000:
            tags.add("180000")
        elif price <= 190000:
            tags.add("190000")
        elif price <= 200000:
            tags.add("200000")
    except:
        pass

    # Connectivity tag
    try:
        connectivity_features = [str(row.get("5G", "")), str(row.get("4G volte", "")), str(row.get("4G", "")), str(row.get("3G", "")), str(row.get("nfc", "")), str(row.get("sim slots", ""))]
        connectivity_text = " ".join(connectivity_features).lower()
        if any(keyword in connectivity_text for keyword in SUPPORTING_FEATURES["connectivity"]):
            tags.add("connectivity")
    except:
        pass

    # Storage tag
    try:
        storage = str(row.get("storage", "")) + " " + str(row.get("memory card support", ""))
        if any(keyword in storage.lower() for keyword in SUPPORTING_FEATURES["storage"]):
            tags.add("storage")
    except:
        pass

    # Performance tag
    try:
        perf_text = str(row.get("ram", "")) + " " + str(row.get("processor", "")) + " " + str(row.get("processor type", ""))
        if any(keyword in perf_text.lower() for keyword in SUPPORTING_FEATURES["performance"]):
            tags.add("performance")
    except:
        pass

    # Night photography tag
    try:
        camera_text = str(row.get("rear camera", "")).lower()
        if any(kw in camera_text for kw in ["night", "ois", "sony sensor", "night vision", "low light"]):
            tags.add("night photography")
    except:
        pass

    # Ultra wide tag
    try:
        if "ultra wide" in str(row.get("rear camera", "")).lower():
            tags.add("ultra wide")
    except:
        pass

    # Design tag
    try:
        design_text = str(row.get("description", "")).lower() + " " + str(row.get("model", "")).lower()
        if any(kw in design_text for kw in ["sleek", "modern", "premium", "glass back", "design", "aesthetic", "stylish"]):
            tags.add("design")
    except:
        pass

    # Cooling tag
    try:
        heat_text = str(row.get("processor", "")).lower() + " " + str(row.get("description", "")).lower()
        if any(kw in heat_text for kw in ["cooling", "vapor chamber", "heat", "thermal", "liquid cooling", "game booster"]):
            tags.add("cooling")
    except:
        pass

    # Vlogging and content creation tags
    try:
        desc = str(row.get("description", "")).lower()
        if "vlog" in desc or "vlogging" in desc:
            tags.add("vlogging")
        if any(kw in desc for kw in ["youtube", "creator", "influencer", "video editing", "content"]):
            tags.add("content creation")
    except:
        pass

    # Brand tag (lowercase)
    brand = str(row.get("brand", "")).lower()
    if brand:
        tags.add(brand)

    # Add spec tags
    tags.update(add_spec_tags(row))

    return list(tags)


if __name__ == "__main__":
    df = pd.read_csv("final dataset.csv")
    df['tags'] = df.apply(tag_phone, axis=1)
    df.to_csv("tagged_dataset.csv", index=False)
    print(df[['model', 'brand', 'tags']].head(10))
