class User:
    def __init__(self, user_id, name, real_name):
        self.user_id = user_id
        self.name = name
        self.real_name = real_name

    def __str__(self):
        return f'{self.real_name if self.real_name else self.name}'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.user_id == other.user_id

    def __hash__(self):
        return hash(self.user_id)