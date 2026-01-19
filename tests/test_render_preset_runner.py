from src.agent.executor.skills.render_preset_runner import render_timeline


def test_render_simulated_no_resolve():
    res = render_timeline(None, timeline_name='Non', preset={'name': 'YouTube 1080p'})
    assert res['success'] is True


def test_render_with_fake_resolve():
    class FakeT:
        pass
    class FakeProject:
        def GetTimelineByName(self, name):
            if name == 'Exists':
                return FakeT()
            return None
        def GetCurrentTimeline(self):
            return FakeT()
    class FakePM:
        def GetCurrentProject(self):
            return FakeProject()
    class FakeResolve:
        def GetProjectManager(self):
            return FakePM()

    res = render_timeline(FakeResolve(), timeline_name='Exists', preset={'name': 'Test'})
    assert res['success'] is True
    res_no = render_timeline(FakeResolve(), timeline_name='Missing', preset={'name': 'Test'})
    assert res_no['success'] is False
