from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5000", "http://localhost:5173"]}})


def download_pdf(title ,driver):
    title = title[0:3]
    wait = WebDriverWait(driver, 10)
    pdf_links = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "a[aria-label='PDF']")))
    #pdf_links = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "a[aria-label='PDF']")))
    pdf_links = pdf_links[0:3]

    for index, link in enumerate(pdf_links):
        print(f'({index})正在下載: {title[index]}')
        link.click()
        pyautogui.sleep(2)
        # 移動到指定的座標
        #print(f'座標位置: {pyautogui.position()}')
    
        pyautogui.moveTo(x=154, y=377, duration = 1.5)
    
        # 顯示座標位置
        print(f'座標位置: {pyautogui.position()}')
        # 點擊一下，讓後面的ctrl+s可以正常開啟另存新檔的視窗
        pyautogui.click()
        pyautogui.hotkey('ctrl', 's')
        pyautogui.sleep(1)
        # 點擊一下，讓後面的alt+s可以儲存檔案
        pyautogui.click()
        pyautogui.hotkey('alt', 's')
        pyautogui.moveTo(x=19, y=48, duration = 1.5)
        pyautogui.click()
        pyautogui.sleep(3)

@app.route('/crawl', methods=['POST'])
def crawl():
    pyautogui.moveTo(x=512, y=1024, duration = 1.5)
    pyautogui.click()
    keyword = request.json.get('keyword')
    print(keyword)
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get("http://dl.acm.org/")
    pyautogui.sleep(2)
    # 定位搜尋框
    search_input = driver.find_element(By.NAME, "AllField")
    # 輸入想要查詢的關鍵字
    search_input.send_keys(keyword)
    # 定位搜尋按鈕
    search_btn = driver.find_element("css selector", "button.btn.quick-search__button")
    # 點擊搜尋按鈕
    search_btn.click()

    # 等待元素渲染完成
    ul_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "search-result__xsl-body")))
    # 抓取每一篇的標題
    li_elements = ul_element.find_elements(By.TAG_NAME, "li")
    title = []
    for li in li_elements:
        div_element = li.find_elements(By.CLASS_NAME, "issue-item--search")
        for h5 in div_element:
            a_element = h5.find_element(By.TAG_NAME, "a")
            title.append(a_element.text)
            #print(a_element.text)

    # 下載PDF 檔案
    download_pdf(title ,driver)
    # 關閉瀏覽器
    driver.quit()
    return jsonify({'message': 'success', 'data': title, 'status': 200})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
