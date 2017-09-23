#coding:utf8
from selenium import webdriver
import requests
import time
import hashlib


def check_omqq(user,pwd):
    b = webdriver.PhantomJS()
    time.sleep(2)
    b.get("https://m.om.qq.com/mobile/login")
    input = b.find_element_by_xpath('//*[@id="app"]/div/div/div/div/form/label[1]/input')
    pw = b.find_element_by_xpath('//*[@id="app"]/div/div/div/div/form/label[2]/input')
    input.send_keys(user)
    pw.send_keys(pwd)
    bt = b.find_element_by_xpath('//*[@id="app"]/div/div/div/div/div/button')
    bt.click()
    time.sleep(2)
    try:
        b.find_element_by_class_name("om-index")
    except Exception as e:
        return False
    return True


def check_yidian(user,pwd):
    def get_rk(cookie):
        return cookie[0:6] + str(int(time.time() * 1000))
    r = requests.session()
    r.get("https://mp.yidianzixun.com/")
    rk = get_rk(r.cookies.get('DID'))
    res = r.post("https://mp.yidianzixun.com/sign_in?_rk=" + rk, data={
        "username": user,
        "password": pwd
    })
    if res.json().get("userid"):
        return True
    return False


def check_miaopai(user,pwd):
    b = webdriver.PhantomJS()
    b.get("http://creator.miaopai.com/login")
    time.sleep(2)
    input_ = b.find_element_by_xpath('//*[@id="app"]/div/span/main/main/section[1]/div/div[4]/form/div[1]/input')
    pw = b.find_element_by_xpath('//*[@id="app"]/div/span/main/main/section[1]/div/div[4]/form/div[2]/input')
    input_.send_keys(user)
    pw.send_keys(pwd)
    b.find_element_by_xpath('//*[@id="app"]/div/span/main/main/section[1]/div/div[4]/form/button/span').click()
    print(b.find_element_by_tag_name('body').text)
    try:
        b.find_element_by_class_name("el-message")
    except Exception as e:
        print(e)
        return True
    return False


def check_renren(user,pwd):
    def md5(str):
        md = hashlib.md5()
        md.update(str.encode())
        return md.hexdigest()
    req = requests
    res = req.post("http://ucenter.rr.tv/page/login", data={
        "username": user,
        "password": md5(pwd)
    })
    if res.status_code == 200:
        return False
    return True


'''


CREATE TABLE `med_flow` (`flow_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,`plat_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '平台id',`third_id` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '第三方素材平台id',`account_id` int(11) NOT NULL DEFAULT '0' COMMENT '账号id',`account_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '账号名称',`plat_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '平台名称',`user_id` int(11) NOT NULL DEFAULT '0' COMMENT '用户id',`title_name` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '标题名称',`flow_count` int(11) NOT NULL DEFAULT '0' COMMENT '流量',`add_time` datetime NOT NULL,`url` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '视频url',`tag` tinyint(1) NOT NULL DEFAULT '0' COMMENT '标签',`adv_id` tinyint(1) NOT NULL DEFAULT '0' COMMENT '广告id', `audit_status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1待审核2通过3不通过',UNIQUE KEY `flow_id` (`flow_id`),UNIQUE KEY `NewIndex1` (`third_id`,`plat_id`)) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci







 CREATE TABLE `med_flow` (`flow_id` int(11) unsigned NOT NULL AUTO_INCREMENT,                                          `plat_id` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '平台id',                               `third_id` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '第三方素材平台id', `account_id` int(11) NOT NULL DEFAULT '0' COMMENT '账号id',                                     
`account_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '账号名称',      
             `plat_name` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '平台名称',         
             `user_id` int(11) NOT NULL DEFAULT '0' COMMENT '用户id',                                        
             `title_name` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '标题名称',       
             `flow_count` int(11) NOT NULL DEFAULT '0' COMMENT '流量',                                       
             `add_time` datetime NOT NULL,                                                                   
             `url` varchar(250) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '视频url',               
             `tag` tinyint(1) NOT NULL DEFAULT '0' COMMENT '标签',                                           
             `adv_id` tinyint(1) NOT NULL DEFAULT '0' COMMENT '广告id',                                      
             `audit_status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '1待审核2通过3不通过',                   
             UNIQUE KEY `flow_id` (`flow_id`),                                                               
             UNIQUE KEY `NewIndex1` (`third_id`,`plat_id`)                                                   
           ) ENGINE=InnoDB AUTO_INCREMENT=4294967295 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci  

'''
