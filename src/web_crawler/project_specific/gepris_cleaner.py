import os
import re

def parse_fields(text):
    """
    Extracts all key-value pairs where a line begins with a label (capitalized, possibly with special characters)
    followed by its value.
    """
    fields = {}
    lines = text.split('\n')
    # Regex: start of line, label (letters, spaces, slashes, hyphens), at least one space, then value
    field_pattern = re.compile(r"^([A-ZÄÖÜ][A-Za-zÄÖÜäöüß0-9\s\-/\.]+?)\s{1,3}(.+)$")
    current_key = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = field_pattern.match(line)
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip()
            fields[key] = value
            current_key = key
        elif current_key:
            # If the line doesn't start a new field but follows a key, treat as continuation (for multiline values)
            fields[current_key] += " " + line
    return fields

def process_all(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if fname.endswith(".txt") or fname.endswith(".html"):
            with open(os.path.join(input_dir, fname), encoding="utf-8") as f:
                text = f.read()
            fields = parse_fields(text)
            # Save as TSV (all fields found, including new/unexpected ones)
            outname = fname.replace('.txt','.tsv').replace('.html','.tsv')
            with open(os.path.join(output_dir, outname), "w", encoding="utf-8") as out:
                for k, v in fields.items():
                    out.write(f"{k}\t{v}\n")
            print(f"Extracted: {fname}")

if __name__ == "__main__":
    # Adjust these paths as needed
    INPUT_DIR = r"C:\workspace\SCAI\web_crawler\data\gepris_projects_test\cleaned_txt"
    OUTPUT_DIR = os.path.join(INPUT_DIR, "structured_flexible")
    process_all(INPUT_DIR, OUTPUT_DIR)