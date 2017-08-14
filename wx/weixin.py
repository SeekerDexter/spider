import requests
import random
import codecs
import tkinter         # 导入Tkinter模块  
from PIL import Image, ImageTk  
import time
import re
import math

class WeiXinSpider(object):        
    def __init__(self, username, password):
        self.reqeust_count = 0
        self.reqeust_method = 'GET'
        self.session = requests.Session()
        self.username = username
        self.password = password
        # ============发现这个必须有，不然微信扫码后，服务器会出错:503===========
        self.init_url = 'https://mp.weixin.qq.com/'
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'mp.weixin.qq.com',
            'Connection': 'keep-alive',
        }
        self.session.get(self.init_url, headers=headers, verify=False)

              
    def ready_data(self, referer, data=None, cookies=None):
        headers = {
            'Host': 'mp.weixin.qq.com',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Referer': referer,
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',              
        }
 
        if self.reqeust_count == 0:
            headers['Origin'] = 'https://mp.weixin.qq.com'

        if data is None:
            data = {
                'username':self.username,
                'pwd':self.password,
                'imgcode':'',
                'f':'json',
                'token':'',
                'lang':'zh_CN',
                'ajax':'1',
            }
        
        if cookies is None:
            cookies = {
                'pgv_pvi': str(self.get_randrom(8)),
                'pgv_si': 's%s'%str(self.get_randrom(8)),
            }

        proxies = {'http':'http://192.168.191.1:8888'}
        return {'headers':headers, 'data':data, 'cookies':cookies, 'proxies':proxies, 'verify':False}
  
    def login_html(self):
        self.login_url = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin'
        referer = 'https://mp.weixin.qq.com/'
        datas = self.ready_data(referer)
        print(datas)
        
        res = self.session.post(self.login_url, **datas)
        res.encoding = 'UTF-8'
        self.reqeust_count += 1
        time.sleep(1)
 
        self.login_cookies = res.headers
        
        return res.text

    def ask_loop(self):
        print('ask_loop...')    
        self.post_token_url = 'https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=ask&token=&lang=zh_CN&token=&lang=zh_CN&f=json&ajax=1&random=0.%s'%str(self.get_randrom(17))
        referer = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=validate&lang=zh_CN&account=%s'%str(self.username)
        datas = self.ready_data(referer, data='')
        res = self.session.get(self.post_token_url, **datas)
        res.encoding = 'UTF-8' 
        self.reqeust_count += 1
        time.sleep(1) 
        
        status = eval(res.text).get('status') 
        if status == 1:
            self.get_token_url()
        else:
            self.ask_loop()
            time.sleep(1)
              

    def get_token_url(self):
        self.post_token_url = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login&token=&lang=zh_CN'
        referer = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=validate&lang=zh_CN&account=%s'%str(self.username)
        data = {
            'token':'',
            'lang':'zh_CN',
            'f':'json',
            'ajax':'1',
            'random':'0.%s'%str(self.get_randrom(17)),
        }
        datas = self.ready_data(referer, data=data)
        res = self.session.post(self.post_token_url, **datas)
        res.encoding = 'UTF-8' 
        self.reqeust_count += 1
        time.sleep(1)       
        self.redirct_url = eval(res.text).get('redirect_url')
        print(self.redirct_url)
        self.token_num = re.search(r'token=(.+)', self.redirct_url).group(1)
        return res.text   

    def get_code_img(self):
        self.code_img_url = 'https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=getqrcode&param=4300&rd=%s'%str(self.get_randrom(3))
        referer = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=validate&lang=zh_CN&account=%s'%self.username
        datas = self.ready_data(referer, data='')
        res = self.session.get(self.code_img_url, **datas)
        img_bin = res.content
        self.reqeust_count += 1
        self.save_file('C:\\code.jpg', img_bin, 'image')
        time.sleep(1)

    def ok_pass(self):
        self.code_ok_url = 'https://mp.weixin.qq.com%s'%self.redirct_url
        referer = 'https://mp.weixin.qq.com/cgi-bin/bizlogin?action=validate&lang=zh_CN&account=%s'%str(self.username)
        datas = self.ready_data(referer, data='')
        res = self.session.get(self.code_ok_url, **datas)
        res.encoding = 'UTF-8'
        html = res.text
        if html.find('消息管理') == -1:
            print('登录失败')
        else:
            print('登录成功')

    #public signal公众号
    def search_pid(self, p_signal, save_post_list):
        self.p_signal = p_signal
        self.save_post_list = save_post_list
        self.search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&token=%s&lang=zh_CN&f=json&ajax=1&random=0.%s&query=%s&begin=0&count=5'%(self.token_num, str(self.get_randrom(16)), p_signal)            
        referer = 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&isMul=1&isNew=1&lang=zh_CN&token=%s'%self.token_num
        datas = self.ready_data(referer, data='')
        res = self.session.get(self.search_url, **datas)
        res.encoding = 'UTF-8'
        
        res_dict = eval(res.text)
        sig_list = res_dict.get('list')
        self.sig_list_fakeid = sig_list[0].get('fakeid').replace('==','')
        self.sig_list_nickname = sig_list[0].get('nickname')
        sig_total = res_dict.get('total')
        time.sleep(1)
    
        if sig_total == 0 :
            print('不存在该公众号')
        elif sig_total > 1:
            print('模糊查询结果有%s个，建议使用微信号精确搜索'%sig_total)
        else:
            self.search_post()
                 
    def search_post(self, begin=0):
        self.search_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?token=%s&lang=zh_CN&f=json&ajax=1&random=0.%s&action=list_ex&begin=%s&count=5&query=&fakeid=%s%%3D%%3D&type=9'%(self.token_num, str(self.get_randrom(17)), begin, self.sig_list_fakeid)        
        referer = 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&isMul=1&isNew=1&lang=zh_CN&token=%s'%self.token_num
        datas = self.ready_data(referer, data='')
        res = self.session.get(self.search_url, **datas)
        res.encoding = 'UTF-8'   
        res_dict = eval(res.text)
        # 保存标题
        title_info = '%s:%s'%(self.sig_list_nickname,self.p_signal)
        self.save_file('C:\\post.txt', title_info, 'file')

        current_count = 0
        current_page = 0 
        # 所有文章总数
        post_count = int(res_dict.get('app_msg_cnt'))
        
        while current_count < post_count:
            # 当前页文章
            app_msg_list = len(res_dict.get('app_msg_list'))
            current_count += app_msg_list
           
            
            time.sleep(1)
            print('已爬取%s篇文章...'%current_count)
            item_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?token=%s&lang=zh_CN&f=json&ajax=1&random=0.%s&action=list_ex&begin=%s&count=5&query=&fakeid=%s%%3D%%3D&type=9'%(self.token_num, str(self.get_randrom(17)), current_page, self.sig_list_fakeid)     
            res = self.session.get(item_url, **datas)
            res.encoding = 'UTF-8'
            res_dict = eval(res.text)
            # 第一页所有文章
            self.post_list = res_dict.get('app_msg_list')  
           
            for post in self.post_list:
                #print(post.get('title'))
                self.save_file('C:\\post.txt', post.get('title'), 'file')

            current_page +=5
                
    @staticmethod
    def get_randrom(num):
        if num == 8:
            return random.randrange(10000000,99999999) 
        elif num == 3:
            return random.randrange(30, 799)
        elif num == 17:
            return random.randint(10000000000000000,39999999999999999)
        elif num == 16:
            return random.randint(1000000000000000,9999999999999999)
            

    @staticmethod
    def save_file(path, data, type='file'):
        if type == 'file':
            with codecs.open(path, 'a', 'utf-8') as f:
                f.write(data+'\n')
        elif type == 'image':
            with open(path, 'wb') as i:
                i.write(data)  
        print('%s保存成功'%type)      


