import cv2
import numpy as np
from PIL import Image
import os


# 定义颜色范围
# red   [120 255 255]
lower_red = (0,255,255)
upper_red = (255,255,255) 

# blue  [ 90 255 255]
lower_blue = (120,255,150)
upper_blue = (120,255,255)

# yellow    [  0 255 255]
# lower_yellow = (20, 80,80)
lower_yellow = (0, 255,255)
upper_yellow = (40,255,255)


# 目标检测
def detect(img, color='red'):
    hsvimg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 定义 color 范围
    if color == 'red':
        color_interval = (lower_red, upper_red)
    elif color == 'blue':
        color_interval = (lower_blue, upper_blue)
    elif color == 'yellow':
        color_interval = (lower_yellow, upper_yellow)

    # 根据 color 范围提取图像区域
    mask = cv2.inRange(hsvimg, color_interval[0], color_interval[1])
    result = cv2.bitwise_and(img, img, mask=mask)

    # K-means
    Z = result.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 0.1)
    K = 2
    ret, label, center=cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((result.shape))
    gray = cv2.cvtColor(res2, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    loc = (0, 0)
    # 标记方框
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        center_x = x + w/2
        center_y = y + h/2
        loc = (round(center_x), round(center_y))

        pad_w = 10
        pad_h = 10
        pad_x = 10
        pad_y = 10  

        cv2.rectangle(img, (x-pad_x,y-pad_y), (x+w+pad_w,y+h+pad_h), (0, 255, 255), 1)

    current_dir = os.getcwd()
    save_dir = os.path.join(current_dir, "save")
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
        print('create save')
    else:
        print('save exhited')
    img_path = os.path.join(save_dir, "result.png")
    cv2.imwrite(img_path, img)
    
    return img, img_path, loc

def adjust(img, alpha=1, beta=0):
    adjusted_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

    return adjusted_img