from pipeline.stage5_conversion import design_conversion
from pipeline.types import Signal, Script, ConversionDesign


def test_design_conversion_builds_cta_and_metrics():
    sig = Signal(ticker="000000", name="샘플전자", thesis="t", metrics={})
    script = Script(hook="h", cuts=["a"], cta="더보기", disclaimer="d")
    cd = design_conversion(sig, script)
    assert isinstance(cd, ConversionDesign)
    assert "샘플전자" in cd.cta_text
    assert "000000" in cd.deeplink
    assert "Watchtime" in cd.metrics
    assert "Conversion" in cd.metrics
