from hanziconv import HanziConv


class DictResult:
    def __init__(self, word: str = "", definition: str = "", suggestion: str = "", is_success: bool = False) -> None:
        self.definition_raw = definition
        self.definition = definition
        self.definition_tc = HanziConv.toTraditional(definition)
        self.suggestion = suggestion
        self.word = word
        self.is_success = is_success

    def __init__(self, word: str = "", definition_raw: str = "", definition: str = "", suggestion: str = "", is_success: bool = False) -> None:
        self.definition_raw = definition_raw
        self.definition = definition
        self.definition_tc = HanziConv.toTraditional(definition)
        self.suggestion = suggestion
        self.word = word
        self.is_success = is_success