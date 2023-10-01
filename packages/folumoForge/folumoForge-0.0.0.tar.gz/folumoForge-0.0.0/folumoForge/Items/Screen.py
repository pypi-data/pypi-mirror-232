class Screen:
    def __init__(self, root, name, size):
        self.root = root
        self.name = name
        self.size = size

    def SwitchScreen(self):
        self.root.Screen = self.name

    def DeleteScreen(self):
        ...

    def OnFrame(self):
        ...