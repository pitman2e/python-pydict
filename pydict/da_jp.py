from hanziconv import HanziConv
from pydict.dict_result import DictResult
from bs4 import BeautifulSoup
import requests

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
    ]

    for word2Replace in word2replaces:
        txt = txt.replace(word2Replace[0], word2Replace[1])

    return txt

def get_dictionary_result(word2search: str) -> DictResult:
    if word2search.strip() == "":
        return DictResult()

    if not word2search:
        return DictResult()

    suburl1 = "dict"
    suburl2 = "asia"
    url = f"https://www.{suburl1}.{suburl2}/jc/{word2search}"

    response = requests.get(url=url, verify=False)
    response.encoding = "utf-8"
    htmltext = response.text

    doc = BeautifulSoup(htmltext, 'html.parser')

    tabs = doc.select("#jp_comment")        

    results = []

    if tabs:
        for tab in tabs[:1]:
            results.append(replace_words(tab.select_one(".jpword").text))
            results.append(replace_words(tab.select_one(".mt10").text.replace("\n", "")).replace("]", "] "))

            eles_comment_item = tab.select(".jp_explain > .commentItem")

            for ele in eles_comment_item:
                for e in ele.select(".liju"):
                    e.decompose()
                
            for ele in eles_comment_item:
                ele_text = ele.get_text(separator = '\n', strip = True) #<br> is converted to \n
                ele_text = replace_words(ele_text)
                
                for txt in ele_text.split("\n"):
                    if "「" in txt:
                        #Example text: 1. xx；xx；xx。「(xxx)xxxxxxxxxxxxxxxxxxx｡」
                        txt_splited = txt.split("「")
                        txt_splited[0] = HanziConv.toTraditional(txt_splited[0])
                        recombined_txt = "「".join(txt_splited)
                        results.append(recombined_txt)
                    elif txt.startswith("["):
                        #Example text: [名]
                        #Example text: [惯用语]
                        results.append(HanziConv.toTraditional(txt))
                    elif "（" in txt: 
                        #Example text: xxxxx，xxxx（xxxxxxxx）
                        txt_splited = txt.split("（")
                        txt_splited[0] = HanziConv.toTraditional(txt_splited[0])
                        recombined_txt = "（".join(txt_splited)
                        results.append(recombined_txt)
                    else:
                        results.append(txt)

        resultStr = "\n".join(results)

        return DictResult(suggestion="", is_success=True, definition=resultStr, word=word2search)
    else:
        return DictResult()
    
