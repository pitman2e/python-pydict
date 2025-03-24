import requests
from bs4 import BeautifulSoup
from pydict.dict_result import DictResult

def check_en_zh(word: str, recursive_depth=0) -> DictResult:
    result = DictResult(word=word)

    if word.strip() == "":
        return result

    url = "https://hk.dictionary.search.yahoo.com/search?p={}".format(word)

    response = requests.get(url)
    response.encoding = "utf-8"
    htmltext = response.text

    doc = BeautifulSoup(htmltext, 'html.parser')
    elements = doc.select(".sys_dict_word_card")
    suggestion_ele = doc.select(".sys_dict_sugg")

    if len(elements) > 0:
        has_va = False
        result.is_success = True

        definitions = []
        for element in elements:
            definitions.append(element.select(".compTitle")[1].text.strip())
            if len(element.select(".va-top")) > 0:
                has_va = True
                definitions.append(element.select(".va-top")[0].text.strip())

            lis = element.select(".p-rel li")
            for li in lis: 
                definition_text = li.text.strip()
                definitions.append(definition_text)
                if len(lis) == 1 and "的" in definition_text and has_va == False and recursive_depth == 0:
                    return check_en_zh(definition_text[0:definition_text.index("的")], recursive_depth + 1)

        result.definition = "\n".join(definitions)
        result.definition_raw = result.definition
        result.suggestion = ""
    else:
        result.is_success = False
        result.definition = ""
        result.definition_raw = result.definition
        if len(suggestion_ele) > 0:
            result.suggestion = suggestion_ele[0].text.strip().replace("你是不是要查 ", "")
        else:
            result.suggestion = ""

    return result