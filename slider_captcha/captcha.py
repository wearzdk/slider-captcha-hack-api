import base64
import time
import cv2
import numpy as np


class SliderCaptcha(object):
    def _show(self, name):
        '''展示圈出来的位置'''
        cv2.imshow('Show', name)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def _tran_canny(self, image):
        """消除噪声"""
        image = cv2.GaussianBlur(image, (3, 3), 0)
        return cv2.Canny(image, 50, 150)

    def _cut_slider(self, image, alpha=100):
        """裁剪滑块"""
        # 识别出alpha通道（透明度），用于后面获取不透明的部分
        alpha_channel = image[:, :, 3]
        # 创建一个mask，值为True的部分表示对应的点不透明
        mask = alpha_channel > alpha
        # 使用np.where找到图像中所有不透明的点
        nonzero_points = np.argwhere(mask)
        # 使用cv2.boundingRect找到不透明部分的边界
        y0, x0 = np.min(nonzero_points, axis=0)
        y1, x1 = np.max(nonzero_points, axis=0)
        return image[y0:y1, x0:x1]

    def base64_to_cv2(self, image_code):
        # 解码
        img_data = base64.b64decode(image_code)
        # 转为numpy
        img_array = np.frombuffer(img_data, np.uint8)
        # 转成opencv可用格式
        img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
        return img

    def cv2_to_base64(self, image):
        # 转为字符串
        img_encode = cv2.imencode('.png', image)[1]
        # base64编码
        img_base64 = str(base64.b64encode(img_encode))[2:-1]
        return img_base64

    def detect_displacement(self, img_slider, img_background) -> int:
        """detect displacement"""
        # # 转为灰度模式
        img_slider = cv2.cvtColor(img_slider, cv2.COLOR_BGR2GRAY)
        img_background = cv2.cvtColor(img_background, cv2.COLOR_BGR2GRAY)

        # 寻找最佳匹配
        res = cv2.matchTemplate(self._tran_canny(
            img_slider), self._tran_canny(img_background), cv2.TM_CCOEFF_NORMED)
        # 最小值，最大值，并得到最小值, 最大值的索引
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        top_left = max_loc[0]  # 横坐标
        # 结果
        # x, y = max_loc
        # w, h = image.shape[::-1]  # 宽高
        # cv2.rectangle(template, (x, y), (x + w, y + h), (7, 249, 151), 2)
        # show(template)
        return top_left

    def do_captcha(self, img_slider_b64, image_background_b64, auto_cut=True):
        """
        执行滑动验证码
        :param img_slider_b64: 滑块图片
        :param image_background_b64: 背景图片
        :param auto_cut: 是否自动裁剪滑块图片
        :return: 滑块x轴坐标
        """
        img_slider = self.base64_to_cv2(img_slider_b64)
        img_background = self.base64_to_cv2(image_background_b64)
        if auto_cut:
            img_slider = self._cut_slider(img_slider)
        top_left = self.detect_displacement(img_slider, img_background)
        return top_left


if __name__ == '__main__':
    slider_captcha = SliderCaptcha()
    start_time = time.time()

    def get_base64(file_path):
        with open(file_path, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            s = base64_data.decode()
            return s

    img_slider_b64 = get_base64('target.png')
    image_background_b64 = get_base64('background.jpeg')
    top_left = slider_captcha.do_captcha(img_slider_b64, image_background_b64)
    print(top_left)
    print("耗时：", time.time() - start_time, "秒")
