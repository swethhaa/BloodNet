import os
import re

template_dir = r"c:\Users\sweth\Desktop\bloodbankproject\templates"

new_nav = """<nav class="navbar navbar-dark bg-danger shadow-sm py-3 mb-4 border-bottom border-4 border-danger border-opacity-75">
    <div class="container d-flex justify-content-between align-items-center">
        <a href="/dashboard" class="navbar-brand fw-bold fs-4 mb-0 text-decoration-none">
            <span class="fs-3 me-2">🩸</span>Blood Bank System
        </a>
        <div class="d-flex gap-2 flex-wrap">
            <a href="/dashboard" class="btn btn-outline-light border-0 px-3 fw-semibold">Dashboard</a>
            <a href="/" class="btn btn-outline-light border-0 px-3 fw-semibold">Donors</a>
            <a href="/bloodstock" class="btn btn-outline-light border-0 px-3 fw-semibold">Stock</a>
            <a href="/hospitals" class="btn btn-outline-light border-0 px-3 fw-semibold">Hospitals</a>
            <a href="/requests" class="btn btn-outline-light border-0 px-3 fw-semibold">Requests</a>
        </div>
    </div>
</nav>"""

# Regex to match the old nav block.
# Since it spans multiple lines, we use re.DOTALL
nav_regex = re.compile(r'<nav class="navbar navbar-dark bg-danger">.*?</nav>', re.DOTALL)

for filename in os.listdir(template_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        new_content = nav_regex.sub(new_nav, content)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
            
print("UI updated successfully.")
