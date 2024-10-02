from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyautogui
from PIL import Image
import ddddocr
import uuid
from bs4 import BeautifulSoup
import random
from selenium.webdriver.common.keys import Keys

# 隨機png檔名製造
def generate_random_filename(extension=''):
    random_uuid = uuid.uuid4()
    random_filename = str(random_uuid).replace('-', '')

    if extension:
        random_filename += f'.{extension}'
    return random_filename

def step_4():
    status = False
    while not status:
        try: # 試著分析並點擊隨機票區
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            rows = soup.find_all('tr', class_='status_tr')
            data = []
            for row in rows:
                row_id = row['id']  # 獲取 id 屬性
                ticket_area = row.find_all('td')[1].text.strip()
                ticket_price = row.find_all('td')[2].text.strip()
                available_seats = row.find_all('td')[3].text.strip()
                data.append({'ID': row_id, '票區': ticket_area, '票價': ticket_price,'空位': available_seats})
            filtered_data = [item for item in data if item['空位'] != '已售完']
            # filtered_data = [item for item in data if item['空位'] == '已售完']
            # 計算起始和結束索引
            start_index = int(len(filtered_data) * START_PERCENTAGE)
            end_index = int(len(filtered_data) * END_PERCENTAGE)
            # 選取指定範圍的資料
            selected_items = filtered_data[start_index:end_index]
            # 指定範圍中隨機選一區來買
            random_row = random.choice(selected_items)
            # 點擊隨機票區
            login_button = WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.element_to_be_clickable((By.XPATH, f"//*[@id='{random_row['ID']}']")))
            login_button.click()
        except: # 如果畫面重新整理超過REFRESH_THRESHOLD秒沒東西跑出來 
            status = False
            driver.get(mystery_page_2)
            current_url = driver.current_url
            continue
        try:
            # 成功點擊立即訂購後 只等待1秒看網址是否跳轉到下個頁面 如果沒有就重新整理再來一次 電腦太爛這邊可能會重複一直刷 那就必須調高閥值 
            WebDriverWait(driver, LAG_THRESHOLD).until(EC.url_changes(current_url))
            current_url = driver.current_url
            status = True
        except:
            status = False
            driver.get(mystery_page_2)
            current_url = driver.current_url







# 設定 Chrome 的選項
chrome_options = Options()
# 設定視窗大小和位置
chrome_options.add_argument("window-size=1500,1000")  # 設定視窗大小 (寬 x 高)
chrome_options.add_argument("window-position=0,0")  # 設定視窗位置 (x, y)

# 使用正確的參數名稱指定版本
service = Service(ChromeDriverManager(driver_version="129.0.6668.90").install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# 第一關 預設先登入 
##################################################################################################
# 初始登入頁面
target_page = "https://kham.com.tw/application/utk13/utk1306_.aspx"
login_status = False
while not login_status:
    driver.get(target_page)
    current_url = driver.current_url
    # 自動輸入帳號
    account_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "ACCOUNT")))
    account_input.send_keys("A123456789") ####
    # 自動輸入密碼
    password_input = driver.find_element(By.ID, "PASSWORD")
    password_input.send_keys("keyyourpassword") ####
    # 找到驗證碼圖片
    img_element = driver.find_element("id", "chk_pic")
    # 獲取驗證碼圖片在網頁中位置
    left = int(img_element.location['x'])
    top = int(img_element.location['y'])
    right = int(img_element.location['x'] + img_element.size['width'])
    bottom = int(img_element.location['y'] + img_element.size['height'])
    # 儲存頁面截圖
    path = generate_random_filename('png')
    driver.save_screenshot(path)
    driver.save_screenshot(path+'.png')
    im = Image.open(path)
    im = im.crop((left, top, right, bottom))
    im.save(path)
    # 辨別驗證碼
    ocr = ddddocr.DdddOcr()
    with open(path, 'rb') as f:
        image = f.read()
    VerifyCode = ocr.classification(image)
    conversion_rules = {'U':'0','g':'9','Z':'7','z':'7','s':'5','S':'5','l':'1','L':'1','I':'1','i':'1'}
    conversion_rules = {}
    # 使用迴圈進行替換
    modified_VerifyCode = ''.join(conversion_rules.get(char, char) for char in VerifyCode)
    # 找到驗證碼欄位並輸入
    password_input = driver.find_element(By.ID, "CHK")
    password_input.clear()
    password_input.send_keys(modified_VerifyCode)
    # 點擊登入
    login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='UpdatePanel1']/div[2]/p[2]/a/button")))
    login_button.click()
    try:
        # 點擊登入後 3秒內要跳轉下個頁面 不然就重頭再登一次
        WebDriverWait(driver, 3).until(EC.url_changes(current_url))
        login_status = True
    except Exception as e:
        login_status = False

