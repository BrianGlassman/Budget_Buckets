"""Script to help find unbalanced internal transfers"""

import _collections_abc

import Record
import Parsing
import Functionified as fn
from Root import Buckets

transactions = Parsing.run()
categorized_transactions = fn.categorize(transactions, cat_filter=Buckets.internal_categories, keep_filter=True,
    use_cat=True, use_uncat=True, use_internal=True)

class Match:
    # Ordering doesn't actually matter
    fidx: int
    first: Record.CategorizedRecord
    midx: int
    match: Record.CategorizedRecord
    def __init__(self, fidx, first, midx, match) -> None:
        self.fidx = fidx
        self.first = first
        self.midx = midx
        self.match = match

class MatchSet(_collections_abc.Sequence):
    items: list[Match]
    indices: set[int]
    def __init__(self) -> None:
        super().__init__()
        self.items = []
        self.indices = set()

    def add(self, item: Match):
        self.items.append(item)
        assert item.fidx not in self.indices
        self.indices.add(item.fidx)
        assert item.midx not in self.indices
        self.indices.add(item.midx)

    def __contains__(self, value: int) -> bool:
        return self.indices.__contains__(value)
    
    def __getitem__(self):
        return None

    def __len__(self) -> int:
        assert len(self.indices) == 2*len(self.items), f"{len(self.indices)} != 2 * {len(self.items)}"
        return len(self.indices)

matches = MatchSet()
matched = []
unmatched = []
for i, t in enumerate(categorized_transactions):
    # Skip transactions that have already been matched
    if i in matches: continue

    found = False
    for j, m in enumerate(categorized_transactions[i+1:]):
        m_idx = i+j+1
        if m_idx in matches: continue

        # Matches have the opposite values, in different accounts
        if (round(t.value, 2) == -round(m.value, 2)
            and
            t.account != m.account):
            if t.account in ('529', 'Student Loans') and m.account in ('529', 'Student Loans'):
                # Should never be any direct transfers between these accounts
                continue

            matches.add(Match(i, t, m_idx, m)) # Have to account for the offset start of iteration
            matched.append(i)
            matched.append(m_idx)
            found = True
            break
    if not found:
        unmatched.append(i)


# Note: Can sometimes falsely identify matches (ex. Checking -> 529, 529 -> CU, mixes up which one matches with which)
# But it (probably) doesn't matter, since the final values should still end up right

print(f"{len(categorized_transactions)} transactions: {len(matches)} matched, {len(unmatched)} unmatched")
print(f"  matched: {[i for i in matched]}")
print(f"unmatched: {[i for i in unmatched]}")
for i in unmatched:
    print(categorized_transactions[i])

# print('---------')
# for x in categorized_transactions:
#     if round(abs(x.value), 2) != 7735.34: continue
#     print(x)