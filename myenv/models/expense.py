class Expense:
    def __init__(self, exp_id: int, description: str,
                 amount: float, category: str, user_id: int, created_at):
        self.id = exp_id
        self.description = description
        self.amount = amount
        self.category = category
        self.user_id = user_id
        self.created_at = created_at
