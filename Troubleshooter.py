"""Parses the pages and saves to file"""

# General imports
from pypdf import PdfReader


# Project imports
from BaseLib.utils import safe_open as open


# Dict like {y: {x: [text]}}
content_type = dict[float, dict[float, list]]
def add_content(target: content_type, text, x, y):
    if not text: return
    if y not in target: target[y] = {}
    if x not in target[y]: target[y][x] = []
    target[y][x].append(text)
def sort_content(target: content_type):
    """Sort by coordinates"""
    return sorted(
        {y: sorted(
            x_dict.items(), key=lambda item: item[0]
            )
            for y, x_dict in target.items()
        }.items(),
        key=lambda item: item[0], reverse=True)

def main(filepath: str):
    reader = PdfReader(filepath)
    general: content_type = {}

    def visitor(text: str, cm: list, tm: list, font_dict: dict, font_size: dict):
        """cm - current matrix to move from user coordinate space (also known as CTM)
        tm - current matrix from text coordinate space"""
        # WARNING: visitor is suppressing Exceptions in a weird way

        _, _, _, _, x, y = tm
        add_content(general, text, x, y)
    
    for i, page in enumerate(reader.pages):
        print(f"Page {i}")
        general.clear()
        raw = page.extract_text(visitor_text=visitor)

        text = '\n'.join(f'{y}:{x_dict}' for y,x_dict in sort_content(general))

        with open(f"{i}.txt", 'w') as f:
            f.writelines(text)

if __name__ == "__main__":
    import os
    data_dir = os.path.join('Raw_Data', 'Statements', 'Checking')
    for filename in os.listdir(data_dir)[0:1]:
        filepath = os.path.join(data_dir, filename)
        main(filepath)