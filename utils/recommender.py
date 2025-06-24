import pandas as pd
import ast
import re
from parser import parse_prompt
import os

# Fix the price column
def clean_price(value):
    try:
        return int(str(value).replace(",", "").replace("\u20b9", "").replace("INR", "").replace("Rs.", "").strip())
    except:
        return None

# Load dataset function
def load_dataset(path='tagged_dataset.csv'):
    df = pd.read_csv(path)
    df['tags'] = df['tags'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    df["price"] = df["price"].apply(clean_price)
    df.dropna(subset=["price"], inplace=True)
    df["price"] = df["price"].astype(int)
    return df

# Brand and feature weights
known_brands = ["Apple", "Samsung", "Xiaomi", "OnePlus", "Realme", "Vivo", "Oppo", "Asus", "Motorola", "Google"]

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

# Extract budget intelligently
def extract_budget_from_prompt(prompt):
    prompt = prompt.lower()
    if any(word in prompt for word in ["affordable", "budget", "cheap", "low-end"]):
        return 20000  # Default budget for affordability
    numbers = re.findall(r'\d+', prompt.replace(',', ''))
    for num in numbers:
        value = int(num)
        if value >= 1000:
            return value
    return None

def extract_brand_from_prompt(prompt):
    prompt_lower = prompt.lower()
    for brand in known_brands:
        if brand.lower() in prompt_lower:
            return brand
    return None

def recommend_phone(user_prompt, df, top_n=5, debug=False, brand_filter=None):
    parsed = parse_prompt(user_prompt)
    intent = parsed.get("intent")
    budget = parsed.get("budget")
    features = set(parsed.get("supporting_features", []))

    if not features:
        features = set(parsed.get("keywords", []))

    if debug:
        print(f"\nParsed Query:\n- Intent: {intent}\n- Budget: {budget}\n- Features: {features}\n- Brand Filter: {brand_filter}\n")

    filtered_df = df.copy()

    if brand_filter:
        filtered_df = filtered_df[filtered_df['brand'].str.lower() == brand_filter.lower()]

    if budget:
        filtered_df = filtered_df[filtered_df['price'] <= budget]

    if intent and not features:
        filtered_df = filtered_df[filtered_df['tags'].apply(lambda tags: intent in tags)]

    def compute_score(row):
        tags = row['tags']
        price = row['price']
        matched = features.intersection(set(tags))
        matched_score = sum(feature_weights.get(f, 1.0) for f in matched)
        intent_bonus = feature_weights.get(intent, 1.0) if intent in tags else 0
        total_possible = sum(feature_weights.get(f, 1.0) for f in features) + (feature_weights.get(intent, 1.0) if intent else 0)
        final_score = (matched_score + intent_bonus) / total_possible if total_possible else 0

        if "affordable" in features and price > 25000:
            final_score *= 0.6

        return int(final_score * 500), list(matched)

    scores_and_matches = filtered_df.apply(compute_score, axis=1)
    filtered_df["match_score"] = [score for score, match in scores_and_matches]
    filtered_df["matched_features"] = [match for score, match in scores_and_matches]

    if filtered_df.empty:
        return "No matching phones found for your query."

    if features or intent:
        top_matches = filtered_df.sort_values(by="match_score", ascending=False)
    else:
        def fallback_score(tags):
            return sum(feature_weights.get(tag, 1.0) for tag in tags)
        filtered_df["fallback_score"] = filtered_df["tags"].apply(fallback_score)
        top_matches = filtered_df.sort_values(by="fallback_score", ascending=False)
        return top_matches[["brand", "model", "price", "tags", "fallback_score"]].head(top_n).reset_index(drop=True)

    return top_matches[["brand", "model", "price", "tags", "matched_features", "match_score"]].head(top_n).reset_index(drop=True)

def print_recommendations(df):
    if isinstance(df, str):
        print(df)
        return

    df_sorted = df.sort_values(by="price", ascending=False).reset_index(drop=True)

    for i, row in df_sorted.iterrows():
        print(f"\nRecommendation #{i+1}:")
        print(f"Brand          : {row['brand']}")
        print(f"Model          : {row['model']}")
        print(f"Price          : ₹{row['price']:,}")
        if "matched_features" in row:
            print(f"Matched Features: {row['matched_features']}")
            print(f"Match Score    : {row['match_score']} / 500")
        elif "fallback_score" in row:
            print(f"Feature Richness Score: {row['fallback_score']} (fallback)")

if __name__ == "__main__":
    df = load_dataset()
    print("📱 Welcome to the Smartphone Recommender!")

    while True:
        user_prompt = input("\nEnter your smartphone requirement: ").strip()

        extracted_budget = extract_budget_from_prompt(user_prompt)
        extracted_brand = extract_brand_from_prompt(user_prompt)

        parsed = parse_prompt(user_prompt)

        if extracted_budget:
            parsed['budget'] = extracted_budget
            if extracted_budget >= 1000:
                print(f"Detected budget from prompt: ₹{extracted_budget}")

        if extracted_brand:
            print(f"Detected brand from prompt: {extracted_brand}")

        # If intent and features are not found
        has_intent_or_features = parsed.get("intent") or parsed.get("supporting_features") or parsed.get("keywords")
        has_brand_and_budget = extracted_brand and extracted_budget

        if not has_intent_or_features and not has_brand_and_budget:
            print("\n⚠️ Sorry, we couldn't identify any specific requirements in your prompt.")
            print("👉 Please be more specific about what you’re looking for — like performance, camera, gaming, battery life etc.")
            continue  # Ask again
        
        else:
            result = recommend_phone(user_prompt, df, top_n=3, debug=True, brand_filter=extracted_brand)

            if isinstance(result, str):
                print("\n❌", result)
                print("😕 Please try again with a different or clearer requirement.")
                continue  # Ask again

            print("\nRecommendations:")
            print_recommendations(result)
            print("=" * 50)
            print("🙏 Thanks for using the Smartphone Recommender. Have a great day!")
            break  # Exit loop
