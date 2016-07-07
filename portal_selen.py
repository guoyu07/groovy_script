#!/usr/bin/env python

import time
from selenium import webdriver

class WebdriverTest:

    def loadWebPage(self):
    #driver=webdriver.Chrome("/Users/kgao000/Downloads/chromedriver")  # Optional argument, if not specified will search path.
        self.driver=webdriver.Firefox()
        self.driver.get('https://internal-ksportalgwyelb-kone-common-259960184.us-west-2.elb.amazonaws.com/signin')
        time.sleep(1)# Let the user actually see something!
        return

    def loginPage(self):
        signIn=self.driver.find_element_by_id('session_uid')
        signIn.send_keys('kone_admin')
        time.sleep(1)
        user=self.driver.find_element_by_id('session_password')
        user.send_keys('BHN3twork')
        time.sleep(2)
        next=self.driver.find_element_by_id('submitBtn')
        next.click()
        time.sleep(15)

    def searchCard(self):
        proxy=self.driver.find_element_by_id('cps_proxyCardNumber_field-inputEl')
        proxy.send_keys('6039535012000010570')
        time.sleep(1)
        search=self.driver.find_element_by_id('ext-gen1635')
        search.click()
        time.sleep(2)
        out=self.driver.find_element_by_xpath("//div[@id='boundlist-1739-listEl']/ul/li[3]")
        out.click()
        time.sleep(4)
        searchBtn=self.driver.find_element_by_id('extensible-search-button-btnIconEl')
        searchBtn.click()
        time.sleep(15)
    #search_box = driver.find_element_by_name('q')
    #search_box.send_keys('ChromeDriver')
    #search_box.submit()
    #time.sleep(5) # Let the user actually see something!
    def closePage(self):
        self.driver.quit()

if __name__ == "__main__":
    instantiatedObject =WebdriverTest()
    instantiatedObject.loadWebPage()
    instantiatedObject.loginPage()
    instantiatedObject.searchCard()
    instantiatedObject.closePage()
