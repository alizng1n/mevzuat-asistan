import os
import markdown
import sys

# Paths
md_path = r"C:\Users\Acer\.gemini\antigravity\brain\bfccaca4-267e-476b-8eef-a1eb948f1599\artifacts\proje_raporu.md"
doc_path = r"C:\Users\Acer\Desktop\Proje_Raporu.doc"

# Read markdown
with open(md_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Convert to HTML with extensions for tables
html = markdown.markdown(text, extensions=['tables'])

# Wrap in basic HTML structure with UTF-8 meta tag so Word renders it correctly
full_html = f"""
<html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
<head>
    <meta charset="utf-8">
    <title>Proje Raporu</title>
    <style>
        body {{ font-family: 'Calibri', sans-serif; font-size: 11pt; line-height: 1.5; }}
        h1, h2, h3 {{ font-family: 'Calibri', sans-serif; }}
        h1 {{ text-align: center; font-size: 18pt; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ border: 1px solid black; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    {html}
</body>
</html>
"""

# Write to .doc file (Word will interpret the HTML content)
with open(doc_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"Successfully converted to {doc_path}")