# 第二關 設定目標歌手 我要購票的頁面 大部分人會在這關一直刷直到可以進到下一關選日期
##################################################################################################
target_page = 'https://kham.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P0NGKVY1' # 10/7 測試網址 ####
target_page = 'https://kham.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P0KYQBSU' # 羅志祥
# target_page = 'https://kham.com.tw/application/UTK02/UTK0201_.aspx?PRODUCT_ID=P0LGVGM0' # 已售完

LAG_THRESHOLD  = 1  #### 電腦太爛這邊可能會重複一直刷 那就必須調高閥值
REFRESH_THRESHOLD = 5 #### 這有可能要等60秒才有東西跑出來 一直重新整理反而都等不到 也有可能一重新整理就跑出來 目前寫法是先一直重新整理
start_selling_status = False
while not start_selling_status:
    driver.get(target_page)
    current_url = driver.current_url
    try: # 試著點擊我要購票
        button = WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='content']/p[2]/a/button")))
        button.click()
    except: # 如果畫面重新整理超過REFRESH_THRESHOLD秒沒東西跑出來 
        start_selling_status = False
        continue
    try:
        # 成功點擊我要購票後 只等待1秒看網址是否跳轉到下個頁面 如果沒有就重新整理再來一次 電腦太爛這邊可能會重複一直刷 那就必須調高閥值 
        WebDriverWait(driver, LAG_THRESHOLD).until(EC.url_changes(current_url))
        current_url = driver.current_url
        start_selling_status = True
    except:
        start_selling_status = False

# 第三關 成功刷入選日期頁面 這邊要選定日期 mystery_page_1
##################################################################################################
# 第一格 立即訂購 2 4 6 8  第一個出現的日期為2  3為第一個日期的殘障票 所以如果演唱會有3天 要挑第一天買就選2 第二天買就選4 第三天買就選6
# 周杰倫演出時間｜2024年12/5 (四) 7:30PM、12/6 (五) 7:30PM、12/7 (六)6:00 PM、12/8 (日) 6:00PM  共四天 所以2468可以選
WHAT_DATE = 2 ####
LAG_THRESHOLD  = 1  #### 電腦太爛這邊可能會重複一直刷 那就必須調高閥值
REFRESH_THRESHOLD = 5 #### 這有可能要等60秒才有東西跑出來 一直重新整理反而都等不到 也有可能一重新整理就跑出來 目前寫法是先一直重新整理
mystery_page_1 = current_url
status = False
while not status:
    try: # 試著點擊立即訂購
        button = WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.element_to_be_clickable((By.XPATH, f"//*[@id='content']/table/tbody/tr[{WHAT_DATE}]/td[4]/a/button")))
        button.click()
    except: # 如果畫面重新整理超過REFRESH_THRESHOLD秒沒東西跑出來 
        status = False
        driver.get(mystery_page_1)
        current_url = driver.current_url
        continue
    try:
        # 成功點擊立即訂購後 只等待1秒看網址是否跳轉到下個頁面 如果沒有就重新整理再來一次 電腦太爛這邊可能會重複一直刷 那就必須調高閥值 
        WebDriverWait(driver, LAG_THRESHOLD).until(EC.url_changes(current_url))
        current_url = driver.current_url
        status = True
    except:
        status = False
        driver.get(mystery_page_1)
        current_url = driver.current_url

# 第四關 開始選區 有很多區 目前是以上下限範圍來決定票區 mystery_page_2
##################################################################################################
# 輸入百分比
START_PERCENTAGE = float(0) / 100
END_PERCENTAGE = float(20) / 100
LAG_THRESHOLD  = 1  #### 電腦太爛這邊可能會重複一直刷 那就必須調高閥值
REFRESH_THRESHOLD = 5 #### 這有可能要等60秒才有東西跑出來 一直重新整理反而都等不到 也有可能一重新整理就跑出來 目前寫法是先一直重新整理
mystery_page_2 = current_url

