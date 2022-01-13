class DictResult:
    def __init__(self, word: str = "", definition: str = "", suggestion: str = "", is_success: bool = False) -> None:
        self.definition = definition
        self.suggestion = suggestion
        self.word = word
        self.is_success = is_success