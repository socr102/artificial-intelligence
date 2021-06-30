from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException 
from selenium.common.exceptions import TimeoutException
import pickle,time
import pandas as pd
import re
import sys,os

def striplist(l):
    return([x.strip() for x in l])
def strip_quote_list(l):
    return([x.strip().replace('"','') for x in l])
keyword_list = {}
with open("keywords.txt", 'r', encoding = 'UTF-8') as f:
    temp_list = f.read().splitlines()
    # print(temp_list)
    for item in temp_list:
        # print(item)
        arr = item.split(':')
        keyword_list[arr[0].strip()] = strip_quote_list(arr[1].split(','))

# print(keyword_list)
def keyword_contain(txt):
    global keyword_list
    ret_str = ""
    for keyword in [*keyword_list]:
        flag = False
        for item in keyword_list[keyword]:
            if item in txt:
                flag = True
                break
        if flag:
            ret_str+=keyword + " "
    return ret_str



def save_text(df,filename):

    with open(filename, 'w', encoding = 'UTF-8') as f:
        index = df.index
        number_of_rows = len(index)
        relation_str = ""
        for row in range(0,number_of_rows):
            relation_tmp = df.iat[row,2]
            if relation_str != relation_tmp:
                if relation_str == "":
                    f.write(relation_tmp+"\n")
                else:
                    f.write("\n"+relation_tmp+"\n")
                relation_str = relation_tmp
            f.write(df.iat[row,0]+"\n")
            # print(df.iat[row,0])




