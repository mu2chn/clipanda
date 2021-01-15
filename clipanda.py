import requests as rq
import urllib.parse
import argparse
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup

class Config:
    def __init__(self, cookies=None, command="help"):
        self.cookies = cookies
        self.command = command

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

    def fetchSites(self):
        path = "portal"
        res = self.__get(path)
        siteMaps = []
        soup = BeautifulSoup(res.content, PandaClient.parser)
        for tag in soup.find_all("li", class_="nav-menu")[1:]:
            atag = tag.find("a")
            siteMaps.append({
                "name": atag.attrs["title"],
                "siteId": atag.attrs["href"].split("/")[-1]
            })
        return siteMaps

    def fetchResources(self, path: str):
        iframePath = self.__fetchIframePath(path)
        res = self.__get(iframePath)
        soup = BeautifulSoup(res.content, PandaClient.parser)
        resourceMaps = []
        for tag in soup.find_all("td", class_="specialLink")[1:]:
            atag = tag.find_all("a")[1]
            resourceMaps.append({
                "type": "file",
                "href": atag.attrs["href"],
                "name": atag.get_text(strip=True)
            })
        return resourceMaps

    def getSideLink(self, siteId: str, page: str):
        pageMap = {
            "home": 0,
            "resources": 3
        }
        path = f"portal/site/{siteId}"
        res = self.__get(path)
        soup = BeautifulSoup(res.content, PandaClient.parser)
        atag = soup.find_all("a", class_="toolMenuLink")[pageMap[page]]
        try:
            return atag.attrs["href"]
        except KeyError:
            return path

def createConfig():
    psr = argparse.ArgumentParser(description="pandaのclitools")
    psr.add_argument("command", help="[list]")
    psr.add_argument("cookies", help="cookieを指定して下さい")
    args = psr.parse_args()
    return Config(cookies=args.cookies, command=args.command)

if __name__ == "__main__":
    config = Config(command="resources", cookies="JSESSIONID=59271fcc-e25b-4873-a5ab-eaa8410c56ca.panda2g")#createConfig()
    
    pc = PandaClient(config.cookies)

    if config.command == "list":
        sites = pc.fetchSites()
        for site in sites:
            print(f"{site['siteId']}: {site['name']}")
    elif config.command == "resources":
        path = pc.getSideLink("2020-110-9104-000", "resources")
        res = pc.fetchResources(path)
        print(res)
    else:
        print("コマンドが無効です")
