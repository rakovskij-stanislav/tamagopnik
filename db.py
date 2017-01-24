import pickle

class db():
    def __init__(self):
        self.base = {} #id - экземпляр player
        self.path = "backup.db"
    def load(self, path=""):
        if path == "": path = self.path
        base_backup = dict(self.base)
        try:
            with open(path) as f:
                self.base = pickle.load(f)
            if str(type(self.base))!="<class 'dict'>":
                raise Exception("NON_DICT")
        except Exception as e:
            self.base = base_backup()
            print("Error while load a backup :", str(e))
        else:
            print("loaded")
    def merge(self, path=''):
        if path == "": path = self.path
        base_backup = dict(self.base)
        try:
            with open(path) as f:
                basem = pickle.load(f)
            if str(type(basem))!="<class 'dict'>":
                raise Exception("NON_DICT_basem")
            self.base.update(basem)
        except Exception as e:
            self.base = base_backup()
            print("Error while load a backup :", str(e))
        else:
            print("Merged")
    def save(self, path=''):
        if path == "": path = self.path
        with open(path, "wb") as f:
            pickle.dump([self.base], f)
        print("Saved")
    def wipe(self):
        self.base = {}
        print("Wiped")

class player():
    def __init__(self):
        self.last_motion = [] #[room,  dialog,  position_in_dialog]
        self.inventory = []
        self.recovery = False #режим восстановления учетной записи
        self.turns = 0
        self.last_activity = 0
        self.waiting_answer = False
