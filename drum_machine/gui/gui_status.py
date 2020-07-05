class GUIStatus:
        def __init__(self):
                self.not_exited = True

        def exit(self):
                self.not_exited = False

        def is_not_exited(self):
                return self.not_exited