class ScanCode(object):
    #获取到验证码，弹出界面
    def scan_code(self):
        root = tkinter.Tk()
        root.title('微信公众号')
        canvas = tkinter.Canvas(root,  
            width = 472,      # 指定Canvas组件的宽度  
            height = 472,      # 指定Canvas组件的高度  
            bg = 'white')      # 指定Canvas组件的背景色  
         
        image = Image.open("C:\\code.jpg")  
        im = ImageTk.PhotoImage(image)  
           
        canvas.create_image(240,240,image = im)      # 使用create_image将图片添加到Canvas组件中  
       
        canvas.pack()         # 将Canvas添加到主窗口

        btn = tkinter.Button(root, text='扫码完成，点我继续', command = root.quit, bg='red')
        btn.pack()   

        root.mainloop()      
         
def main():
    path = 'C:\\weixin.txt'
    username = 'kizzle@qq.com'
    password = 'x'
    save_post_list = []
    # 创建爬虫对象
    wx = WeiXinSpider(username, password)
    # 获取登录后返回的数据
    res_data = wx.login_html()
    
    # 获取并保存登录二维码
    wx.get_code_img()
    # 创建GUI对象，用来显示二维码
    sc = ScanCode()
    sc.scan_code()
    
    # 扫码过程status的变化：0：未扫码，1：已扫码，4：扫码成功
    wx.ask_loop()
    
    # 检查是否登录成功
    wx.ok_pass()
    
    # 搜索公众号
    wx.search_pid('redhadoop', save_post_list)
    
    
if __name__ == '__main__':
    main()
        
    