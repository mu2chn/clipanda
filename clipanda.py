import requests as rq
import urllib.parse
import argparse, os, json, re, getpass, sys
from http.cookies import SimpleCookie

# sakai reference
# https://confluence.sakaiproject.org/download/attachments/75662075/KeitaiAPI.pdf

class HttpResponse:
    def __init__(self, status: int, content):
        self.status = status
        self.content = content


class PandaFile:

    @staticmethod
    def fromResponse(json):
        directory = "/".join(json["container"].split("/")[4:])
        path = urllib.parse.urlparse(json["url"]).path
        return PandaFile(filename=json["title"], directory=directory, size=int(json["size"]), path=path)    

    def __init__(self, filename, directory: str, path: str, size=None):
        self.filename = filename
        self.directory = directory
        self.size = size
        # path of url
        self.path = path

    def localPath(self):
        return os.path.join(self.directory, self.filename)


class PandaSite:

    @staticmethod
    def fromResponse(json):
        return PandaSite(json["id"], json["type"], name=json["title"])

    def __init__(self, siteId: str, sitetype: str, name=""):
        self.siteId = siteId
        self.name = name
        # course or project
        self.sitetype = sitetype


class LoginFailedException(Exception):
    def __str__(self):
        return "login faild. Is ecs-id or password correct?"


