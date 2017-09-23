import requests


headers = {
    "Cookie": "JSESSIONID=POW3Oz2pOGjA1Cb-O-sJ9Q",
    "Accept-Encoding": "gzip, deflate",
    "Tingyun-Process": "true",
    "Host": "a1.go2yd.com",
    "Connection": "Keep-Alive",
    "User-Agent": "okhttp/3.3.0",

}

r = requests.get('http://a1.go2yd.com/Website/channel/news-list-for-vertical?'
'interest_id=d4XLO2ArglN7pnWr0OD5BoppFZoaTgWJVAa12BMsyLxsQvWseqSjl4SUu-wxVInwkxUjHRL5ou8JrKIOF-GZR-DWuz5DPnVLjEJY_iTgcaekw9ljSVmb_TG8Rdh8Zt8E'
'&fields=docid&fields=category&fields=date&fields=image&fields=image_urls&fields=like&fields=source&fields=title&fields=url&fields=comment_count&fields=summary&fields=up&'
'cstart=10&cend=80&appid=yidian&version=020109&platform=1&cv=3.7.2&distribution=app.qq.com'
            ,headers = headers)

print(len(r.json()['result']))
print(r.json()['result'][0])
