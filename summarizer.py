import json
from collections import defaultdict
from transformers import pipeline
from datetime import datetime
import re

# Load T5 model for summarization with GPU support
summarizer = pipeline("summarization", model="t5-large", device=0)

# Load your original JSON file
with open(r"C:\Users\tanma\OneDrive\Desktop\Data Engineering\web_scraping_workspace\scrapy\news\output.json", "r", encoding="utf-8") as f:
    news_data = json.load(f)

# Function to apply sentence casing
def sentence_case(text):
    text = text.strip()
    sentences = re.split('(?<=[.])\s+', text)
    sentences = [s.capitalize() for s in sentences]
    return ' '.join(sentences)

# Summarize and replace 'body_text'
filtered_news_data = []  # This will store valid news items
for item in news_data:
    # Skip articles with null or empty title or body_text
    if not item.get('title') or not item.get('body_text'):
        continue
    
    body_text = item.get('body_text', '')
    input_length = len(body_text.split())
    dynamic_max_length = max(int(input_length * 0.7), 30) if input_length < 250 else 250

    # Generate summary and replace 'body_text'
    summary = summarizer(
        body_text,
        max_length=dynamic_max_length,
        min_length=80,
        do_sample=False
    )[0]['summary_text']

    item['body_text'] = sentence_case(summary)
    
    # Add valid item to the filtered list
    filtered_news_data.append(item)

# Group articles by category
grouped_data = defaultdict(list)
for item in filtered_news_data:
    category = item.get('category', 'General').capitalize()
    grouped_data[category].append(item)

# Combine date and grouped categories at top level
output_with_date = {
    "date": datetime.today().strftime("%Y-%m-%d"),
    **grouped_data  # Unpack categories at the top level
}

# Save to JSON
with open(r'C:\Users\tanma\OneDrive\Desktop\Data Engineering\Uberblick\news.json', "w", encoding="utf-8") as f:
    json.dump(output_with_date, f, ensure_ascii=False, indent=4)

print("✅ Grouped and summarized JSON with separate top-level date saved as 'news.json'.")
