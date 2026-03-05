import re

# ==========================================
# ASOOM HTML ENGINE (BAAP LEVEL) - FULL VERSION
# ==========================================
class AsoomHTMLTranspiler:
    def __init__(self):
        # Yeh list yaad rakhegi ki kaunse tags open hain (Nesting ke liye)
        self.tag_stack = []
        self.output = []

    def parse_attributes(self, line, command):
        """
        UNIVERSAL ATTRIBUTE PARSER:
        Yeh function line se tag ka naam hatayega, aur usme se `text=".."` ko alag karega.
        """
        # Command word ko hatao (jaise 'btn ', 'box ')
        remain = re.sub(r'^' + command + r'\b\s*', '', line).strip()
        
        text_val = ""
        # Pehle check karo agar direct double quotes mein text ho -> txt "Hello"
        direct_text_match = re.match(r'^"(.*?)"(.*)', remain)
        
        # Phir check karo agar text="..." format mein ho -> btn text="Click"
        named_text_match = re.search(r'text="(.*?)"', remain)
        
        if direct_text_match:
            text_val = direct_text_match.group(1)
            remain = direct_text_match.group(2).strip()
        elif named_text_match:
            text_val = named_text_match.group(1)
            remain = re.sub(r'text=".*?"', '', remain).strip()
            
        attr_str = f" {remain}" if remain else ""
        return text_val, attr_str

    def open_tag(self, tag, attrs=""):
        """Naya tag open karo aur stack mein daal do"""
        self.tag_stack.append(tag)
        self.output.append(f"<{tag}{attrs}>")

    def close_tag(self, force_tag=None):
        """Stack mein se sabse upar wala tag nikal kar close karo"""
        if not self.tag_stack:
            return

        if force_tag:
            if self.tag_stack[-1] == force_tag:
                closed_tag = self.tag_stack.pop()
                self.output.append(f"</{closed_tag}>")
            else:
                self.output.append(f"<!-- Asoom Warning: Expected </{self.tag_stack[-1]}> but got </{force_tag}> -->")
        else:
            closed_tag = self.tag_stack.pop()
            self.output.append(f"</{closed_tag}>")

    def close_all(self):
        """End mein agar bache ne kuch band nahi kiya, toh auto-close kar do"""
        while self.tag_stack:
            closed_tag = self.tag_stack.pop()
            self.output.append(f"</{closed_tag}>")

    def get_html(self):
        """YAHI WOH MISSING FUNCTION THA! Pura HTML code string banake bhejta hai."""
        return "\n".join(self.output)

    # ==========================================
    # MAIN LOGIC: PROCESSING LINES
    # ==========================================
    def process_line(self, line):
        original_line = line
        line = line.strip()

        # ------------------------------------------
        # PART 4: DESI LAYOUTS (FLEXBOX MAGIC)
        # ------------------------------------------
        if line.startswith("katar ") or line == "katar":
            cmd = "katar" if line.startswith("katar ") else ""
            _, attrs = self.parse_attributes(line, cmd)
            if 'style="' in attrs:
                attrs = attrs.replace('style="', 'style="display: flex; ')
            else:
                attrs = f' style="display: flex;"{attrs}'
            self.open_tag("div", attrs)

        elif line.startswith("hissa ") or line == "hissa":
            cmd = "hissa" if line.startswith("hissa ") else ""
            _, attrs = self.parse_attributes(line, cmd)
            if 'style="' in attrs:
                attrs = attrs.replace('style="', 'style="flex: 1; ')
            else:
                attrs = f' style="flex: 1;"{attrs}'
            self.open_tag("div", attrs)
            
        elif line.startswith("kendr ") or line == "kendr":
            cmd = "kendr" if line.startswith("kendr ") else ""
            _, attrs = self.parse_attributes(line, cmd)
            flex_style = "display: flex; justify-content: center; align-items: center;"
            if 'style="' in attrs:
                attrs = attrs.replace('style="', f'style="{flex_style} ')
            else:
                attrs = f' style="{flex_style}"{attrs}'
            self.open_tag("div", attrs)

        # ------------------------------------------
        # PART 1 & 2: STRUCTURAL & BASIC TAGS
        # ------------------------------------------
        # Box / Div (Container)
        elif line.startswith("box ") or line == "box":
            cmd = "box" if line.startswith("box ") else ""
            _, attrs = self.parse_attributes(line, cmd)
            self.open_tag("div", attrs)

        # Universal Close Tag (list_band bhi daal diya tera wala)
        elif line in ["band", "/box", "list_band", "/list"]:
            self.close_tag()

        # Headings (h1 se h6)
        elif re.match(r'^h[1-6]\b', line):
            tag = line[:2]
            text_val, attrs = self.parse_attributes(line, tag)
            self.output.append(f"<{tag}{attrs}>{text_val}</{tag}>")

        # Paragraph (Text)
        elif line.startswith("txt ") or line.startswith("likho "):
            cmd = "txt" if line.startswith("txt ") else "likho"
            text_val, attrs = self.parse_attributes(line, cmd)
            self.output.append(f"<p{attrs}>{text_val}</p>")

        # Buttons
        elif line.startswith("btn ") or line.startswith("batan "):
            cmd = "btn" if line.startswith("btn ") else "batan"
            text_val, attrs = self.parse_attributes(line, cmd)
            if not text_val: text_val = "Asoom Btn"
            self.output.append(f"<button{attrs}>{text_val}</button>")

        # Links
        elif line.startswith("link ") or line.startswith("rasta "):
            cmd = "link" if line.startswith("link ") else "rasta"
            text_val, attrs = self.parse_attributes(line, cmd)
            if not text_val: text_val = "Link"
            self.output.append(f"<a{attrs}>{text_val}</a>")

        # ------------------------------------------
        # PART 3: FORMS, INPUTS, IMAGES & LISTS
        # ------------------------------------------
        # Images (tasveer/pic)
        elif line.startswith("pic ") or line.startswith("tasveer "):
            cmd = "pic" if line.startswith("pic ") else "tasveer"
            _, attrs = self.parse_attributes(line, cmd)
            self.output.append(f"<img{attrs}>")

        # Inputs (dabba/inpt)
        elif line.startswith("inpt ") or line.startswith("dabba "):
            cmd = "inpt" if line.startswith("inpt ") else "dabba"
            _, attrs = self.parse_attributes(line, cmd)
            self.output.append(f"<input{attrs}>")

        # Form Container (parcha)
        elif line.startswith("parcha ") or line == "parcha":
            cmd = "parcha" if line.startswith("parcha ") else ""
            _, attrs = self.parse_attributes(line, cmd)
            self.open_tag("form", attrs)

        # List Container (suchi/list)
        elif line.startswith("suchi ") or line == "suchi" or line == "list":
            cmd = "suchi" if line.startswith("suchi ") else ("list" if line.startswith("list ") else "")
            _, attrs = self.parse_attributes(line, cmd)
            self.open_tag("ul", attrs)

        # List Item
        elif line.startswith("item ") or line.startswith("bindu "):
            cmd = "item" if line.startswith("item ") else "bindu"
            text_val, attrs = self.parse_attributes(line, cmd)
            self.output.append(f"<li{attrs}>{text_val}</li>")
            
        # ------------------------------------------
        # PART 5: TYPOGRAPHY & EXTRA
        # ------------------------------------------
        # Bold Text (mota)
        elif line.startswith("mota "):
            text_val, attrs = self.parse_attributes(line, "mota")
            self.output.append(f"<b{attrs}>{text_val}</b>")
            
        # Line Break (br/khali)
        elif line == "br" or line == "khali":
            self.output.append("<br>")

        # MAHA-ASTRA (Fallback)
        else:
            self.output.append(original_line)


# ==========================================
# MAIN EXPORT FUNCTION (Called by Engine)
# ==========================================
def transpile(code: str):
    engine = AsoomHTMLTranspiler()
    
    for line in code.split("\n"):
        line = line.strip()
        if not line:
            continue
            
        engine.process_line(line)
        
    engine.close_all()
    return engine.get_html()