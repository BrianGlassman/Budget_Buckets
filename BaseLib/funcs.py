
def read_commented_csv(filename: str) -> list[str]:
    """Reads a CSV with comments (lines starting with #) and removes the comments
    Note: does NOT split lines"""
    with open(filename, 'r', newline='') as f:
        lines = [line.strip() for line in f.readlines()]
    lines = [line for line in lines if line] # Remove empty lines
    lines = [line for line in lines if not line.startswith('#')] # Remove comment lines
    return lines

def read_flagged_csv(filename: str) -> dict[str, list[str]]:
    """Reads a CSV with comments (lines starting with #) and flags (lines starting with $)
    Returns a dictionary like {flag: [flagged lines]}
    Note: does NOT split lines"""
    lines = read_commented_csv(filename)

    flag = 'HEADER'
    out = {}
    for line in lines:
        if line.startswith('$'):
            flag = line.replace('$', '').strip()
        else:
            if flag not in out:
                out[flag] = []
            out[flag].append(line)
    
    # Header should be one line, or removed
    if len(out['HEADER']) == 0:
        out.pop('HEADER')
    elif len(out['HEADER']) == 1:
        pass
    else:
        raise RuntimeError("Multiple header lines found")
    
    return out
