import os
import csv
from bs4 import BeautifulSoup

def parse_gepris_html(html):
    soup = BeautifulSoup(html, "lxml")
    fields = {}

    # Project title
    h1 = soup.select_one("div.details h1.facelift")
    if h1:
        fields["Projekt"] = h1.get_text(strip=True)

    # All label/value pairs in the "details" block
    for div in soup.select("div.details > div, div.details > div.firstUnderAntragsbeteiligte, div.details > div.projektnummer"):
        label = div.find("span", class_="name")
        value = div.find("span", class_="value")
        if label and value:
            label_text = label.get_text(strip=True).replace(":", "")
            value_text = value.get_text(" ", strip=True)
            fields[label_text] = value_text

    # Project description
    desc = soup.select_one("div#projekttext")
    if desc:
        fields["Projektbeschreibung"] = desc.get_text(" ", strip=True)

    # Other label/value pairs in the "projektbeschreibung" block
    for div in soup.select("div#projektbeschreibung > div"):
        label = div.find("span", class_="name")
        value = div.find("span", class_="value")
        if label and value:
            label_text = label.get_text(strip=True).replace(":", "")
            value_text = value.get_text(" ", strip=True)
            fields[label_text] = value_text

    return fields

def aggregate_all_html(input_dir, output_file):
    all_rows = []
    all_keys = set()
    for fname in os.listdir(input_dir):
        if fname.endswith(".html"):
            with open(os.path.join(input_dir, fname), encoding="utf-8") as f:
                html = f.read()
            fields = parse_gepris_html(html)

            # --- Combine Antragsteller fields ---
            antragsteller_vals = set()
            for k in ['Antragsteller', 'Antragstellerin', 'Antragsteller/in']:
                v = fields.get(k, '')
                if v:
                    antragsteller_vals.add(v)
            fields['Antragsteller/in'] = ' ; '.join(sorted(antragsteller_vals)) if antragsteller_vals else ''
            for k in ['Antragsteller', 'Antragstellerin']:
                fields.pop(k, None)

            # --- Combine Institution fields ---
            inst_vals = set()
            for k in ['Antragstellende Institution', 'Beteiligte Institution']:
                v = fields.get(k, '')
                if v:
                    inst_vals.add(v)
            fields['Institution(en)'] = ' ; '.join(sorted(inst_vals)) if inst_vals else ''
            for k in ['Antragstellende Institution', 'Beteiligte Institution']:
                fields.pop(k, None)

            all_rows.append(fields)
            all_keys.update(fields.keys())
    all_keys = sorted(all_keys)
    with open(output_file, "w", encoding="utf-8-sig", newline='') as out:
        writer = csv.DictWriter(out, fieldnames=all_keys, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)
    print(f"Aggregated {len(all_rows)} HTML files into {output_file}")

if __name__ == "__main__":
    INPUT_DIR = r"C:\workspace\SCAI\web_crawler\data\html_test"
    OUTPUT_FILE = os.path.join(INPUT_DIR, "all_projects.csv")
    aggregate_all_html(INPUT_DIR, OUTPUT_FILE)