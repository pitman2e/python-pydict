import requests
from bs4 import BeautifulSoup

def Check_EN_ZH(word: str, recursiveDepth=0):
    result = {}

    if (word.strip() == ""): 
        result["isSuccess"] = False
        result["suggestion"] = ""
        result["definition"] = ""
        return result

    url = "https://hk.dictionary.search.yahoo.com/search?p={}".format(word)

    response = requests.get(url)
    response.encoding = "utf-8"
    htmltext = response.text

    doc = BeautifulSoup(htmltext, 'html.parser')
    elements = doc.select(".sys_dict_word_card")
    suggestion_ele = doc.select(".sys_dict_sugg")
    

    if (len(elements) > 0):
        hasVA = False
        result["isSuccess"] = True

        definitions = []
        for element in elements:
            definitions.append(element.select(".compTitle")[1].text.strip())
            if len(element.select(".va-top")) > 0:
                hasVA = True
                definitions.append(element.select(".va-top")[0].text.strip())

            lis = element.select(".p-rel li")
            for li in lis: 
                definitionText = li.text.strip()
                definitions.append(definitionText)
                if len(lis) == 1 and "的" in definitionText and hasVA == False and recursiveDepth == 0:
                    return Check_EN_ZH(definitionText[0:definitionText.index("的")], recursiveDepth+1)

        result["definition"] = "\n".join(definitions)
        result["suggestion"] = ""
    else:
        result["isSuccess"] = False
        result["definition"] = ""
        result["suggestion"] = suggestion_ele[0].text.strip().replace("你是不是要查 ", "")

    return result