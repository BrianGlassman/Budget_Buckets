def cat_then_desc(transactions):
    """Group together by Category, then description
    Sort to have the largest groups first"""
    annotated = ((t.category + "<>" + t.desc, t) for t in transactions)
    grouped = {}
    for key, t in annotated:
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(t)

    _sorted = sorted(grouped.items(), key=lambda item: len(item[1]))
    _reversed = reversed(_sorted)

    ret = []
    for _,v in _reversed:
        ret.extend(v)
    return ret

def by_date(transactions):
    """Sort by date"""
    return sorted(transactions, key=lambda item: item.date, reverse=True)