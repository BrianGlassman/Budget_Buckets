
def read_commented_csv(filename: str):
    """Reads a CSV with comments (lines starting with #) and removes the comments"""
    with open(filename, 'r', newline='') as f:
        lines = [line.strip() for line in f.readlines()]
    lines = [line for line in lines if line] # Remove empty lines
    lines = [line for line in lines if not line.startswith('#')] # Remove comment lines
    return lines
