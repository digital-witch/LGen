import requests
from bs4 import BeautifulSoup

#https://api.proxyscrape.com/?request=getproxies&proxytype=http

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
}

def downloadProxyScrapeList():
    proxyList = []
    try:
        response = requests.get('https://api.proxyscrape.com/?request=getproxies&proxytype=http', headers=header, stream=True)
    except Exception as ex:
        print(ex)
        pass
    if response.status_code == 200:
        for line in response.iter_lines(decode_unicode=True):
            if line:
                proxyList.append(line)
        #with open(outputname, 'wb+') as file:
            #file.write(response.content)
    #return len(open(outputname).readlines(  ))
    return proxyList

def checkProxy(proxyIP, url):
    proxy = {
        'http': proxyIP
    }

    try:
        response = requests.get(url, headers=header, proxies=proxy)
        if response.status_code == 200:
            return proxyIP
        else:
            return False
    except Exception as ex:
        pass


def createProxyFile(filename):
    f = open(filename, 'w+')

def writeProxyFile(filename, data):
    f = open(filename, 'a')

    with f:
        f.write(data+'\n')

def checkProxyList(proxyfile, url, outputname): #proxyfile should be a list of proxies seperated by newlines, url should be the url to check against
    count = 0
    file = open(proxyfile, 'r')
    checkedfile = open(outputname, 'w+')
    for line in file:

        proxy = {
            'http': line
        }

        try:
            response = requests.get(url, headers=header, proxies=proxy)
            if response.status_code == 200:
                checkedfile.write(line)
                count += 1
        except Exception as ex:
            pass
    file.close()
    os.remove(proxyfile)
    return count