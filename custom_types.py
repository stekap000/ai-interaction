class Model:
    def __init__(self, author, name, model, context_size, free):
        self.author = author
        self.name = name
        self.model = model
        self.context_size = context_size
        self.free = free

    def code_string(self):
        return " Model(\"" + self.author + "\", \"" + self.name + "\", \"" + self.model + "\", " + str(self.context_size) + ", " + str(self.free) + ")"
