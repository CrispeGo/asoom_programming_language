def transpile(code: str):
    output = []
    
    for line in code.split("\n"):
        stripped = line.strip()
        
        # Agar line khali hai
        if not stripped:
            output.append("")
            continue
            
        # Line ke aage ke spaces (indentation) bachane ke liye
        indent = line[:len(line) - len(stripped)]
        
        # Asoom Logic ko JS mein badalna
        if stripped.startswith("maan "):
            new_line = stripped.replace("maan ", "let ", 1)
            # Agar semi-colon nahi hai toh laga do
            if not new_line.endswith(";"):
                new_line += ";"
            output.append(indent + new_line)
            
        elif stripped.startswith("bol("):
            new_line = stripped.replace("bol(", "console.log(", 1)
            if not new_line.endswith(";"):
                new_line += ";"
            output.append(indent + new_line)
            
        else:
            # Baaki ka normal JS jaisa hai waisa hi rakho
            output.append(line)

    return "\n".join(output)