import os
import re
import json
import glob
from datetime import datetime

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INDEX_HTML_PATH = os.path.join(BASE_DIR, 'index.html')

def parse_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(file_path)
    date_match = re.search(r'producthunt-daily-(\d{4}-\d{2}-\d{2})\.md', filename)
    date_str = date_match.group(1) if date_match else "Unknown Date"
    
    # Split content by products
    # The first part is the header, subsequent parts are products
    parts = re.split(r'\n## \[', content)
    
    products = []
    
    # Skip the first part (header)
    for part in parts[1:]:
        # Add back the bracket removed by split
        part = '[' + part
        
        # Parse product details
        name_match = re.search(r'## \[\d+\. (.*?)\]', part)
        tagline_match = re.search(r'\*\*标语\*\*：(.*?)\n', part)
        desc_match = re.search(r'\*\*介绍\*\*：(.*?)\n', part)
        url_match = re.search(r'\*\*产品网站\*\*.*?\[立即访问\]\((.*?)\)', part)
        image_match = re.search(r'!\[.*?\]\((.*?)\)', part)
        keywords_match = re.search(r'\*\*关键词\*\*：(.*?)\n', part)
        votes_match = re.search(r'\*\*票数\*\*.*?[🔺^](\d+)', part)
        
        rank_match = re.search(r'## \[(\d+)\.', part)
        
        if name_match:
            product = {
                "rank": int(rank_match.group(1)) if rank_match else 0,
                "name": name_match.group(1),
                "tagline": tagline_match.group(1) if tagline_match else "",
                "description": desc_match.group(1) if desc_match else "",
                "votes_count": int(votes_match.group(1)) if votes_match else 0,
                "image_url": image_match.group(1) if image_match else "",
                "url": url_match.group(1) if url_match else "",
                "keywords": keywords_match.group(1) if keywords_match else ""
            }
            products.append(product)
            
    return {
        "date": date_str,
        "products": products,
        "filename": filename.replace('.md', '.json') # keep json extension for compatibility with existing logic
    }

def main():
    print(f"Scanning {DATA_DIR} for markdown files...")
    md_files = glob.glob(os.path.join(DATA_DIR, 'producthunt-daily-*.md'))
    
    all_data = []
    
    for md_file in md_files:
        print(f"Parsing {os.path.basename(md_file)}...")
        try:
            data = parse_markdown_file(md_file)
            all_data.append(data)
        except Exception as e:
            print(f"Error parsing {md_file}: {e}")

    # Sort by date descending
    all_data.sort(key=lambda x: x['date'], reverse=True)
    
    # Construct INLINE_DATA structure
    inline_data = {
        "index": [],
        "details": {}
    }
    
    for entry in all_data:
        # Add to index
        top_product = entry['products'][0] if entry['products'] else {}
        inline_data["index"].append({
            "date": entry['date'],
            "title": f"PH今日热榜 | {entry['date']}",
            "top_product": {
                "name": top_product.get('name', ''),
                "tagline": top_product.get('tagline', ''),
                "image_url": top_product.get('image_url', '')
            },
            "filename": entry['filename']
        })
        
        # Add to details
        inline_data["details"][entry['filename']] = {
            "date": entry['date'],
            "products": entry['products']
        }
        
    # Read index.html
    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # Replace INLINE_DATA
    # Match "const INLINE_DATA = { ... };" (handling nested braces is tricky with regex, 
    # but since we formatted it nicely before, we can try to match from start to the variable declaration end)
    
    # We'll construct the new JS object string
    new_json_str = json.dumps(inline_data, ensure_ascii=False, indent=4)
    new_inline_data_decl = f"const INLINE_DATA = {new_json_str};"
    
    # Use regex to find the block. We assume it starts with "const INLINE_DATA = {" and ends with "};" 
    # and is followed by "async function fetchIndex"
    pattern = r'const INLINE_DATA = \{[\s\S]*?\};'
    
    if re.search(pattern, html_content):
        new_html_content = re.sub(pattern, new_inline_data_decl, html_content)
        
        with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(new_html_content)
        print(f"Successfully updated {INDEX_HTML_PATH} with {len(all_data)} days of data.")
    else:
        print("Could not find INLINE_DATA block in index.html")

if __name__ == "__main__":
    main()