status = False
while not status:
    try: # 試著分析並點擊隨機票區
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        rows = soup.find_all('tr', class_='status_tr')
        data = []
        for row in rows:
            row_id = row['id']  # 獲取 id 屬性
            ticket_area = row.find_all('td')[1].text.strip()
            ticket_price = row.find_all('td')[2].text.strip()
            available_seats = row.find_all('td')[3].text.strip()
            data.append({'ID': row_id, '票區': ticket_area, '票價': ticket_price,'空位': available_seats})
        filtered_data = [item for item in data if item['空位'] != '已售完']
        # filtered_data = [item for item in data if item['空位'] == '已售完']
        # 計算起始和結束索引
        start_index = int(len(filtered_data) * START_PERCENTAGE)
        end_index = int(len(filtered_data) * END_PERCENTAGE)
        # 選取指定範圍的資料
        selected_items = filtered_data[start_index:end_index]
        # 指定範圍中隨機選一區來買
        random_row = random.choice(selected_items)
        # 點擊隨機票區
        login_button = WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.element_to_be_clickable((By.XPATH, f"//*[@id='{random_row['ID']}']")))
        login_button.click()
    except: # 如果畫面重新整理超過REFRESH_THRESHOLD秒沒東西跑出來 
        status = False
        driver.get(mystery_page_2)
        current_url = driver.current_url
        continue
    try:
        # 成功點擊立即訂購後 只等待1秒看網址是否跳轉到下個頁面 如果沒有就重新整理再來一次 電腦太爛這邊可能會重複一直刷 那就必須調高閥值 
        WebDriverWait(driver, LAG_THRESHOLD).until(EC.url_changes(current_url))
        current_url = driver.current_url
        status = True
    except:
        status = False
        driver.get(mystery_page_2)
        current_url = driver.current_url

# 第五關 開始選位置 有很多位置 mystery_page_3
##################################################################################################
# '//*[@id="content"]/div[3]/div[1]/div[1]/div[2]/button[1]' 原價
# '//*[@id="content"]/div[3]/div[1]/div[1]/div[2]/button[2]' 身心障礙
# '//*[@id="content"]/div[3]/div[1]/div[1]/div[2]/button[1]' 身障陪同
        

