import os
from pipeline.stage4_storyboard import split_cuts, generate_storyboard
from pipeline.clients import FakeImageClient
from pipeline.types import Script, Storyboard


def _script():
    return Script(hook="후크", cuts=["컷A", "컷B", "컷C"], cta="더보기", disclaimer="d")


def test_split_cuts_prepends_hook():
    cuts = split_cuts(_script())
    assert cuts == ["후크", "컷A", "컷B", "컷C"]


def test_generate_storyboard_makes_one_image_per_cut(tmp_path):
    client = FakeImageClient()
    sb = generate_storyboard(_script(), client, str(tmp_path))
    assert isinstance(sb, Storyboard)
    assert len(sb.cuts) == 4
    assert os.path.exists(sb.cuts[0].image_path)
    assert len(client.calls) == 4
