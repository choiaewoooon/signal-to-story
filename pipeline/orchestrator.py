from pipeline.types import Signal
from pipeline.stage2_script import generate_script
from pipeline.stage3_compliance import check
from pipeline.stage4_storyboard import generate_storyboard
from pipeline.stage5_conversion import design_conversion


class Pipeline:
    def __init__(self, claude, image_client, out_dir: str):
        self._claude = claude
        self._image = image_client
        self._out_dir = out_dir
        self.state = "INIT"
        self.signal = None
        self.script = None
        self.report = None
        self.storyboard = None
        self.conversion = None

    def run_until_gate(self, signal: Signal):
        self.signal = signal
        self.script = generate_script(signal, self._claude)
        self.report = check(self.script, self._claude)
        self.state = "AWAITING_APPROVAL"

    def approve(self):
        assert self.state == "AWAITING_APPROVAL"
        self.state = "APPROVED"

    def reject(self):
        assert self.state == "AWAITING_APPROVAL"
        self.state = "REJECTED"

    def resume(self):
        assert self.state == "APPROVED"
        self.storyboard = generate_storyboard(self.script, self._image, self._out_dir)
        self.conversion = design_conversion(self.signal, self.script)
        self.state = "DONE"
