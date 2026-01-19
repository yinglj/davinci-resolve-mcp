from src.agent.executor.skills.import_and_tag_assets import import_assets, query_assets_by_tag, ASSET_DB


def test_import_assets_basic():
    ASSET_DB.clear()
    res = import_assets(['/tmp/nonexistent.mp4'], metadata={'tags': ['b-roll']})
    assert len(res) == 1
    aid = res[0]['id']
    assert ASSET_DB[aid]['metadata']['tags'] == ['b-roll']


def test_query_by_tag():
    ASSET_DB.clear()
    import_assets(['/tmp/f1.mp4'], metadata={'tags': ['hero']})
    import_assets(['/tmp/f2.mp4'], metadata={'tags': ['b-roll']})
    res = query_assets_by_tag('hero')
    assert len(res) == 1
    assert res[0]['metadata']['tags'] == ['hero']
