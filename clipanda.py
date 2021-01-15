import requests as rq
import urllib.parse
import argparse, os
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup

class Config:
    def __init__(self, cookies=None, command="help"):
        self.cookies = cookies
        self.command = command

class HttpResponse:
    def __init__(self, status: int, content):
        self.status = status
        self.content = content

class PandaClient:
    
    baseurl = "https://panda.ecs.kyoto-u.ac.jp"
    parser = "html5lib"

    @staticmethod
    def absolutePath(path):
        return urllib.parse.urljoin(PandaClient.baseurl, path)

    def __init__(self, cookies: str):
        self.__cookies = cookies

    def __covertRespose(self, res):
        return HttpResponse(res.status_code, res.content)

    def __get(self, relativePath: str):
        url = PandaClient.absolutePath(relativePath)
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

    def downloadFiles(self, path: str):
        res = self.__get(path)
        return res.content        

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

    def fetchResources(self, siteId: str):
        path = f"access/content/group/{siteId}/"
        res = self.__get(path)
        soup = BeautifulSoup(res.content, PandaClient.parser)
        resourceMaps = []
        for tag in soup.find_all("li")[1:]:
            if(tag["class"][0] == "folder"):
                atag = tag.find("a")
                resourceMaps.append({
                    "type": "folder",
                    "children": self.fetchResources(f"{siteId}/{atag.attrs['href']}"),
                    "name": atag.get_text(strip=True)
                })
            elif(tag["class"][0] == "file"):
                atag = tag.find("a")
                resourceMaps.append({
                    "type": "file",
                    "href": path+atag.attrs["href"],
                    "name": atag.get_text(strip=True)
                })
        return resourceMaps

    def getSideLink(self, siteId: str, page: str):
        pageMap = {
            "home": 0,
            "resources": "授業資料（リソース）"
        }
        path = f"portal/site/{siteId}"
        res = self.__get(path)
        soup = BeautifulSoup(res.content, PandaClient.parser)
        atag = None
        for tag in soup.find_all("a", class_="toolMenuLink"):
            if tag.find_all("span")[1].get_text(strip=True) == pageMap[page]:
                atag = tag
                break
        try:
            return atag.attrs["href"]
        except KeyError:
            return path

def saveFile(directory, filename, content):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, filename), "wb") as f:
        f.write(content)

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
        res = pc.fetchResources("2020-110-9079-000")
        def dowmloads(res, baseDir="content/"):
            for r in res:
                if r["type"] == "file":
                    binary = pc.downloadFiles(r["href"])
                    saveFile(baseDir, r["name"], binary)
                    pass
                elif r["type"] == "folder":
                    dowmloads(r["children"], baseDir=os.path.join(baseDir, r["name"]))
        dowmloads(res)
    else:
        print("コマンドが無効です")
