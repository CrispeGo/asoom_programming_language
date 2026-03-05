import os
import shutil
from flask import Flask, render_template, request, jsonify

# NAYA IMPORT: Tera Master Asoom Compiler
import asoom_compiler

app = Flask(__name__)

# ==========================================
# WORKSPACE SETUP
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(BASE_DIR, "user_workspace")

if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR)

# ==========================================
# SECURITY: SAFE PATH FUNCTION
# ==========================================
def safe_path(relative_path):
    # Normalize path
    normalized = os.path.normpath(relative_path)
    full_path = os.path.join(WORKSPACE_DIR, normalized)

    # Prevent path traversal
    if not full_path.startswith(WORKSPACE_DIR):
        raise Exception("Invalid path detected!")

    return full_path


# ==========================================
# 1. UI ROUTE
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# 2. RUN API (Asoom Engine Connected)
# ==========================================
@app.route("/api/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code", "")

    if not code.strip():
        return jsonify({
            "status": "error",
            "terminal_log": "Error: Code khali hai bhai!"
        })

    try:
        # Pura code Asoom Compiler ke paas bhej diya
        compiled_data = asoom_compiler.compile_asoom(code)
        
        # HTML aur baki frontend code nikal liya
        final_web_code = compiled_data["html"]
        log_msg = "Asoom Build Success! 🚀 Live preview ready."

        return jsonify({
            "status": "success",
            "output_html": final_web_code,
            "terminal_log": log_msg
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "terminal_log": f"Engine Crash: {str(e)}"
        })


# ==========================================
# 3. SAVE FILE
# ==========================================
@app.route("/api/save", methods=["POST"])
def save_file():
    data = request.json
    filename = data.get("filename")
    code = data.get("code", "")

    if not filename:
        return jsonify({"status": "error", "message": "Filename missing"}), 400

    try:
        file_path = safe_path(filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        return jsonify({"status": "success", "message": "File saved successfully"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================
# 4. LOAD FILE
# ==========================================
@app.route("/api/load", methods=["POST"])
def load_file():
    data = request.json
    filename = data.get("filename")

    if not filename:
        return jsonify({"status": "error", "code": ""}), 400

    try:
        file_path = safe_path(filename)

        if not os.path.exists(file_path):
            return jsonify({"status": "not_found", "code": ""})

        with open(file_path, "r", encoding="utf-8") as f:
            return jsonify({"status": "success", "code": f.read()})

    except Exception as e:
        return jsonify({"status": "error", "code": "", "message": str(e)}), 500


# ==========================================
# 5. FILE TREE (NESTED)
# ==========================================
@app.route("/api/tree", methods=["GET"])
def get_tree():
    def build_tree(path, base=""):
        tree = []
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            relative_path = os.path.join(base, item)

            if os.path.isdir(full_path):
                tree.append({
                    "name": item,
                    "path": relative_path,
                    "type": "folder",
                    "children": build_tree(full_path, relative_path)
                })
            else:
                tree.append({
                    "name": item,
                    "path": relative_path,
                    "type": "file"
                })
        return tree

    return jsonify({
        "status": "success",
        "tree": build_tree(WORKSPACE_DIR)
    })


# ==========================================
# 6. CREATE FILE OR FOLDER
# ==========================================
@app.route("/api/create", methods=["POST"])
def create_item():
    data = request.json
    path = data.get("path")
    item_type = data.get("type")

    if not path:
        return jsonify({"status": "error", "message": "Path missing"}), 400

    try:
        full_path = safe_path(path)
        if item_type == "folder":
            os.makedirs(full_path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("")
        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================
# 7. DELETE
# ==========================================
@app.route("/api/delete", methods=["POST"])
def delete_item():
    data = request.json
    path = data.get("path")

    if not path:
        return jsonify({"status": "error"}), 400

    try:
        full_path = safe_path(path)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================
# 8. RENAME
# ==========================================
@app.route("/api/rename", methods=["POST"])
def rename_item():
    data = request.json
    old_path = data.get("old")
    new_path = data.get("new")

    if not old_path or not new_path:
        return jsonify({"status": "error"}), 400

    try:
        old_full = safe_path(old_path)
        new_full = safe_path(new_path)
        os.makedirs(os.path.dirname(new_full), exist_ok=True)
        os.rename(old_full, new_full)
        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# 9. ASOOM LIVE SERVER (For Multi-Page Linking)
# ==========================================
@app.route("/live/<path:filename>")
def live_server(filename):
    try:
        # File ka asli path nikalo
        file_path = safe_path(filename)
        
        if not os.path.exists(file_path):
            return f"<h1 style='color:red;'>Error 404</h1><p>Bhai, <b>{filename}</b> naam ki koi file nahi mili!</p>", 404

        # File read karo
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Agar Asoom file hai, toh compile karke uska HTML return karo
        if filename.endswith(".asoom"):
            compiled_data = asoom_compiler.compile_asoom(code)
            return compiled_data["html"]
        
        # Agar koi normal file (image, text) hai toh direct bhej do
        from flask import send_file
        return send_file(file_path)

    except Exception as e:
        return f"<h1>Engine Crash</h1><p>{str(e)}</p>", 500
    
# ==========================================
# START SERVER
# ==========================================
if __name__ == "__main__":
    app.run(debug=True, threaded=True)
