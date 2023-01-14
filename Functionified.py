def categorize(transactions, cat_filter = [], keep_filter=True, limit = 0, use_uncat = True, use_cat = True):
    """
    cat_filter - list of categories to include/exclude
    keep_filter - if False, exclude the categories in cat_filter. If True, include only those categories
    limit = 0 # Use 0 for all
    use_uncat = True # Whether to show uncategorized items
    use_cat = True # Whether to show categorized items
    """
    import Categorize

    categorized_transactions = Categorize.run(
        transactions=transactions, limit=limit, use_uncat=use_uncat, use_cat=use_cat, use_internal=False)

    categorized_transactions = [x for x in categorized_transactions if
        (x.category in cat_filter) == keep_filter # weird boolean logic to make filtering work correctly
        ]
    
    return categorized_transactions