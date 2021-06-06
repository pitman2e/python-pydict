import requests
from bs4 import BeautifulSoup

def Check_EN_ZH(word, recursiveDepth=0):
    url = "https://hk.dictionary.search.yahoo.com/search?p={}".format(word)

    response = requests.get(url)
    response.encoding = "utf-8"
    htmltext = response.text

    doc = BeautifulSoup(htmltext, 'html.parser')
    elements = doc.select(".sys_dict_word_card")

    result = {}

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
    else:
        result["isSuccess"] = False
        result["definition"] = ""

    return result