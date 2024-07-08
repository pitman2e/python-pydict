from hanziconv import HanziConv
from .dict_result import DictResult
from bs4 import BeautifulSoup
import requests

def replace_words(txt: str) -> str:
    word2Replaces = [
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

    for word2Replace in word2Replaces:
        txt = txt.replace(word2Replace[0], word2Replace[1])

    return txt

def GetDictionaryResult(word2Search: str) -> DictResult:
    if (word2Search.strip() == ""):
        return DictResult()

    if (not word2Search):
        return DictResult()

    suburl1 = "dict"
    suburl2 = "asia"
    url = f"https://www.{suburl1}.{suburl2}/jc/{word2Search}"

    response = requests.get(url)
    response.encoding = "utf-8"
    htmltext = response.text

    doc = BeautifulSoup(htmltext, 'html.parser')

    tabs = doc.select("#jp_comment")        

    results = []

    resultStr = ""
    if tabs:
        for tab in tabs[:1]:
            results.append(replace_words(tab.select_one(".jpword").text))
            results.append(replace_words(tab.select_one(".mt10").text.replace("\n", "")).replace("]", "] "))

            eles_commentItem = tab.select(".jp_explain > .commentItem")

            for ele in eles_commentItem:
                for e in ele.select(".liju"):
                    e.decompose()
                
            for ele in eles_commentItem:
                ele_text = ele.get_text(separator = '\n', strip = True) #<br> is converted to \n
                ele_text = replace_words(ele_text)
                
                for txt in ele_text.split("\n"):
                    if "「" in txt:
                        #Example text: 1. xx；xx；xx。「(xxx)xxxxxxxxxxxxxxxxxxx｡」
                        txt_splited = txt.split("「")
                        txt_splited[0] = HanziConv.toTraditional(txt_splited[0])
                        recombined_txt = "".join(txt_splited)
                        results.append(recombined_txt)
                    elif txt.startswith("["):
                        #Example text: [名]
                        #Example text: [惯用语]
                        results.append(HanziConv.toTraditional(txt))
                    elif "。" in txt:
                        #Example text: 1.x，x。（xxxxxxxxxxxx。）
                        txt_splited = txt.split("。")
                        txt_splited[0] = HanziConv.toTraditional(txt_splited[0])
                        recombined_txt = "".join(txt_splited)
                        results.append(recombined_txt)
                    else:
                        results.append(txt)

        resultStr = "\n".join(results)

        return DictResult(suggestion="", is_success=True, definition=resultStr, word=word2Search)
    else:
        return DictResult()
    
