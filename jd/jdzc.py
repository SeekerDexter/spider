import requests
import re
import math
import time
import codecs

def ready_data(url,page=1):
    headers = {
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Referer': 'http://z.jd.com/bigger/search.html',
        'Accept-Language': 'zh-CN',
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'z.jd.com',
        'Connection': 'Keep-Alive',
    }
    data ={
        'status':'4',
        'sort':'zhtj',
        'categoryId':'',
        'parentCategoryId':'',
        'sceneEnd':'',
        'productEnd':'',
        'keyword':'',
        'page':page,
    }
    return {'url':url, 'headers':headers, 'data':data, 'verify':False}

def get_html(**kwargs):
    try:
        r = requests.post(**kwargs)
        r.raise_for_status()
        r.encoding = 'UTF-8'
        return r.text
    except Exception as e:
        print(e)
        return ''

def save_to_file(path, data):
    with codecs.open(path, 'a', 'utf-8') as f:
        f.write(data)

def parse_html(data_list, html, datas):
    # 总项目数
    total_project = re.search(r'l-statistics fr.+g>(\d+?)<', html).group(1)
    total_project = eval(total_project)
    per_page = 16
    # 要爬取的页数
    fetch_pages = math.ceil(total_project/per_page)
    # 先测试2页试试
    # fetch_pages = 2
    
    for i in range(1, fetch_pages+1):
        try:
            print('请稍等(共要爬取%s页)...正在爬取第%s页'%(fetch_pages,i))
            
            datas['data']['page'] = i
            html = get_html(**datas)
            titles = re.findall(r'link-tit.+_blank\">(.+?)</h4>',html)
            p_percents =  re.findall(r'p-percent\">(.+?)<',html)         
            p_extras =  re.findall(r'p-extra\">(.+?)<',html)
            urls = re.findall(r'/scene/(.+.html)', html)        
            for j in range(1, 17):
                item1 = '%s/%s'%(p_percents[(j-1)*3+0],p_extras[(j-1)*3+0])
                item2 = '%s/%s'%(p_percents[(j-1)*3+1],p_extras[(j-1)*3+1])
                item3 = '%s/%s'%(p_percents[(j-1)*3+2],p_extras[(j-1)*3+2])
                data_list.append([item1,item2,item3,titles[j-1], 'http://z.jd.com/project/details/%s'%urls[j-1]])
            time.sleep(1)
        except:      
            continue
                       
def print_info(save_path, data_list):
    templates = '{:<8}\t{:<12}\t{:<8}\t{:<20}\t{:<40}\n'
    title = templates.format('完成度','筹集款','项目时间','项目名称', '项目地址')
    print(title)
    save_to_file(save_path, title)
    for i in range(len(data_list)):
        content = templates.format(data_list[i][0],data_list[i][1],data_list[i][2],data_list[i][3],data_list[i][4])
        print(content)
        save_to_file(save_path, content)
        

def main():
    jdzc_url = 'http://z.jd.com/bigger/search.html'
    save_path = 'C:\\jdzc.txt'
    datas = ready_data(jdzc_url)

    html = get_html(**datas)
   
    data_list = []
    parse_html(data_list, html, datas)
    print_info(save_path, data_list)
    

if __name__ == '__main__':
    main()



    