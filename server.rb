require 'webrick'
require 'json'
require 'date'

PORT = 8000
BASE_DIR = File.expand_path(File.dirname(__FILE__))
DATA_DIR = File.join(BASE_DIR, 'data')

def parse_markdown_file(file_path)
  content = File.read(file_path, encoding: 'utf-8')
  filename = File.basename(file_path)
  
  date_match = filename.match(/producthunt-daily-(\d{4}-\d{2}-\d{2})\.md/)
  date_str = date_match ? date_match[1] : "Unknown Date"
  
  # Split content by products
  parts = content.split("\n## [")
  
  products = []
  
  # Skip the first part (header)
  parts[1..-1].each do |part|
    part = '## [' + part
    
    name_match = part.match(/## \[\d+\. (.*?)\]/)
    tagline_match = part.match(/\*\*标语\*\*：(.*?)\n/)
    desc_match = part.match(/\*\*介绍\*\*：(.*?)\n/)
    url_match = part.match(/\*\*产品网站\*\*.*?\[立即访问\]\((.*?)\)/)
    image_match = part.match(/!\[.*?\]\((.*?)\)/)
    keywords_match = part.match(/\*\*关键词\*\*：(.*?)\n/)
    votes_match = part.match(/\*\*票数\*\*.*?[🔺^](\d+)/)
    rank_match = part.match(/## \[(\d+)\./)
    
    if name_match
      product = {
        "rank" => rank_match ? rank_match[1].to_i : 0,
        "name" => name_match[1],
        "tagline" => tagline_match ? tagline_match[1] : "",
        "description" => desc_match ? desc_match[1] : "",
        "votes_count" => votes_match ? votes_match[1].to_i : 0,
        "image_url" => image_match ? image_match[1] : "",
        "url" => url_match ? url_match[1] : "",
        "keywords" => keywords_match ? keywords_match[1] : ""
      }
      products << product
    end
  end
  
  {
    "date" => date_str,
    "products" => products,
    "filename" => filename # Use md filename as key/id
  }
end

def get_all_data
  md_files = Dir.glob(File.join(DATA_DIR, 'producthunt-daily-*.md'))
  all_data = []
  
  md_files.each do |md_file|
    begin
      data = parse_markdown_file(md_file)
      all_data << data
    rescue => e
      puts "Error parsing #{md_file}: #{e}"
    end
  end

  # Sort by date descending
  all_data.sort_by! { |x| x['date'] }.reverse!
  
  # Construct response structure
  response_data = {
    "index" => [],
    "details" => {}
  }
  
  all_data.each do |entry|
    key = entry['filename']
    top_product = (entry['products'] && entry['products'].first) || {}
    
    response_data["index"] << {
      "date" => entry['date'],
      "title" => "PH今日热榜 | #{entry['date']}",
      "top_product" => {
        "name" => top_product['name'] || '',
        "tagline" => top_product['tagline'] || '',
        "image_url" => top_product['image_url'] || ''
      },
      "filename" => key
    }
    
    response_data["details"][key] = {
      "date" => entry['date'],
      "products" => entry['products']
    }
  end
  
  response_data
end

# Create server
server = WEBrick::HTTPServer.new(:Port => PORT, :DocumentRoot => BASE_DIR)

# API Endpoint
server.mount_proc '/api/data' do |req, res|
  res.content_type = 'application/json'
  res['Access-Control-Allow-Origin'] = '*'
  
  data = get_all_data
  res.body = JSON.generate(data)
end

trap 'INT' do server.shutdown end

puts "Serving at port #{PORT}"
puts "Open http://localhost:#{PORT} in your browser"
server.start
