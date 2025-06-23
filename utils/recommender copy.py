import pandas as pd
import ast
import re
from parser import parse_prompt
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # directory of this script
csv_path = os.path.join(BASE_DIR, "utils", "tagged_dataset.csv")
df = pd.read_csv("tagged_dataset.csv")
df['tags'] = df['tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

# Fix the price column
def clean_price(value):
    try:
        return int(str(value).replace(",", "").replace("\u20b9", "").replace("INR", "").replace("Rs.", "").strip())
    except:
        return None

df["price"] = df["price"].apply(clean_price)
df.dropna(subset=["price"], inplace=True)
df["price"] = df["price"].astype(int)

# Known brands list for brand filtering
known_brands = ["Apple", "Samsung", "Xiaomi", "OnePlus", "Realme", "Vivo", "Oppo", "Asus", "Motorola", "Google"]

# Tag weights
feature_weights = {
    "performance": 2.0,
    "camera": 1.8,
    "battery": 1.5,
    "connectivity": 1.2,
    "storage": 1.2,
    "display": 1.0,
    "gaming": 2.0,
    "budget": 1.0,
    "design": 1.0,
    "night photography": 1.5,
    "ultra wide": 1.2,
    "cooling": 1.3,
    "vlogging": 1.2,
    "content creation": 1.3
}

def extract_budget_from_prompt(prompt):
    # Find all numbers in the prompt, assuming the first large number is budget in INR
    # We ignore small numbers < 1000 to avoid false positives
    numbers = re.findall(r'\d+', prompt.replace(',', ''))
    for num in numbers:
        value = int(num)
        if value >= 1000:  # threshold can be adjusted if needed
            return value
    return None

def extract_brand_from_prompt(prompt):
    prompt_lower = prompt.lower()
    for brand in known_brands:
        if brand.lower() in prompt_lower:
            return brand
    return None

def recommend_phone(user_prompt, top_n=5, debug=False, brand_filter=None):
    parsed = parse_prompt(user_prompt)
    intent = parsed.get("intent")
    budget = parsed.get("budget")
    features = set(parsed.get("supporting_features", []))

    # Fallback: use keywords if no supporting features are extracted
    if not features:
        features = set(parsed.get("keywords", []))

    if debug:
        print(f"\nParsed Query:\n- Intent: {intent}\n- Budget: {budget}\n- Features: {features}\n- Brand Filter: {brand_filter}\n")

    filtered_df = df.copy()

    # Apply brand filter
    if brand_filter:
        filtered_df = filtered_df[filtered_df['brand'].str.lower() == brand_filter.lower()]

    # Apply budget filter
    if budget:
        filtered_df = filtered_df[filtered_df['price'] <= budget]

    # Apply intent filter (phones must have the intent tag)
    if intent:
        filtered_df = filtered_df[filtered_df['tags'].apply(lambda tags: intent in tags)]

    # Score phones with weighted tags and matched features
    def compute_score(tags):
        matched = features.intersection(set(tags))
        matched_score = sum(feature_weights.get(f, 1.0) for f in matched)
        intent_bonus = feature_weights.get(intent, 1.0) if intent in tags else 0
        total_possible = sum(feature_weights.get(f, 1.0) for f in features) + feature_weights.get(intent, 1.0)
        final_score = (matched_score + intent_bonus) / total_possible if total_possible else 0
        return int(final_score * 500), list(matched)

    scores_and_matches = filtered_df['tags'].apply(compute_score)
    filtered_df["match_score"] = [score for score, match in scores_and_matches]
    filtered_df["matched_features"] = [match for score, match in scores_and_matches]

    if filtered_df.empty:
        return "No matching phones found for your query."

    # Sort and return top N
    top_matches = filtered_df.sort_values(by="match_score", ascending=False)
    return top_matches[["brand", "model", "price", "tags", "matched_features", "match_score"]].head(top_n).reset_index(drop=True)

def print_recommendations(df):
    if isinstance(df, str):  # handle error message string
        print(df)
        return

    # Sort by price descending
    df_sorted = df.sort_values(by="price", ascending=False).reset_index(drop=True)

    for i, row in df_sorted.iterrows():
        print(f"\nRecommendation #{i+1}:")
        print(f"Brand          : {row['brand']}")
        print(f"Model          : {row['model']}")
        print(f"Price          : ₹{row['price']:,}")
        print(f"Matched Features: {row['matched_features']}")
        print(f"Match Score    : {row['match_score']} / 500")

# ------------------------------
# Main execution block
# ------------------------------
if __name__ == "__main__":
    user_prompt = input("Enter your smartphone requirement: ")

    extracted_budget = extract_budget_from_prompt(user_prompt)
    extracted_brand = extract_brand_from_prompt(user_prompt)

    parsed = parse_prompt(user_prompt)

    if extracted_budget:
        parsed['budget'] = extracted_budget
        if extracted_budget >= 1000:
            print(f"Detected budget from prompt: ₹{extracted_budget}")

    if extracted_brand:
        print(f"Detected brand from prompt: {extracted_brand}")

    result = recommend_phone(user_prompt, top_n=3, debug=True, brand_filter=extracted_brand)

    print("\nRecommendations:")
    print_recommendations(result)

    print("=" * 50)
