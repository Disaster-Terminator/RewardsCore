import re
import json
import sys

def find_cards_in_json(data, path=""):
    if isinstance(data, dict):
        # Check if this dict looks like a card
        if "className" in data:
            cls = str(data["className"])
            # Normalize spaces
            cls = ' '.join(cls.split())
            if "rounded-2xl" in cls and "bg-neutralBg1" in cls:
                print(f"\n--- Potential Card Found at {path} ---")
                print(f"Class: {cls}")
                print(f"Content: {str(data)[:500]}")
        
        # Recursively search children
        for k, v in data.items():
            find_cards_in_json(v, f"{path}.{k}")
            
    elif isinstance(data, list):
        for i, item in enumerate(data):
            find_cards_in_json(item, f"{path}[{i}]")
    elif isinstance(data, str):
        # Sometimes JSON is embedded in strings
        if data.strip().startswith('{') and data.strip().endswith('}'):
            try:
                nested = json.loads(data)
                find_cards_in_json(nested, path + "(parsed)")
            except:
                pass

def analyze_html(file_path):
    print(f"Analyzing {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Extract self.__next_f.push calls
    # Pattern: self.__next_f.push([1, "JSON_STRING"])
    matches = re.findall(r'self\.__next_f\.push\(\[(.*?)\]\)', content)
    
    print(f"Found {len(matches)} data pushes.")
    
    for i, match in enumerate(matches):
        try:
            # The match is like: 1, "..."
            # We want to reconstruct it as a valid JSON array if possible
            # Or just extract the string part
            
            # Since the regex might be fragile, let's try a safer approach
            # Just extract the second element which is usually the big payload
            parts = match.split(',', 1)
            if len(parts) < 2:
                continue
                
            payload_str = parts[1].strip()
            
            # Remove surrounding quotes if present
            if payload_str.startswith('"') and payload_str.endswith('"'):
                # This is a JSON string literal
                try:
                    payload = json.loads(payload_str)
                    # Now payload might be a string containing JSON, or an object
                    if isinstance(payload, str):
                        try:
                             # Try to parse it as JSON if it looks like it
                            if payload.strip().startswith('{') or payload.strip().startswith('['):
                                data = json.loads(payload)
                                find_cards_in_json(data, f"Block{i}")
                            else:
                                # It might be a weird format where it's just a string but contains JSON structures
                                # Let's just try to find our target string in it
                                if "rounded-2xl" in payload and "bg-neutralBg1" in payload:
                                     print(f"\n--- Potential Card String in Block {i} ---")
                                     print(payload[:500])
                        except:
                            # If not JSON, just search string
                             if "rounded-2xl" in payload and "bg-neutralBg1" in payload:
                                     print(f"\n--- Potential Card String in Block {i} ---")
                                     print(payload[:500])
                    else:
                        find_cards_in_json(payload, f"Block{i}")
                except Exception as e:
                    # print(f"Error parsing payload in block {i}: {e}")
                    pass
        except Exception as e:
            # print(f"Error processing block {i}: {e}")
            pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_html(sys.argv[1])
    else:
        print("Usage: python analyze_html.py <path_to_html>")
