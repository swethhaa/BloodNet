import os

template_dir = r"c:\Users\sweth\Desktop\bloodbankproject\templates"

for filename in os.listdir(template_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Add Logout button to navbar if it's the admin navbar
        # We look for the "Requests" button and append the Logout button after it
        if 'href="/requests"' in content and 'href="/logout"' not in content:
            content = content.replace(
                '<a href="/requests" class="btn btn-outline-light border-0 px-3 fw-semibold">Requests</a>',
                '<a href="/requests" class="btn btn-outline-light border-0 px-3 fw-semibold">Requests</a>\n            <a href="/logout" class="btn btn-outline-light border-0 px-3 fw-semibold text-warning">Logout</a>'
            )
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
print("Added Logout button to navbars.")
