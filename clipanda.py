import requests as rq
import urllib.parse
import argparse
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup

class Config:
    def __init__(self, cookies=None):
        self.cookies = cookies

class HttpResponse:
    def __init__(self, status: int, content: str):
        self.status = status
        self.content = content

class PandaClient:
    
    baseurl = "https://panda.ecs.kyoto-u.ac.jp"
    parser = "html5lib"

    def __init__(self, cookies: str):
        self.__cookies = cookies

    def __covertRespose(self, res):
        return HttpResponse(res.status_code, res.text)

    def __get(self, relativePath: str):
        url = urllib.parse.urljoin(PandaClient.baseurl, relativePath)
        sc = SimpleCookie()
        sc.load(self.__cookies)
        cookieDict = {}
        for key, morsel in sc.items():
            cookieDict[key] = morsel.coded_value
        res = rq.get(url, cookies=cookieDict)
        return self.__covertRespose(res)

    def __fetchIframePath(self, path):
        res = self.__get(path)
        soup = BeautifulSoup(res.content, PandaClient.parser)
        url = soup.find("iframe").attrs["src"]
        return urllib.parse.urlparse(url).path

    def fetchResources(self):
        path = "portal/site/2020-110-9104-000/page/4dd1e68e-52cc-4f8e-9a4d-9e0f0526f2b7"
        iframePath = self.__fetchIframePath(path)
        res = self.__get(iframePath)
        soup = BeautifulSoup(res.content, PandaClient.parser)
        resourceMap = []
        for tag in soup.find_all("td", class_="specialLink")[1:]:
            atag = tag.find_all("a")[1]
            resourceMap.append({
                "type": "file",
                "href": atag.attrs["href"],
                "name": atag.get_text(strip=True)
            })
        return resourceMap


def createConfig():
    psr = argparse.ArgumentParser(description="pandaのclitools")
    psr.add_argument("cookies", help="cookieを指定して下さい")

    args = psr.parse_args()
    return Config(cookies=args.cookies)

if __name__ == "__main__":
    config = Config(cookies="JSESSIONID=59271fcc-e25b-4873-a5ab-eaa8410c56ca.panda2g")#createConfig()
    
    pc = PandaClient(config.cookies)

    pc.fetchResources()
