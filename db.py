class db():
    def __init__(self):
        self.base = {} #id - экземпляр player
    def load(self):
        pass
    def save(self):
        pass
    def wipe(self):
        pass

class player():
    def __init__(self):
        self.last_motion = [] #[room,  dialog,  position_in_dialog]
        self.inventory = []
        self.finished_dialogs = []
        self.recovery = False #режим восстановления учетной записи
        self.turns = 0
        self.last_activity = 0
