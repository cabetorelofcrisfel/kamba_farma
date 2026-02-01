class Session:
    def __init__(self):
        self.user = None

    def login(self, user):
        self.user = user

    def logout(self):
        self.user = None
