from hanziconv import HanziConv


def to_traditional_cond(txt: str) -> str:
    rtv = ""
    # The dictionary's value has no usage, just for reference
    excluded_c = {
        "出", "齣",
        "面", "麵",
        "表", "錶",
        "曲", "麯",
        "回", "迴",
        "借", "藉",
        "向", "嚮",
    }

    for c in txt:
        if c in excluded_c:
            rtv = rtv + c
        else:
            rtv = rtv + HanziConv.toTraditional(c)

    return rtv
