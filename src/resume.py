class ResumeOnFile:
    def __init__(self, path):
        self.path = path
        self.resume = None

    def load(self):
        with open(self.path, "r") as f:
            self.resume = f.read()




