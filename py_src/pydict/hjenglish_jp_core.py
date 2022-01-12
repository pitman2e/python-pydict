from selenium import webdriver
from hanziconv import HanziConv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from typing import Tuple

class HJEnglishWebDriverCore:
    def __init__(self) -> None:
        options = Options()
        options.headless = True
        caps = DesiredCapabilities().CHROME
        # caps["pageLoadStrategy"] = "normal"  #  Waits for full page load
        caps["pageLoadStrategy"] = "none"   # Do not wait for full page load
        self.driver = webdriver.Chrome(options=options, desired_capabilities=caps)
        self.driver.get("https://dict.hjenglish.com/jp/")
        self.prevUrl = ""
        self.prevWord2Search = ""
    
    def GetDictionaryResult(self, word2Search: str) -> Tuple[str, bool, str]:
        if (word2Search.strip() == ""):
            return ""

        prevUrl = self.driver.current_url
        
        if (not word2Search):
            return ""

        if (self.prevWord2Search != word2Search):
            WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".search-input")))

            searchInputEle = self.driver.find_element(By.CSS_SELECTOR, ".search-input")
            searchInputEle.click()
            searchInputEle.clear()
            searchInputEle.send_keys(word2Search)
            searchInputEle.send_keys(u'\ue007')

            if prevUrl:
                try:
                    WebDriverWait(self.driver, 10).until(lambda d: prevUrl != d.current_url)
                except:
                    return "Failed to load !", False, ""

        self.prevWord2Search = word2Search

        WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, ".word-details-pane-header,.word-suggestions,.word-details-tab,.word-notfound")))

        if (self.driver.find_elements_by_css_selector(".word-suggestions")):
            return "Word not found !", True, ""

        if (self.driver.find_elements_by_css_selector(".word-notfound")):
            return "Word not found !", True, ""

        tabs = self.driver.find_elements_by_css_selector(".word-details-tab")

        resultStr = ""
        if tabs:
            i = 0
            for tab in tabs:
                tab.click()
                WebDriverWait(self.driver, 10).until(lambda d: len(d.find_elements_by_css_selector(".word-details-pane-header")) > i)
                result = self.driver.find_elements_by_css_selector(".word-details-pane-header")[i].text
                resultSplit = result.splitlines()
                #1st/2nd lines are Japanese words, should not convert to TC
                for j in range(2, len(resultSplit)): 
                    resultSplit[j] = HanziConv.toTraditional(resultSplit[j])
                resultTC = "\n".join(resultSplit[(1 if i > 0 else 0):]) + "\n\n" #First line is the same thro-out all tabs, no need except 1st tab
                resultStr += resultTC
                i += 1
            return resultStr.strip("\n"), True, ""
        else:
            result = self.driver.find_element(By.CSS_SELECTOR, ".word-details-pane-header").text
            resultSplit = result.splitlines()
            for i in range(2, len(resultSplit)):
                resultSplit[i] = HanziConv.toTraditional(resultSplit[i])
            resultTC = "\n".join(resultSplit)
            resultStr += resultTC
            return resultStr.strip("\n"), True, ""
        
    def close(self) -> None:
        self.driver.quit()
