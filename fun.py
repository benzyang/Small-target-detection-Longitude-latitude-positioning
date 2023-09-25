import folium
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import cv2
import numpy as np
import random
import matplotlib.pyplot as plt


def showimage(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.show()


def createmap(offline_map_path, location, zoom, map_name, whetheropen):
    m = folium.Map(
        location=location, 
        zoom_start=zoom,
        tiles=offline_map_path, 
        attr='M',
        control_scale=False,
        zoom_control = False, 
        double_click_zoom = False
        )

    # 添加经纬度弹出窗口插件
    m.add_child(folium.LatLngPopup())

    m.save(map_name)
    if whetheropen:
        webbrowser.open(map_name)

    return m


def getmapimg(size, map_file):
    current_dir = os.getcwd()
    driver_path = os.path.join(current_dir, "chromedriver.exe")
    save_dir = os.path.join(current_dir, "save")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--window-size={size}, {size}')  # 设置窗口大小为1920x1080
    chrome_options.add_argument('--headless')  # 无界面模式
    # chromedriver_path = "chromedriver.exe"
    driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
    driver.get(f'file://{map_file}')
    time.sleep(3)

    screenshot_file = os.path.join(save_dir, f'map_{size}.png')
    driver.save_screenshot(screenshot_file)
    driver.quit()

    print_text = f"离线地图图像已保存为：{screenshot_file}"
    mapimg = cv2.imread(screenshot_file)

    return mapimg, print_text, screenshot_file


def createtarget(img):
    height, width = img.shape[:2]
    x = random.randint(100, width - 100)
    y = random.randint(100, height - 100)
    img[y, x] = (0, 255, 0)

    print('target location: ', x, ',', y)
    cv2.imwrite('target.png', img)
    target_loc = [x, y]

    return img, target_loc


def match(map, target, target_loc, whethershow):
    map_gray = cv2.cvtColor(map, cv2.COLOR_BGR2GRAY)
    target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(map_gray, target_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc
    bottom_right = (top_left[0] + target.shape[1], top_left[1] + target.shape[0])

    loc = (top_left[0] + target_loc[0], top_left[1] + target_loc[1])

    map_match = map.copy()
    cv2.rectangle(map_match, top_left, bottom_right, (0, 255, 0), 2)
    map_match[loc[1], loc[0]] = (0, 255, 0)
    cv2.imwrite('match.png', map_match) 
    if whethershow:
        showimage(map_match)

    return map_match, loc


def outputlalo(loc, map_file, size, screenshot):
    current_dir = os.getcwd()
    driver_path = os.path.join(current_dir, "chromedriver.exe")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--window-size={size}, {size}')
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

    driver.get(f'file://{map_file}')
    time.sleep(3)

    # 鼠标点击
    actions = ActionChains(driver)
    actions.move_by_offset(loc[0], loc[1]).click().perform()
    time.sleep(5)

    # wait = WebDriverWait(driver, 10)  # 最多等待10秒钟
    # element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'leaflet-popup-content')))

    # 获取经纬度信息
    popup_element = driver.find_element_by_class_name('leaflet-popup-content')
    popup_text = popup_element.text
    latitude = None
    longitude = None

    # 解析经纬度信息
    lines = popup_text.split('\n')
    for line in lines:
        if line.startswith('Latitude'):
            latitude = line.split(': ')[1]
        elif line.startswith('Longitude'):
            longitude = line.split(': ')[1]

    if screenshot:
        current_dir = os.getcwd()
        save_dir = os.path.join(current_dir, "save")
        screenshot_file = os.path.join(save_dir, 'lalo.png')
        driver.save_screenshot(screenshot_file)

    driver.quit()

    return latitude, longitude, screenshot_file


def addmark(la, lo, map, map_save_name):
    m = map
    folium.Marker(location=[la, lo], popup='Mark').add_to(m)
    m.save(map_save_name)
    webbrowser.open(map_save_name)


def imagerotate(img, point, angle):
    # 图像旋转
    height, width = img.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(img, rotation_matrix, (width, height))

    # 坐标旋转
    point_homogeneous = np.array([point[0], point[1], 1])
    rotated_point_homogeneous = np.dot(rotation_matrix, point_homogeneous)
    rotated_point_1 = (round(rotated_point_homogeneous[0]), round(rotated_point_homogeneous[1]))
    
    return rotated_image, rotated_point_1


def rotatematch(map, target, target_loc, whethershow):
    best_val = 0
    best_loc = (0, 0)
    best_point = (0, 0)
    best_angle = 0

    # 地图灰度
    map_gray = cv2.cvtColor(map, cv2.COLOR_BGR2GRAY)

    # 旋转匹配
    for angle in range(-12, 12):
        rotated_target, point = imagerotate(target, target_loc, angle)

        target_gray = cv2.cvtColor(rotated_target, cv2.COLOR_BGR2GRAY)
        mask = np.where(target_gray > 0, 255, 0).astype(np.uint8)
        result = cv2.matchTemplate(map_gray, target_gray, cv2.TM_CCOEFF_NORMED, mask)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        # print(angle)
        # print(max_val)
        if max_val > best_val:
            best_val = max_val
            best_loc = max_loc
            best_point = point
            best_angle = angle


    top_left = best_loc
    bottom_right = (top_left[0] + target.shape[1], top_left[1] + target.shape[0])

    loc = (top_left[0] + best_point[0], top_left[1] + best_point[1])
    loc = (round(loc[0]), round(loc[1]))

    map_match = map.copy()
    cv2.rectangle(map_match, top_left, bottom_right, (0, 255, 0), 2)
    map_match[loc[1], loc[0]] = (0, 255, 0)

    current_dir = os.getcwd()
    save_dir = os.path.join(current_dir, "save")
    match_dir = os.path.join(save_dir, 'rotatematch.png')
    cv2.imwrite(match_dir, map_match) 
    if whethershow:
        showimage(map_match)

    return map_match, loc

