import http.server
import socketserver
import os
import re
import json
import glob

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def parse_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = os.path.basename(file_path)
    date_match = re.search(r'producthunt-daily-(\d{4}-\d{2}-\d{2})\.md', filename)
    date_str = date_match.group(1) if date_match else "Unknown Date"
    
    # Split content by products
    parts = re.split(r'\n## \[', content)
    
    products = []
    
    # Skip the first part (header)
    for part in parts[1:]:
        part = '## [' + part
        
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
        "filename": filename # Use md filename as key/id
    }

def get_all_data():
    md_files = glob.glob(os.path.join(DATA_DIR, 'producthunt-daily-*.md'))
    all_data = []
    
    for md_file in md_files:
        try:
            data = parse_markdown_file(md_file)
            all_data.append(data)
        except Exception as e:
            print(f"Error parsing {md_file}: {e}")

    # Sort by date descending
    all_data.sort(key=lambda x: x['date'], reverse=True)
    
    # Construct response structure
    response_data = {
        "index": [],
        "details": {}
    }
    
    for entry in all_data:
        # We use the md filename as the ID/key now, to avoid confusion with non-existent json files
        key = entry['filename'] 
        
        top_product = entry['products'][0] if entry['products'] else {}
        response_data["index"].append({
            "date": entry['date'],
            "title": f"PH今日热榜 | {entry['date']}",
            "top_product": {
                "name": top_product.get('name', ''),
                "tagline": top_product.get('tagline', ''),
                "image_url": top_product.get('image_url', '')
            },
            "filename": key
        })
        
        response_data["details"][key] = {
            "date": entry['date'],
            "products": entry['products']
        }
        
    return response_data

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # Allow CORS if needed
            self.end_headers()
            
            data = get_all_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        else:
            super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at port {PORT}")
        print(f"Open http://localhost:{PORT} in your browser")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()
