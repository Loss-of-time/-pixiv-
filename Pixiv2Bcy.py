from selenium import webdriver
import time
import os
import requests
import threading
import shutil


class Break(Exception):  # 自定义错误，用于多级跳出
    pass


class Dothat(Exception):  # 自定义错误，用于多级跳出
    pass


def getImg(page=10):
    def theNextStep(add=0, awDict={}, aimLi=['東方', '東方Project'], exceptLi=['漫画', '四コマ', '東方4コマ']):
        doThat = False
        try:  # 报错形式的多级跳出
            for awTag in awDict['tags']:
                for exceptTag in exceptLi:
                    if awTag == exceptTag:
                        raise Break
            for awTag in awDict['tags']:
                for aimTag in aimLi:
                    if awTag == aimTag:  # 判断是否含有我们需要的标签
                        raise Dothat
        except Break:
            doThat = False
        except Dothat:
            doThat = True
        tags = ''
        for awTag in awDict['tags']:
            try:
                tag = J2C[awTag]
                tags += f'_{tag}'
            except:
                pass
        if doThat:
            awId = awDict['illust_id']
            re = requests.get(f'https://www.pixiv.net/ajax/illust/{awId}/pages?lang=zh', headers={
                'referer': f'https://www.pixiv.net/artworks/{awId}'})
            if len(re.json()['body']) == 1:  # 不爬取含有多个图片的作品
                img = re.json()['body'][0]
                imgUrl = img['urls']['original']
                imgRe = requests.get(
                    imgUrl, headers={'referer': f'https://www.pixiv.net/artworks/{awId}'})
                num = (3-len(str(add)))*'0'+str(add)
                fileName = f'./2BCY/{num}{tags}_{imgUrl[57:]}'
                print(f'{fileName} has downloaded.')
                with open(fileName, 'wb') as f:
                    f.write(imgRe.content)
        return 0
    # 获取所有PID
    awLiLi = []
    for i in range(page):
        rankUrl = f'https://www.pixiv.net/ranking.php?p={i+1}&format=json'
        re = requests.get(rankUrl)
        awLi = re.json()['contents']  # 这里得到一个字典列表，字典中有上榜图片的信息
        awLiLi.append(awLi)
    # 创建线程开始下载
    tds = []
    add = 0
    for awLi in awLiLi:
        for awDict in awLi:
            td = threading.Thread(target=theNextStep, args=(add, awDict))
            tds.append(td)
            add += 1
    for td in tds:
        td.start()
    for td in tds:
        td.join()


def showImg():
    url = 'https://bcy.net/'
    wdPath = r"C:\edgedriver_win64\msedgedriver.exe"
    wd = webdriver.Edge(wdPath)
    wd.get(url)
    #
    wd.find_element_by_xpath(
        '//*[@id="app"]/div/div[1]/div[2]/div[1]/form/div[3]/div/span[3]').click()  # 使用QQ登录
    wd.switch_to.frame('ptlogin_iframe')  # 跳转到所需frame
    wd.find_element_by_id('switcher_plogin').click()  # 使用账号密码登录
    u = wd.find_element_by_id('u')
    p = wd.find_element_by_id('p')
    userId = '你的qq号'
    u.send_keys(userId)
    passWord = '你的密码'
    p.send_keys(passWord)
    wd.find_element_by_id('login_button').click()
    #
    time.sleep(5)
    wd.get('https://bcy.net/item/newnote')
    rootPath = os.path.dirname(__file__)+'\\2BCY\\'
    imgLi = os.listdir(r'./2BCY')
    #
    content = wd.find_element_by_id('content')
    content.send_keys('希望国内用户也可以欣赏Pixiv上优秀东方project作品。\nPID:')
    dict_ = {}
    # 发送图片
    dl = []
    for i in range(3):
        imgInput = wd.find_element_by_xpath(
            '/html/body/div[1]/form/div/div[1]/div/div[1]/div/ul//input')
        imgInput.send_keys(rootPath+imgLi[i])
        time.sleep(1)
        pid = ''.join(imgLi[i].split('_')[-2])
        dl.append(pid) #
        content.send_keys(f'{pid} ')
        if len(imgLi[i].split('_')) > 3:
            dict_[imgLi[i].split('_')[-3]] = 1
    charactar = list(dict_.keys())
    #
    with open(f'./uped/{len(os.listdir("./uped"))+1}','w') as f:
        f.write(str(dl))
    #
    wd.find_element_by_id('js-add-watermark').click()
    addTag = wd.find_element_by_class_name('js-add-tag-input')
    wd.find_element_by_class_name('btn--add-tag').click()
    for tag in ['搬运', '东方project', '东方', '绘画', 'selenium']:
        addTag.send_keys(tag)
        wd.find_element_by_class_name('i-tag-confirm-white').click()
    for tag in charactar:
        addTag.send_keys(tag)
        wd.find_element_by_class_name('i-tag-confirm-white').click()
    #
    wd.find_element_by_id('js-submit').click()
    time.sleep(15)
    wd.close()


def cycle():
    try:
        shutil.rmtree('./2BCY')
    finally:
        # 创建要保存到的文件夹
        if not os.path.exists('./2BCY'):
            os.mkdir('./2BCY')

def removeUped():
    dl = []
    for i in os.listdir('./uped'):
        with open(f'./uped/{i}','r',encoding='utf-8') as f:
            f = f.read()
            f = eval(f)
        dl += f
    print(dl)
    for i in os.listdir('./2BCY'):
        for o in dl:
            if i.split('_')[-2] == o:
                os.remove(f'./2BCY/{i}')
                break

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))  # 设定工作目录为当前文件夹,方便在vs code 中调用

    # 中文转日文
    J2C = {'古明地こいし': '古明地恋', '古明地さとり': '古明地觉', '魂魄妖夢': '魂魄妖梦', 'フランドール・スカーレット': '芙兰朵露',
           '琪露诺': '琪露诺', '博麗霊夢': '博丽灵梦', 'レミリア': '蕾米莉亚', '西行寺幽々子': '西行寺幽幽子', '射命丸文': '射命丸文'}

    # 调用
    cycle()
    getImg()
    removeUped()
    showImg()

