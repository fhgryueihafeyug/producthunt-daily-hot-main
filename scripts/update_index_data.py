import os
import json
import re

def parse_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Date from Title
    title_match = re.search(r'# PH今日热榜 \| (\d{4}-\d{2}-\d{2})', content)
    date_str = title_match.group(1) if title_match else "Unknown"

    products = []
    sections = re.split(r'\n## ', content)
    
    for section in sections[1:]:
        product = {}
        
        name_match = re.match(r'\[(\d+)\.\s+(.*?)\]\((.*?)\)', section)
        if name_match:
            product['rank'] = int(name_match.group(1))
            product['name'] = name_match.group(2)
            product['url'] = name_match.group(3)
        
        tagline_match = re.search(r'\*\*标语\*\*：(.*?)\n', section)
        if tagline_match:
            product['tagline'] = tagline_match.group(1).strip()
            
        desc_match = re.search(r'\*\*介绍\*\*：(.*?)\n', section)
        if desc_match:
            product['description'] = desc_match.group(1).strip()
            
        img_match = re.search(r'!\[.*?\]\((.*?)\)', section)
        if img_match:
            product['image_url'] = img_match.group(1).split('?')[0] + "?auto=format"
            
        votes_match = re.search(r'\*\*票数\*\*: 🔺(\d+)', section)
        if votes_match:
            product['votes_count'] = int(votes_match.group(1))
            
        keywords_match = re.search(r'\*\*关键词\*\*：(.*?)\n', section)
        if keywords_match:
            product['keywords'] = keywords_match.group(1).strip()

        if 'name' in product:
            products.append(product)

    return {
        'date': date_str,
        'products': products
    }

def update_html_file(html_path, data):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Prepare new INLINE_DATA structure
    date_str = data['date']
    filename = f"producthunt-daily-{date_str}.json"
    
    top_product = data['products'][0] if data['products'] else {}
    
    new_inline_data = {
        "index": [
            {
                "date": date_str,
                "title": f"PH今日热榜 | {date_str}",
                "top_product": {
                    "name": top_product.get('name'),
                    "tagline": top_product.get('tagline'),
                    "image_url": top_product.get('image_url')
                },
                "filename": filename
            }
        ],
        "details": {
            filename: data
        }
    }
    
    # Convert to JSON string with indentation
    json_str = json.dumps(new_inline_data, ensure_ascii=False, indent=4)
    
    # Replace the INLINE_DATA constant in HTML
    # We look for: const INLINE_DATA = { ... };
    # Using regex with DOTALL to match multiline
    pattern = r'const INLINE_DATA = \{.*?\};'
    replacement = f'const INLINE_DATA = {json_str};'
    
    new_html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html_content)
    
    print(f"Successfully updated {html_path} with {len(data['products'])} products.")

def main():
    md_file = 'data/producthunt-daily-2026-01-12.md'
    html_file = 'index.html'
    
    if os.path.exists(md_file) and os.path.exists(html_file):
        data = parse_markdown_file(md_file)
        update_html_file(html_file, data)
    else:
        print("Files not found.")

if __name__ == '__main__':
    main()
