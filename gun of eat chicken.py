import requests,json,os,pygal,re,time
# 打开url并返回一个response
def open_url(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Referer':'http://pg.qq.com/web201801/ziliao_list.shtml',
    }
    html = requests.get(url,headers=headers)
    return html
# 获取json数据包并整理
def get_data(html):
    data = json.loads(html)
    # 遍历武器分类
    for each in data['wq_47']:
        # 获得武器分类的名称
        weapon_sort = each['lx_b5'][0]
        # 避开近战武器这一分类
        if weapon_sort['mc_94'] == '近战武器':
            break
        # 武器分类文件夹的路径
        sort_foldername = 'E:\Eat_chicken\%s'%weapon_sort['mc_94']
        # 创建武器分类文件夹
        if not os.path.exists(sort_foldername):
            os.makedirs(sort_foldername)
        # 改变默认目录至武器分类文件夹下
        os.chdir(sort_foldername)
        # 在武器分类文件夹中创建该类的所有武器的雷达图
        make_radar_all(each)
        # 创建武器分类下的所有武器的文件夹
        get_weapon(weapon_sort)

# 创建武器分类下的所有武器的文件夹
def get_weapon(weapon_sort):
    # 遍历该武器分类下的所有武器
    for each in weapon_sort['dx_2a']:
        # 武器的文件夹路径
        weapondir = 'E:\Eat_chicken\%s\%s'%(weapon_sort['mc_94'],each['mc_94'])
        # 如果武器文件夹不存在，则进行下面的操作，否则跳过
        if not os.path.exists(weapondir):
            os.makedirs(weapondir)
            os.chdir(weapondir)
            # 整理武器的信息数据并存入文件中
            make_weapon_message(each)
            # 创建武器的雷达图，传入武器属性的字典和武器名
            make_radar(each['wqxq_f9'][0]['ldt_79'][0],each['mc_94'])
            # 让程序适当休息，防止被服务器封ip
            time.sleep(3)

# 整理武器的信息数据并存入文件中
def make_weapon_message(weapon):
    # 武器的优点
    advantage = weapon['wqxq_f9'][0]['yd_c6']
    # 武器的优点
    disadvantage = weapon['wqxq_f9'][0]['qd_00']
    # 武器的标签
    flag = weapon['jb_f0']
    # 武器的对于的子弹口径
    caliber = weapon['zdkj_a2']
    # 武器的伤害程度
    damage = re.findall(r": '(.*?)'",str(weapon['wqxq_f9'][0]['wqshst_a7'])+str(weapon['wqxq_f9'][0]['stshtb_fd']))
    print(damage)
    # 武器伤害的内容
    content = '武器伤害：\n射击身体：裸（%s枪致死），1级护甲（%s枪致死），2级护甲（%s枪致死），3级护甲（%s枪致死）' \
              '\n射击头部：裸（%s枪致死），1级护甲（%s枪致死），2级护甲（%s枪致死），3级护甲（%s枪致死）'\
              %(damage[0],damage[1],damage[2],damage[3],damage[4],damage[5],damage[6],damage[7])
    # 创建.txt文件写入武器的信息
    with open('%s的简介.txt'%weapon['mc_94'],'w') as g:
        g.write('%s(%s)\n口径：%s\n优点：%s\n缺点：%s\n%s'%(weapon['mc_94'],flag,caliber,advantage,disadvantage,content))
    print('武器图片\nhttp:%s'%weapon['tp_93'])
    # 获取武器的图片的html文件
    weapon_pic = open_url(r'http:%s'%weapon['tp_93']).content
    # 创建武器图片的文件
    with open(weapon['mc_94']+'.jpg','wb') as f:
        f.write(weapon_pic)
    try:
        # 遍历武器的最佳配件
        for i in weapon['wqxq_f9'][0]['pjzh_7a']:
            # 获得武器配件的图片的html文件
            parts_pic = open_url(r'http:%s'%i['pjtp_ea']).content
            # 创建武器配件图片的文件
            with open('最佳配件之%s(%s).jpg' % (i['pjmc_2a'],i['pjms_0a']),'wb') as p:
                p.write(parts_pic)
            print('%s(%s)' % (i['pjmc_2a'],i['pjms_0a']))
    # 跳过没有最佳配件的武器
    except KeyError:
        pass
# 创建武器的雷达图，传入武器属性的字典和武器名
def make_radar(datadic,name):
    # 实例化Radar这个类，fill代表是否填充，range代表每个属性的值范围
    radar_chart = pygal.Radar(fill='True',range=(0,100))
    # 创建雷达图的标题
    radar_chart.title = '武器属性'
    # 创建雷达图的属性
    radar_chart.x_labels = ['威力','射程','射速','稳定性','子弹数']
    t = []
    # 遍历每个属性字典中的值，并追加到t列表中
    for i in datadic:
        t.append(int(datadic[i]))
    # 添加武器的属性值和武器名到雷达图中
    radar_chart.add(name,t)
    # 最后命名雷达图的文件
    radar_chart.render_to_file('radar(枪支性能).svg')
# 在武器分类文件夹中创建该类的所有武器的雷达图
def make_radar_all(data):
    print(str(data))
    # 获得武器分类下的所有武器属性的元组组成的属性列表
    wl_list = re.findall("'ldt_79': \[{'wl_45': '(\d*)', 'sc_54': '(\d*)', 'ss_d0': '(\d*)', 'wdx_a7': '(\d*)', 'zds_62': '(\d*)'}]",str(data))
    # 获得武器分类下的所有武器名称
    name_list = re.findall("{'mc_94': '([^,]*?)', 'tp_93':",str(data))
    radar_chart = pygal.Radar(range=(0,100))
    radar_chart.title = '%s的属性'%data['lx_b5'][0]['mc_94']
    radar_chart.x_labels = ['威力','射程','射速','稳定性','子弹数']
    # 遍历武器分类列表下的所有武器的属性，并添加每个武器的属性值和武器名到雷达图中
    for index in range(len(wl_list)):
        t = []
        # 获得武器的名称
        name = name_list[index]
        # 遍历武器的所有属性值，并转为整型追加到t列表中
        for each in wl_list[index]:
            t.append(int(each))
        radar_chart.add(name, t)
    radar_chart.render_to_file('radar_%s.svg'%radar_chart.title[0:-3])

if __name__ == '__main__':
    # 所有的武器和配件的信息都在json文件中，通过访问网址可获得
    url = 'http://pg.qq.com/zlkdatasys/data_zlk_zlzx.json'
    get_data(open_url(url).text)