LAG_THRESHOLD  = 1  #### 電腦太爛這邊可能會重複一直刷 那就必須調高閥值
REFRESH_THRESHOLD = 5 #### 這有可能要等60秒才有東西跑出來 一直重新整理反而都等不到 也有可能一重新整理就跑出來 目前寫法是先一直重新整理
BUY_TICKET_HOLDTIME = 180 #### 成功輸入驗證碼後的等待時間 如果中斷可能導致訂單取消 但等太久不知道會不會成功
VERIFY_DELAY_TIME = 1.5 #### 輸入驗證碼的間隔時間  爛電腦調高一點
mystery_page_3 = current_url
status = False
while not status:
    try:
        # 點擊原價
        button = WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div[3]/div[1]/div[1]/div[2]/button[1]')))
        button.click()
        # 點擊座位
        click_flag = False
        target_tds = driver.find_elements(By.CLASS_NAME, 'empty.up')
        if target_tds:
            random_td = random.choice(target_tds)  # 隨機選擇一個元素
            random_td.click()  # 點擊隨機選擇的元素
            click_flag = True
        target_tds = driver.find_elements(By.CLASS_NAME, 'empty.right')
        if target_tds:
            random_td = random.choice(target_tds)  # 隨機選擇一個元素
            random_td.click()  # 點擊隨機選擇的元素
            click_flag = True
        target_tds = driver.find_elements(By.CLASS_NAME, 'empty.left')
        if target_tds:
            random_td = random.choice(target_tds)  # 隨機選擇一個元素
            random_td.click()  # 點擊隨機選擇的元素
            click_flag = True
        if click_flag == False:
            raise ValueError("no empty can click")
    except:
        step_4()
    if click_flag == True:
        try:
            # 找到驗證碼圖片
            img_element = driver.find_element("id", "chk_pic")
            # 獲取驗證碼圖片在網頁中位置
            left = int(img_element.location['x'])
            top = int(img_element.location['y'])
            right = int(img_element.location['x'] + img_element.size['width'])
            bottom = int(img_element.location['y'] + img_element.size['height'])
            # 儲存頁面截圖
            path = generate_random_filename('png')
            driver.save_screenshot(path)
            driver.save_screenshot(path+'.png')
            im = Image.open(path)
            im = im.crop((left, top, right, bottom))
            im.save(path)
            #辨別驗證碼
            ocr = ddddocr.DdddOcr()
            with open(path, 'rb') as f:
                image = f.read()
            VerifyCode = ocr.classification(image)
            conversion_rules = {'U':'0','g':'9','Z':'7','z':'7','s':'5','S':'5','l':'1','L':'1','I':'1','i':'1'}
            conversion_rules = {}
            # 使用迴圈進行替換
            modified_VerifyCode = ''.join(conversion_rules.get(char, char) for char in VerifyCode)
            # 找到驗證碼欄位並輸入驗證碼
            password_input = driver.find_element(By.ID, "CHK")
            password_input.clear()
            password_input.send_keys(modified_VerifyCode)
            # password_input.send_keys('qq9w')
            # 點選 加入購物車
            button = WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='addcart']/button")))
            button.click()
            # 等待彈窗出現
            WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-dialog")))
            button = driver.find_element(By.CLASS_NAME, "ui-dialog-titlebar-close")
            button.click()
            time.sleep(VERIFY_DELAY_TIME)
            # 找第二次驗證碼圖片
            img_element = driver.find_element("id", "chk_pic")
            # 獲取驗證碼圖片在網頁中位置
            left = int(img_element.location['x'])
            top = int(img_element.location['y'])
            right = int(img_element.location['x'] + img_element.size['width'])
            bottom = int(img_element.location['y'] + img_element.size['height'])
            # 儲存頁面截圖
            path = generate_random_filename('png')
            driver.save_screenshot(path)
            driver.save_screenshot(path+'.png')
            im = Image.open(path)
            im = im.crop((left, top, right, bottom))
            im.save(path)
            #辨別驗證碼
            ocr = ddddocr.DdddOcr()
            with open(path, 'rb') as f:
                image = f.read()
            VerifyCode = ocr.classification(image)
            conversion_rules = {'U':'0','g':'9','Z':'7','z':'7','s':'5','S':'5','l':'1','L':'1','I':'1','i':'1'}
            conversion_rules = {}
            # 使用迴圈進行替換
            modified_VerifyCode_2 = ''.join(conversion_rules.get(char, char) for char in VerifyCode)

            if modified_VerifyCode == modified_VerifyCode_2: # 如果驗證碼輸入正確
                try:
                    # 等待180秒直到進入結帳10分鐘頁面 ####
                    WebDriverWait(driver, BUY_TICKET_HOLDTIME).until(EC.url_changes(current_url))
                    status = True
                    break
                except:
                    pass
            else:
                # 找到驗證碼欄位並輸入驗證碼
                password_input = driver.find_element(By.ID, "CHK")
                password_input.clear()
                password_input.send_keys(modified_VerifyCode)
                # password_input.send_keys('qq9ws')
                # 點選 加入購物車
                login_button = WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='addcart']/button")))
                login_button.click()
                # 等待彈窗出現
                WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-dialog")))
                close_button = driver.find_element(By.CLASS_NAME, "ui-dialog-titlebar-close")
                close_button.click()
                time.sleep(VERIFY_DELAY_TIME)
                # 找第三次驗證碼圖片
                img_element = driver.find_element("id", "chk_pic")
                # 獲取驗證碼圖片在網頁中位置
                left = int(img_element.location['x'])
                top = int(img_element.location['y'])
                right = int(img_element.location['x'] + img_element.size['width'])
                bottom = int(img_element.location['y'] + img_element.size['height'])
                # 儲存頁面截圖
                path = generate_random_filename('png')
                driver.save_screenshot(path)
                driver.save_screenshot(path+'.png')
                im = Image.open(path)
                im = im.crop((left, top, right, bottom))
                im.save(path)
                #辨別驗證碼
                ocr = ddddocr.DdddOcr()
                with open(path, 'rb') as f:
                    image = f.read()
                VerifyCode = ocr.classification(image)
                conversion_rules = {'U':'0','g':'9','Z':'7','z':'7','s':'5','S':'5','l':'1','L':'1','I':'1','i':'1'}
                conversion_rules = {}
                # 使用迴圈進行替換
                modified_VerifyCode_3 = ''.join(conversion_rules.get(char, char) for char in VerifyCode)

                if modified_VerifyCode_2 == modified_VerifyCode_3: # 如果驗證碼輸入正確
                    try:
                        # 等待180秒直到進入結帳10分鐘頁面 ####
                        WebDriverWait(driver, BUY_TICKET_HOLDTIME).until(EC.url_changes(current_url))
                        status = True
                        break
                    except:
                        pass
                else:
                    # 找到驗證碼欄位並輸入驗證碼
                    password_input = driver.find_element(By.ID, "CHK")
                    password_input.clear()
                    password_input.send_keys(modified_VerifyCode_3)
                    # password_input.send_keys('qq9w')
                    # 點選 加入購物車
                    login_button = WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='addcart']/button")))
                    login_button.click()
                    # 等待彈窗出現
                    WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-dialog")))
                    close_button = driver.find_element(By.CLASS_NAME, "ui-dialog-titlebar-close")
                    close_button.click()
                    try:
                        # 第三次輸入驗證碼 只 等待 REFRESH_THRESHOLD 秒 ####
                        WebDriverWait(driver, REFRESH_THRESHOLD).until(EC.url_changes(current_url))
                        status = True
                        break
                    except:
                        pass
        except:
            pass
    step_4()



print('購票成功')
time.sleep(60000)

'''
<input name="ctl00$ContentPlaceHolder1$ACCOUNT" type="text" maxlength="20" id="ACCOUNT" autocomplete="Off" placeholder="身分證字號、護照或台灣通行證號碼" style="max-width: 280px;" data-gtm-form-interact-field-id="0">


'''