class PandaClient:
    
    baseurl = "https://panda.ecs.kyoto-u.ac.jp"

    @staticmethod
    def absolutePath(path):
        return urllib.parse.urljoin(PandaClient.baseurl, path)

    def __init__(self, cookies: str):
        self.__cookies = cookies

    @staticmethod
    def __covertRespose(res):
        return HttpResponse(res.status_code, res.content)

    def __get(self, relativePath: str):
        url = PandaClient.absolutePath(relativePath)
        sc = SimpleCookie()
        sc.load(self.__cookies)
        cookieDict = {}
        for key, morsel in sc.items():
            cookieDict[key] = morsel.coded_value
        res = rq.get(url, cookies=cookieDict)
        return PandaClient.__covertRespose(res)

    def downloadFiles(self, path: str):
        res = self.__get(path)
        return res.content

    @staticmethod
    def createSession(username, password):
        baseUrl = "https://cas.ecs.kyoto-u.ac.jp"
        loginPath = baseUrl + "/cas/login?service=https%3A%2F%2Fpanda.ecs.kyoto-u.ac.jp%2Fsakai-login-tool%2Fcontainer"
        getResp = rq.get(loginPath)
        html = str(PandaClient.__covertRespose(getResp).content)
        formTag = re.search(r'<form id="fm1" class="fm-v clearfix" action=".+" method="post">', html).group()
        postPath = re.sub(r'(<form id="fm1" class="fm-v clearfix" action="|" method="post">)', '', formTag)
        ltTag = re.search(r'<input type="hidden" name="lt" value="[a-z A-Z 0-9 \-]+" />', html).group()
        lt = re.sub(r'(<input type="hidden" name="lt" value="|" />)', '', ltTag)
        postResp = rq.post(baseUrl+postPath, data=urllib.parse.urlencode({
            "lt": lt,
            "password": password,
            "username": username,
            "execution": "e1s1",
            "_eventId": "submit",
            "submit": "LOGIN"
        }), headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if len(postResp.history) != 3:
            raise LoginFailedException()
        cookieLists = []
        for key, value in postResp.history[1].cookies.items():
            cookieLists.append(f"{key}={value};")
        return "".join(cookieLists)

    def fetchSites(self):
        path = "direct/site.json"
        res = self.__get(path)
        contents = json.loads(res.content)["site_collection"]
        sites = []
        for content in contents:
            sites.append(PandaSite.fromResponse(content))
        return sites

    def fetchResources(self, siteId: str):
        path = f"direct/content/site/{siteId}.json"
        res = self.__get(path)
        contents = json.loads(res.content)["content_collection"]
        files = []
        for content in contents:
            files.append(PandaFile.fromResponse(content))
        return files
    
    def fetchAssignmentsAttachments(self, siteId: str):
        path = f"direct/assignment/site/{siteId}.json"
        res = self.__get(path)
        contents = json.loads(res.content)["assignment_collection"]
        files = []
        for content in contents:
            for attachment in content["attachments"]:
                path = urllib.parse.urlsplit(attachment["url"]).path
                files.append(PandaFile(attachment["name"], "attachment/"+content["title"], path=path))
        return files


class FileHandler:

    @staticmethod
    def saveFile(directory, filename, content):
        if directory != "":
            os.makedirs(directory, exist_ok=True)
        if type(content) is str:
            with open(os.path.join(directory, filename), "w") as f:
                f.write(content)
        else:
            with open(os.path.join(directory, filename), "wb") as f:
                f.write(content)

    @staticmethod
    def readFile(directory, filename):
        with open(os.path.join(directory, filename)) as f:
            return f.read()

    @staticmethod
    def splitPath(filepath: str):
         return (os.path.dirname(filepath), os.path.basename(filepath))


class CommandHandler:

    @staticmethod
    def list(args, cookies):
        pc = PandaClient(cookies)

        sites = pc.fetchSites()
        for site in sites:
            if args.site_type != None and args.site_type != site.sitetype:
                break
            if args.only_site_id:
                print(f"{site.siteId}")
            else:
                print(f"{site.siteId}: {site.name}")

    @staticmethod
    def downloadResources(args, cookies):
        pc = PandaClient(cookies)

        files = pc.fetchResources(args.site_id)
        for f in files:
            binary = pc.downloadFiles(f.path)
            FileHandler.saveFile(os.path.join(args.directory, f.directory), f.filename, binary)

    @staticmethod
    def downloadAttachments(args, cookies):
        pc = PandaClient(cookies)

        files = pc.fetchAssignmentsAttachments(args.site_id)
        for f in files:
            binary = pc.downloadFiles(f.path)
            FileHandler.saveFile(os.path.join(args.directory, f.directory), f.filename, binary)

    @staticmethod
    def createSession(args, cookies):
        cookies = PandaClient.createSession(args.username, args.password if args.password != None else getpass.getpass())
        if args.output == None:
            print(cookies)
        else:
            directory, filename = FileHandler.splitPath(args.output)
            FileHandler.saveFile(directory, filename, cookies)  

if __name__ == "__main__":

    psr = argparse.ArgumentParser(description="cli tools for panda")
    subpsrs = psr.add_subparsers()

    psr_session = subpsrs.add_parser("login", help="see login -h")
    psr_session.add_argument("-u", "--username", required=True, help="ecs-id")
    psr_session.add_argument("-p", "--password", help="if not selected, show prompt.")
    psr_session.add_argument("-o", "--output", nargs="?", const="cookie", help="cookie output file. if blank, 'coookie'")
    psr_session.set_defaults(handler=CommandHandler.createSession)
    
    psr_sites = subpsrs.add_parser("sites", help="see sites -h")
    psr_sites.set_defaults(handler=CommandHandler.list)
    psr_sites.add_argument("-c", "--cookies", default="cookie", metavar="COOKIE_FILE", help="select cookies file")
    psr_sites.add_argument("--site-type", help="course, project, portfolio etc ")
    psr_sites.add_argument("--only-site-id", action='store_true')

    psr_resources = subpsrs.add_parser("resources-dl", help="see resources-dl -h")
    psr_resources.set_defaults(handler=CommandHandler.downloadResources)
    psr_resources.add_argument("-c", "--cookies", default="cookie", metavar="COOKIE_FILE", help="select cookies file")
    psr_resources.add_argument("-s", "--site-id", required=True, help="select site id")
    psr_resources.add_argument("-d", "--directory", default="content/", help="select site id")

    psr_attachments = subpsrs.add_parser("assignments-dl", help="see assignments-dl -h")
    psr_attachments.set_defaults(handler=CommandHandler.downloadAttachments)
    psr_attachments.add_argument("-c", "--cookies", default="cookie", metavar="COOKIE_FILE", help="select cookies file")
    psr_attachments.add_argument("-s", "--site-id", required=True, help="select site id")
    psr_attachments.add_argument("-d", "--directory", default="content/", help="select site id")

    args = psr.parse_args()

    if hasattr(args, 'handler'):
        if hasattr(args, "cookies"):
            cookieDir, cookieFile = FileHandler.splitPath(args.cookies)
            cookie = FileHandler.readFile(cookieDir, cookieFile)
            args.handler(args, cookie)
        else:
            args.handler(args, None)
    else:
        psr.print_help()
