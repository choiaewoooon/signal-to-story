from pipeline.types import Signal, Script, ConversionDesign


def design_conversion(signal: Signal, script: Script) -> ConversionDesign:
    cta_text = f"{signal.name} 상세 보기 →"
    deeplink = f"nextsec://stock/{signal.ticker}?utm_source=shorts&utm_campaign=signal_demo"
    metrics = {
        "Watchtime": {"정의": "영상 평균 시청 시간", "목표": "≥ 7초/15초", "목업": "8.4초"},
        "CTR": {"정의": "CTA 노출 대비 클릭률", "목표": "≥ 4%", "목업": "5.1%"},
        "Conversion": {"정의": "클릭 → 앱 내 종목 상세 진입", "추적": "딥링크+UTM", "목업": "1.9%"},
    }
    return ConversionDesign(cta_text=cta_text, deeplink=deeplink, metrics=metrics)
