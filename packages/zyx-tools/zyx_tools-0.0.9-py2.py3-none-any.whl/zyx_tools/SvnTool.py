import sys
import os
from typing import List
import re
from urllib.parse import urljoin
from .OtherTool import run_cmd
from pydantic import BaseModel
from xml.etree import ElementTree
from datetime import datetime
import logging


# 更新
def update_svn(path):
    print("update ", path)
    cmd = f"svn update {path} --non-interactive --accept theirs-full "
    ret = os.system(cmd)

    print("resolve confilict ", path)
    cmd = (
        f"svn resolve {path} --depth infinity --accept theirs-full  --non-interactive "
    )
    ret = os.system(cmd)
    if ret != 0:
        raise Exception("update Error!:" + path)


def commit_svn(path):
    commit_svn_comment(path, "auto commmit")


def revert_svn(path):
    command = f"""svn revert -R {path} """
    ret = os.system(command)
    print(command)
    if ret != 0:
        raise Exception("revert Error!:" + path)
        return
    else:
        print("revert ok!")


def commit_svn_comment(path, comment):
    command = f"""svn ci {path} -m "{comment}" -q """
    ret = os.system(command)
    print(command)
    if ret != 0:
        raise Exception("commit Error!:" + path)
        return
    else:
        print("commit ok!")


def resolveConflict(path):
    cmd = "svn status " + path
    ret = os.popen(cmd)
    text = ret.read()
    ret.close()
    for linetext in text.splitlines():
        wordlist = re.split(r"\s+", linetext)
        print(wordlist)
        if len(wordlist) >= 2 and wordlist[0] == "C":
            filepath = os.path.join(path, wordlist[1])
            cmd = "svn resolve " + filepath + "--accept theirs-full  --non-interactive "
            ret = os.system(cmd)
            print("resolve confilict ok ", path)


def add_svn(path):
    cur_path = os.getcwd()
    # 当前文件目录
    os.chdir(path)
    command = """svn status|grep ? |awk '{print($2}'|xargs svn add"""
    ret = os.system(command)
    print(command)
    if ret != 0:
        raise Exception("add svn Error!:" + path)
    else:
        print("add ok!")
    os.chdir(cur_path)


def add_svn_force(path):
    command = f"""svn add {path} --force """
    ret = os.system(command)
    print(command)
    if ret != 0:
        raise Exception("add force Error!:" + path)
    else:
        print("add ok!")


def get_svn_externals(url, username=None, passwd=None) -> List[str]:
    res: List[str] = []
    auth = ""
    if username and passwd:
        auth = f"--username {username} --password {passwd}"
    cmd = f"svn {auth} propget svn:externals -R {url} "
    logging.info(f"get_svn_externals cmd:{cmd}")
    lines = run_cmd(cmd, "gbk").splitlines()
    prefix = ""
    for line in lines:
        if len(line) == 0:
            continue
        idx = line.find(" - ")
        if idx > 0:
            prefix = line[0:idx].strip()
            if prefix.endswith("/") is False:
                prefix += "/"
            line = line[idx + 3 :].strip()
        info_arr = line.split(" ")
        path2_url = info_arr[0].strip()
        if path2_url.startswith("^"):
            head_str = path2_url.split("/")[1]
            head_idx = prefix.find(f"/{head_str}/")
            new_prefix = prefix[0 : head_idx + 1]
            path2_url = urljoin(new_prefix, path2_url[1:])
        elif path2_url.startswith("svn:") is False:
            path2_url = urljoin(prefix, path2_url)
        # print(f"res:{path2_url} url:{info_arr[0].strip()} pre:{prefix}")
        res.append(path2_url)
    return res


class SvnLogInfo(BaseModel):
    author: str = ""
    date: datetime = None
    msg: str = ""
    revision: str = ""


def get_svn_log(
    url: str, start_date: str, end_date: str, search=None, username=None, passwd=None
) -> List[SvnLogInfo]:
    res: List[SvnLogInfo] = []
    auth = ""
    search_txt = ""
    if username and passwd:
        auth = f"--username {username} --password {passwd}"
    if search:
        search_txt = f" --search {search}"
    date_str = "-r " + "{" + start_date + "}" + ":" + "{" + end_date + "}"
    cmd = f"svn {auth} log --xml {search_txt} {date_str} {url}"
    logging.info(f"get_svn_log cmd:{cmd}")
    output = run_cmd(cmd)
    if len(output.strip()) <= 0:
        return res
    root = ElementTree.fromstring(output)
    for elem in root.findall("logentry"):
        info = SvnLogInfo()
        info.msg = elem.find("msg").text
        info.date = datetime.strptime(elem.find("date").text, "%Y-%m-%dT%H:%M:%S.%fZ")
        info.author = elem.find("author").text
        info.revision = elem.get("revision")
        res.append(info)
    return res


def get_svn_ls(url, username=None, password=None) -> List[str]:
    res: List[str] = []
    auth = ""
    if username and password:
        auth = f"--username {username} --password {password}"
    cmd = f"svn {auth} ls {url}"
    logging.info(f"get svnls cmd:{cmd}")
    output = run_cmd(cmd)
    output = output.strip()
    if len(output) == 0:
        return res
    res = output.splitlines()
    return res
