import re

with open(r'c:\Coding\soengkanel.github.io\slide\hrlab\slides.md', 'r', encoding='utf-8') as f:
    text = f.read()

tokens = ['<div', '</div>', '<span', '</span>', '<template', '</template>', '<table', '</table>', '<tr', '</tr>', '<td', '</td>', '<th', '</th>', '<h1', '</h1>', '<h2', '</h2>', '<h3', '</h3>', '<p', '</p>', '<ul', '</ul>', '<li', '</li>']

for t in tokens:
    if t.startswith('</'):
        count = text.count(t)
    else:
        # Avoid counting </div as <div
        count = len(re.findall(f'{re.escape(t)}(?![a-zA-Z0-9/])', text))
    print(f"{t}: {count}")
