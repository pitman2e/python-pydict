import opencc

converter = opencc.OpenCC('s2t.json')

def to_traditional_cond(txt: str) -> str:
    rtv = ""
    # The dictionary's value has no usage, just for reference
    excluded_c = {
        "出": "齣",
        "面": "麵",
        "表": "錶",
        "曲": "麯",
        "回": "迴",
        "借": "藉",
        "向": "嚮",
        "旋": "鏇",
        "合": "閤",
        "別": "彆",
        "才": "纔",
        "了": "瞭",
        "志": "誌",
        "蔑": "衊",
        "家": "傢",
        #"干": "乾",
    }

    for c in txt:
        if c in excluded_c:
            rtv = rtv + c
        else:
            rtv = rtv + converter.convert(c)

    return rtv
