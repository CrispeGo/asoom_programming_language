import re
import traceback

import transpiler_html
import transpiler_css
import transpiler_js
import transpiler_py

# ==========================================
# BAAP LEVEL: Smart Block Extractor
# ==========================================
def extract_block(source_code, block_name):
    # Regex se block dhoondho
    pattern = re.compile(r'\b' + block_name + r'\s*\{')
    match = pattern.search(source_code)
    
    if not match:
        return ""

    start_index = match.end()
    brace_count = 1
    i = start_index

    # Jab tak brackets barabar na ho jayein, code nikalte raho
    while i < len(source_code) and brace_count > 0:
        char = source_code[i]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        i += 1

    if brace_count == 0:
        return source_code[start_index:i-1].strip()
    else:
        return source_code[start_index:].strip()


# ==========================================
# MAIN ASOOM COMPILER ENGINE
# ==========================================
def compile_asoom(code: str):
    
    # 1. Blocks ko smartly alag karna
    blocks = {
        "page": extract_block(code, "page"),
        "style": extract_block(code, "style"),
        "logic": extract_block(code, "logic"),
        "server": extract_block(code, "server")
    }

    # 2. Crash-Proof Transpiler Function
    def safe_transpile(module, code_block, name):
        if not code_block:
            return ""
        try:
            return module.transpile(code_block)
        except Exception as e:
            error_msg = f"Asoom Engine Error ({name} block): {str(e)}"
            print(error_msg) # Backend Console ke liye
            
            # Frontend par error show karne ka nuskha
            if name == "page":
                return f"<div style='color:white; background:red; padding:10px; border-radius:5px;'><b>{error_msg}</b></div>"
            elif name == "logic":
                return f"console.error('{error_msg}');"
            elif name == "style":
                return f"/* {error_msg} */"
            return ""

    # 3. Transpile all blocks safely
    html = safe_transpile(transpiler_html, blocks["page"], "page")
    css = safe_transpile(transpiler_css, blocks["style"], "style")
    js = safe_transpile(transpiler_js, blocks["logic"], "logic")
    
    try:
        py = transpiler_py.transpile(blocks["server"]) if blocks["server"] else ""
    except Exception as e:
        py = f"# Backend Python Error: {str(e)}"

    # 4. Standard HTML5 Production Level Structure
    final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asoom Live Preview</title>
    <style>
/* --- ASOOM CSS ENGINE --- */
{css}
    </style>
</head>
<body>
    {html}
    
    <script>
        // Yeh line ensure karegi ki pure HTML buttons load hone ke baad hi JS chale!
        window.onload = function() {{
            try {{
{js}
            }} catch(err) {{
                console.error("Asoom Logic Runtime Error: " + err.message);
            }}
        }};
    </script>
</body>
</html>"""

    # YAHI WOH LINE HAI JISKE GAYAB HONE SE CRASH HUA THA!
    return {
        "html": final_html,
        "python": py
    }