class DummyResolve:
    def __init__(self):
        self.timelines = {}

    def CreateTimeline(self, name):
        self.timelines[name] = []
        return True


def get_resolve():
    return DummyResolve()
