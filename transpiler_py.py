def transpile(code: str):

    lines = code.split("\n")
    output = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("bol("):
            line = line.replace("bol(", "print(", 1)

        output.append(line)

    return "\n".join(output)