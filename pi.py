from aip import AipFace
from picamera import PiCamera
import RPi.GPIO as GPIO
import pyautogui
import urllib.request
import base64
import time
import json
import subprocess

config_file = {}
with open("./config.json", "r") as f:
    config_file=json.load(f)
    print("加载配置文件完成")

# 百度人脸识别API账号信息
APP_ID = config_file['APP_ID']
API_KEY = config_file['API_KEY']
SECRET_KEY = config_file['SECRET_KEY']
client = AipFace(APP_ID, API_KEY, SECRET_KEY)  # 创建一个客户端用以访问百度云

# 图像编码方式
IMAGE_TYPE = config_file['IMAGE_TYPE']
camera = PiCamera()  # 定义一个摄像头对象

# 用户组
GROUP = config_file['GROUP']

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.output(26, False)


# 照相函数
def getimage():
    # camera.resolution = (1024, 768)  # 摄像界面为1024*768
    # camera.start_preview()  # 开始摄像
    # time.sleep(2)
    camera.capture('faceimage.jpg')  # 拍照并保存
    # time.sleep(2)

# 对图片的格式进行转换
def transimage():
    f = open('faceimage.jpg', 'rb')
    img = base64.b64encode(f.read())
    return img

# 上传到百度api进行人脸检测
def go_api(image):
    try:
        result = client.search(str(image, 'utf-8'),
                               IMAGE_TYPE, GROUP)  # 在百度云人脸库中寻找有没有匹配的人脸
    except json.decoder.JSONDecodeError as err:
        # GPIO.output(26,True)
        print('网络故障，请刷卡开门并联系管理员！')
        f = open('Log.txt', 'a')
        f.write("NETWORKERR" + "Time:" +
                str(time.asctime(time.localtime(time.time())))+'\n')
        f.close()
    except json.decoder.JSONDecodeError as err:
        # GPIO.output(26,True)
        print('网络故障，请刷卡开门并联系管理员！')
        f = open('Log.txt', 'a')
        f.write("NETWORKERR" + "Time:" +
                str(time.asctime(time.localtime(time.time())))+'\n')
        f.close()
    else:
        if result['error_msg'] == 'SUCCESS':  # 如果成功了
            name = result['result']['user_list'][0]['user_id']  # 获取名字
            score = result['result']['user_list'][0]['score']  # 获取相似度
            if score > 80:  # 如果相似度大于80
                GPIO.output(26, True)
                print(name+"，欢迎！ 门已开")
                # os.system('mplayer /home/pi/Desktop/open.mp3')
                ret = subprocess.run('mplayer /home/pi/Desktop/open.mp3', shell=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                time.sleep(1)
            else:
                print("对不起，我不认识你！")
                # p = vlc.MediaPlayer("file:///home/pi/Desktop/fail.mp3")
                # p.play()
                name = 'Unknow'
                return 0
            curren_time = time.asctime(time.localtime(time.time()))  # 获取当前时间

            # 将人员出入的记录保存到Log.txt中
            f = open('Log.txt', 'a')
            f.write("Person: " + name + "     " +
                    "Time:" + str(curren_time)+'\n')
            f.close()
            return 1
        elif result['error_msg'] == 'pic not has face':
            # p = vlc.MediaPlayer("file:///home/pi/Desktop/close.mp3")
            # p.play()
            # print('检测不到人脸')
            # time.sleep(2)
            return 0
        else:
            print(result['error_code'])
            return 0


# 主函数
if __name__ == '__main__':
    GPIO.output(26, False)
    camera.resolution = (1024, 768)  # 摄像界面为1024*768
    camera.start_preview()  # 开始摄像
    count = 0
    while True:
        count+=1
        getimage()  # 拍照
        img = transimage()  # 转换照片格式
        res = go_api(img)  # 将转换了格式的图片上传到百度云
        if res == 1:
            GPIO.output(26, False)
        print('')

        if count==10:
            count = 0
            pyautogui.click()
            print('系统运行中......')
        time.sleep(0.3)
