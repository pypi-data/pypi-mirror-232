import json

class slider:
    def __init__(self, min = 0, max = 1, step = 0.01) -> None:
        self.min = min
        self.max = max
        self.step = step

    def __str__(self) -> str:
        return json.dumps({
            "min": self.min,
            "max": self.max,
            "step": self.step
        })