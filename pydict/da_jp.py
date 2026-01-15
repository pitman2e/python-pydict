from pydict.dict_result import DictResult
from bs4 import BeautifulSoup
import requests

from pydict.tc_conv import to_traditional_cond

hiragana_katakana = [
    ["あ", "い", "う", "え", "お"],
    ["か", "き", "く", "け", "こ"],
    ["さ", "し", "す", "せ", "そ"],
    ["た", "ち", "つ", "て", "と"],
    ["な", "に", "ぬ", "ね", "の"],
    ["は", "ひ", "ふ", "へ", "ほ"],
    ["ま", "み", "む", "め", "も"],
    ["や", "ゆ", "よ"],
    ["ら", "り", "る", "れ", "ろ"],
    ["わ", "を"],
    ["ん"],
    ["が", "ぎ", "ぐ", "げ", "ご"],
    ["ざ", "じ", "ず", "ぜ", "ぞ"],
    ["だ", "ぢ", "づ", "で", "ど"],
    ["ば", "び", "ぶ", "べ", "ぼ"],
    ["ぱ", "ぴ", "ぷ", "ぺ", "ぽ"],
    ["ア", "イ", "ウ", "エ", "オ"],
    ["カ", "キ", "ク", "ケ", "コ"],
    ["サ", "シ", "ス", "セ", "ソ"],
    ["タ", "チ", "ツ", "テ", "ト"],
    ["ナ", "ニ", "ヌ", "ネ", "ノ"],
    ["ハ", "ヒ", "フ", "ヘ", "ホ"],
    ["マ", "ミ", "ム", "メ", "モ"],
    ["ヤ", "ユ", "ヨ"],
    ["ラ", "リ", "ル", "レ", "ロ"],
    ["ワ", "ヲ"],
    ["ン"],
    ["ガ", "ギ", "グ", "ゲ", "ゴ"],
    ["ザ", "ジ", "ズ", "ゼ", "ゾ"],
    ["ダ", "ヂ", "ヅ", "デ", "ド"],
    ["バ", "ビ", "ブ", "ベ", "ボ"],
    ["パ", "ピ", "プ", "ペ", "ポ"]
]

def replace_words(txt: str) -> str:
    word2replaces = [
        ("【" , "["),
        ("】" , "]"),
        ("❶" , "1."),
        ("❷" , "2."),
        ("❸" , "3."),
        ("❹" , "4."),
        ("❺" , "5."),
        ("❻" , "6."),
        ("❼" , "7."),
        ("❽" , "8."),
        ("❾" , "9."),
        ("（1）", "1."),
        ("（2）", "2."),
        ("（3）", "3."),
        ("（4）", "4."),
        ("（5）", "5."),
        ("（6）", "6."),
        ("（7）", "7."),
        ("（8）", "8."),
        ("（9）", "9."),
        ("（１）", "1."),
        ("（２）", "2."),
        ("（３）", "3."),
        ("（４）", "4."),
        ("（５）", "5."),
        ("（６）", "6."),
        ("（７）", "7."),
        ("（８）", "8."),
        ("（９）", "9."),
    ]

    for word2Replace in word2replaces:
        txt = txt.replace(word2Replace[0], word2Replace[1])

    return txt

def get_dictionary_result(word2search: str) -> DictResult:
    if word2search.strip() == "":
        return DictResult()

    if not word2search:
        return DictResult()

    sub_url_1 = "dict"
    sub_url_2 = "asia"
    url = f"https://www.{sub_url_1}.{sub_url_2}/jc/{word2search}"

    response = requests.get(url=url, verify=False)
    response.encoding = "utf-8"
    htmltext = response.text

    doc = BeautifulSoup(htmltext, 'html.parser')

    tabs = doc.select("#jp_comment")        

    results = []
    results_raw = []

    if tabs:
        for tab in tabs[:1]:
            tmp_txt = replace_words(tab.select_one(".jpword").text)
            results.append(tmp_txt)
            results_raw.append(tmp_txt)

            tmp_txt = replace_words(tab.select_one(".mt10").text.replace("\n", "")).replace("]", "] ")
            results.append(tmp_txt)
            results_raw.append(tmp_txt)

            eles_comment_item = tab.select(".jp_explain > .commentItem")

            for ele in eles_comment_item:
                for e in ele.select(".liju"):
                    e.decompose()
                
            for ele in eles_comment_item:
                ele_text = ele.get_text(separator = '\n', strip = True) #<br> is converted to \n
                ele_text = replace_words(ele_text)
                
                for txt in ele_text.split("\n"):
                    results_raw.append(txt)

                    if txt.startswith("["):
                        #Example text: [名]
                        #Example text: [惯用语]
                        results.append(to_traditional(txt))
                        continue

                    # Example text: 1.jp_text_here。／sc_text_here。
                    sep_idx = txt.find("。／")
                    if sep_idx >= 0:
                        found_invalid = False # True when Text looks like example, but jp text at later part
                        for c in txt[sep_idx:]:
                            if c in hiragana_katakana:
                                found_invalid = True
                                break

                        if not found_invalid:
                            results.append(txt[:sep_idx] + to_traditional(txt[sep_idx:]))
                            continue

                    is_processed = False
                    for i in range(len(txt)):
                        c = txt[i]
                        if c in "「（〔":
                            if "1" <= txt[0] <= "9" and txt[1] in "." and i == 2:
                                # Example text: 1.〔SC TXT〕xxxxxxxxxxxxxxxx（xxxxxxxxxxxxxxxx）
                                continue

                            # Example text: 1. xx；xx；xx。「(xxx)xxxxxxxxxxxxxxxxxxx｡」
                            # Example text: 2 xxxxx，xxxx（xxxxxxxx）
                            txt_split = txt.split(c)  # Pass tense of split is split?!?
                            for j in range(len(txt_split) - 1):
                                txt_split[j] = to_traditional(txt_split[j])
                            recombined_txt = c.join(txt_split)
                            results.append(recombined_txt)
                            is_processed = True
                            break

                    if not is_processed:
                        results.append(txt)

        result_str = "\n".join(results)
        result_str_raw = "\n".join(results_raw)

        return DictResult(suggestion="", is_success=True, definition=result_str, definition_raw=result_str_raw, word=word2search)
    else:
        return DictResult()

def to_traditional(txt: str) -> str:
    seps = "〉〈()。・（）［］、,./\\〔〕·,.|-+!~\n\t《》[]:：\"'；"

    tr_buffer = ""
    buffer = ""
    is_jp = False
    for c in txt:
        if c in hiragana_katakana:
            is_jp = True

        buffer = buffer + c
        if c in seps:
            tr_buffer = tr_buffer + (buffer if is_jp else to_traditional_cond(buffer))
            buffer = ""
            is_jp = False

    rtv = tr_buffer + (buffer if is_jp else to_traditional_cond(buffer))
    return rtv

