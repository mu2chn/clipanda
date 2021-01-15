import requests as rq
import urllib.parse
import argparse
from http.cookies import SimpleCookie

class Config:
    def __init__(self, cookies=None):
        self.cookies = cookies

class PandaClient:
    
    baseurl = "https://panda.ecs.kyoto-u.ac.jp"

    def __init__(self, cookies: str):
        self.__cookies = cookies

    def __get(self, relativePath: str):
        url = urllib.parse.urljoin(PandaClient.baseurl, relativePath)
        sc = SimpleCookie()
        sc.load(self.__cookies)
        cookieDict = {}
        for key, morsel in sc.items():
            cookieDict[key] = morsel.coded_value
        return rq.get(url, cookies=cookieDict)

    def fetchResources(self):
        path = "portal/site/2020-110-9031-000/page/744e68fb-5aee-453a-b085-17798934b88e"
        return self.__get(path)

def createConfig():
    psr = argparse.ArgumentParser(description="pandaのclitools")
    psr.add_argument("cookies", help="cookieを指定して下さい")

    args = psr.parse_args()
    return Config(cookies=args.cookies)

if __name__ == "__main__":
    config = Config(cookies="JSESSIONID=59271fcc-e25b-4873-a5ab-eaa8410c56ca.panda2g")#createConfig()
    
    pc = PandaClient(config.cookies)
    print(pc.fetchResources())

