class DummyTimeline:
    def __init__(self, name):
        self._name = name
        self._markers = {}

    def GetName(self):
        return self._name

    def GetSetting(self, name):
        # basic defaults for frame rate and resolution
        if name == 'timelineFrameRate':
            return '24'
        if name == 'timelineResolutionWidth':
            return '1920'
        if name == 'timelineResolutionHeight':
            return '1080'
        return None

    def SetStartTimecode(self, tc):
        self._start_tc = tc
        return True

    def AddMarker(self, frame, color, note):
        self._markers[frame] = {'color': color, 'note': note}
        return True

    def GetMarkers(self):
        return self._markers


class DummyMediaPool:
    def __init__(self):
        self.timelines = {}

    def CreateEmptyTimeline(self, name):
        tl = DummyTimeline(name)
        self.timelines[name] = tl
        return tl


class DummyProject:
    def __init__(self):
        self.media_pool = DummyMediaPool()
        self._current_timeline = None

    def GetMediaPool(self):
        return self.media_pool

    def GetCurrentTimeline(self):
        return self._current_timeline

    def SetCurrentTimeline(self, tl):
        self._current_timeline = tl
        return True

    def GetTimelineCount(self):
        return len(self.media_pool.timelines)

    def GetTimelineByIndex(self, i):
        names = list(self.media_pool.timelines.keys())
        if 1 <= i <= len(names):
            return self.media_pool.timelines[names[i - 1]]
        return None

    def GetTimelineByName(self, name):
        return self.media_pool.timelines.get(name)


class DummyProjectManager:
    def __init__(self, project):
        self.project = project

    def GetCurrentProject(self):
        return self.project


class DummyResolve:
    def __init__(self):
        self._pm = DummyProjectManager(DummyProject())

    def GetProjectManager(self):
        return self._pm


def get_resolve():
    return DummyResolve()
