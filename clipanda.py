import requests as rq
import urllib.parse
import argparse, os
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup

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

class CommandHandler:

    @staticmethod
    def list(args):
        pc = PandaClient(args.cookies)
        sites = pc.fetchSites()
        for site in sites:
            if args.only_site_id:
                print(f"{site['siteId']}")
            else:
                print(f"{site['siteId']}: {site['name']}")

    @staticmethod
    def downloadResources(args):
        pc = PandaClient(args.cookies)
        res = pc.fetchResources(args.site_id)
        directory = args.directory
        def dowmloads(res, baseDir=directory):
            for r in res:
                if r["type"] == "file":
                    binary = pc.downloadFiles(r["href"])
                    saveFile(baseDir, r["name"], binary)
                    pass
                elif r["type"] == "folder":
                    dowmloads(r["children"], baseDir=os.path.join(baseDir, r["name"]))
        dowmloads(res)

def saveFile(directory, filename, content):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, filename), "wb") as f:
        f.write(content)

if __name__ == "__main__":

    psr = argparse.ArgumentParser(description="cli tools for panda")
    subpsrs = psr.add_subparsers()
    
    psr_sites = subpsrs.add_parser("sites", help="see sites -h")
    psr_sites.set_defaults(handler=CommandHandler.list)
    psr_sites.add_argument("-c", "--cookies", required=True, help="select cookies")
    psr_sites.add_argument("--only-site-id", action='store_true')

    psr_resources = subpsrs.add_parser("save", help="see save -h")
    psr_resources.set_defaults(handler=CommandHandler.downloadResources)
    psr_resources.add_argument("-c", "--cookies", required=True, help="select cookies")
    psr_resources.add_argument("-s", "--site-id", required=True, help="select site id")
    psr_resources.add_argument("-d", "--directory", default="content/", help="select site id")

    args = psr.parse_args()

    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        psr.print_help()
