def calculate_total(expenses):
    return sum(e["amount"] for e in expenses)

def filter_by_category(expenses, category):
    return [e for e in expenses if e["category"] == category]
