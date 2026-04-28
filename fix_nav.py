import os

template_dir = r"c:\Users\sweth\Desktop\bloodbankproject\templates"

for filename in os.listdir(template_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Fix the Donors link in the navbar
        new_content = content.replace('<a href="/" class="btn btn-outline-light border-0 px-3 fw-semibold">Donors</a>', 
                                      '<a href="/donors" class="btn btn-outline-light border-0 px-3 fw-semibold">Donors</a>')
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
            
print("Fixed Donors link in navbar.")
