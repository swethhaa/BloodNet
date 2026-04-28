import os

template_dir = r"c:\Users\sweth\Desktop\bloodbankproject\templates"

for filename in os.listdir(template_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Remove the span with the emoji from the brand
        new_content = content.replace('<span class="fs-3 me-2">🩸</span>', '')
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
            
print("Removed emoji from navbar.")