# url = "https://www.linkedin.com/in/arun-d-kumar-325aa415b/"
def main(url):


    # with open(filename, 'w', encoding = 'UTF-8') as f:
    #     f.close()
    cnt = 0
    friend_list = []
    friend_link_list = []
    try:
        with open(f'My LinkedIn Friends.txt', 'r', encoding = 'UTF-8') as f:
            temp_list = f.read().splitlines()
    except:
        with open(f'My LinkedIn Friends.txt', 'r') as f:
            temp_list = f.read().splitlines()

    # print(temp_list)
    for item in temp_list:
        # print(item)
        # print(re.split(r'\t+', item))
        friend_list.append(striplist(re.split(r'\t+', item)))
        # print(friend_list)
        # friend_list.append(item.split(r'\t'))
        link = friend_list[-1][1]
        friend_link_list.append(".com"+link[link.find('/in/'):])
        # print(friend_link_list)
    # friend_list = striplist(friend_list)
    # friend_link_list = striplist(friend_link_list)
    # print(friend_link_list)
    df = pd.DataFrame(columns = ['Person','Link','Relation'])
    options = webdriver.ChromeOptions()
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # options.add_experimental_option("prefs", prefs)
    options.add_argument('--ignore-certificate-errors') #removes SSL errors from terminal
    options.add_experimental_option("excludeSwitches", ["enable-logging"]) #removes device adapter errors from terminal
    options.add_argument('--disable-web-security') #removes SSL errors from terminal
    options.add_argument("--log-level=3")
    options.add_argument("--user-data-dir=chrome-data")
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
    driver.maximize_window()
    driver.get(url)
    try:
        # driver.maximize_window()
        SCROLL_PAUSE_TIME = 3
        while True:
            try:
                WebDriverWait(driver, 60).until( \
                        EC.presence_of_element_located((By.XPATH, '//*[@id="ember21"]')) \
                        )
                break
            except:
                pass
        # eleclick=WebDriverWait(driver, 60).until( \
        #         EC.presence_of_element_located((By.XPATH, '//a[contains(string(), " connections")]')) \
        #         )
        # driver.execute_script("arguments[0].click()",eleclick)
        # WebDriverWait(driver, 60).until( \
        #         EC.invisibility_of_element_located((By.XPATH, '//a[contains(string(), " connections")]')) \
        #         )

        eleclick=WebDriverWait(driver, 60).until( \
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a.app-aware-link.pv-highlight-entity__card-action-link')) \
                )
        count=""
        try:
            count = driver.find_elements(By.CSS_SELECTOR, "a.app-aware-link.pv-highlight-entity__card-action-link")[1].find_element(By.TAG_NAME,"h3").text.replace(" mutual connections","")
            print("Shared connections:"+count)
        # print(driver.find_elements(By.CSS_SELECTOR, "a.app-aware-link.pv-highlight-entity__card-action-link")[1].find_element(By.TAG_NAME,"h3").text.replace("mutual connections",""))
        except:
            count="0"

        url = driver.current_url
        filename = url.split('/')[-2]+".txt"
        if url.split('/')[-1]!='':
            filename = url.split('/')[-1]+".txt"

        path=os.path.abspath(os.getcwd())+"\\output"
    
        if os.path.exists(path) == False:
            os.mkdir(path)
        filename = path+"\\"+filename
        # print(filename)





        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        profile=""
        profile_atract=""
        try:
            profile_ele=WebDriverWait(driver, 15).until( \
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pv-profile-section-pager.ember-view')) \
                )
            profile_eles = driver.find_elements(By.TAG_NAME, "section")
            for ele in profile_eles:
                attr = ele.get_attribute("class")
                if "pv-profile-section" in attr:
                    if "pv-interests-section" in attr:
                        continue
                    profile += ele.text

            profile_atract = keyword_contain(profile)


            # if  "Harvard"  in profile:
            #     profile_atract +="Harvard "
            # if  "Stanford"  in profile:
            #     profile_atract +="Stanford "
            # if  "MIT "  in profile:
            #     profile_atract +="MIT "
            # if  "Brown University"  in profile:
            #     profile_atract +="Brown University "
            # if  "MIT Sloan"  in profile:
            #     profile_atract +="MIT Sloan "





        except:
            pass
        print("keywords:"+profile_atract)






        driver.execute_script("arguments[0].click()",eleclick)
        WebDriverWait(driver, 60).until( \
                EC.invisibility_of_element_located((By.CSS_SELECTOR, 'a.app-aware-link.pv-highlight-entity__card-action-link')) \
                )



        while  True:
            
            time.sleep(2)
            # Get scroll height
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            items_div = driver.find_elements_by_class_name("entity-result__item")
            for item in items_div:
                href_str=item.find_element_by_tag_name('a').get_attribute('href')+"/"
                # print(href_str)
                href_str = ".com"+href_str[href_str.find('/in/'):]
                if href_str in friend_link_list:
                    index = friend_link_list.index(href_str)
                    print(index)
                    df.loc[cnt] = friend_list[index]
                    print("matching---")
                    # print(friend_list[index])
                    cnt += 1
                    df=df.sort_values('Relation')
                    # print(df)
                    save_text(df,filename)
                    # df.to_csv(filename, header=None, index=None, sep=' ', mode='w')
                    print(cnt)
                    append_write = ""



            try:
                nextclick = WebDriverWait(driver, 10).until( \
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button.artdeco-pagination__button.artdeco-pagination__button--next.artdeco-button.artdeco-button--muted.artdeco-button--icon-right.artdeco-button--1.artdeco-button--tertiary.ember-view')) \
                        )
            except:
                break
            try:
                if nextclick.get_attribute("disabled") == None:
                    nextclick.click()
                else:
                    break
            except:
                break
        if os.path.exists(filename):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not
        with open(filename, append_write, encoding = 'UTF-8') as f:
            f.write("\nShared connections:"+count)
            f.write("\nKeywords:"+profile_atract)
        with open(filename, 'r', encoding = 'UTF-8') as f:
            print(f.read())
        driver.quit()
    except Exception as e: 
        print(e)
        # print("Error!")
        driver.quit()


    print("Finish!")




args = sys.argv
if len(args) == 2:
    # if "://www.linkedin.com/in/" in args[1]:
    main(args[1])
    # else:
        # print("Please input correct link")
else:
    print("python grab_match.py [link]")
    print("ex; python grab_match.py https://www.linkedin.com/in/arun-d-kumar-325aa415b/")



