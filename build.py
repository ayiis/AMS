#!/usr/local/bin/python
#encoding:utf8
import sys, os, datetime, time, pty, pprint, shutil, re
sys.path.insert(0, "..")

from fabric.api import (
    run, env, prompt, put, cd, sudo, settings
)
from fabric.contrib.files import (
    exists as fab_exists,
    append as fab_append,
)
from fabric.context_managers import (
    prefix
)

from scripts import (
    gcc, python, nodejs, nginx
)

BUILD_SETTING = [{
    "remote_user": "root",
    "remote_ip": "192.168.32.233",
    "remote_port": "40901",
    "remote_path": "/opt/build",
    "deployer_name": "deployer",
    # "all_proxy": "http://172.18.36.166:23339",
    "OBJ": ["python", "nginx"], # "gcc", "python", "nodejs", "nginx" # U can skips any, but do not change the order
}]


if __name__ == "__main__":
    os.system("fab -f %s build_main" % (__file__))

    exit(0) # stupid


def init_setting(func):
    env.hosts = [ "%s@%s:%s" % (setting["remote_user"], setting["remote_ip"], setting["remote_port"]) for setting in BUILD_SETTING]

    def do():
        func(setting)

    return do


def build_yum_base(setting):
    run("yum-complete-transaction -y >> fabric.log")
    run("yum install -y tcl zlib-devel openssl-devel sqlite tk-devel texinfo >> fabric.log")
    run("yum groupinstall -y \"Development tools\" >> fabric.log")
    run("yum install -y pcre-devel libstdc++-devel.i686 bzip2-devel glibc-devel.i686 >> fabric.log")
    run("yum install -y gcc* >> fabric.log")


@init_setting
def build_main(setting):

    # setup root-directory for building
    run("/bin/mkdir -p %s" % ( setting["remote_path"] ) )
    with cd(setting["remote_path"]):

        # yum build up necessary libs
        build_yum_base(setting)

        # put build package into remote server
        for item_name in setting["OBJ"]:
            put(item_name, "%s" % (setting["remote_path"]))

        # get cpu count for make file
        setting["_cpu_count"] = run("lscpu|sed -n 's/^CPU(s):[ ]*//p'")

        # create deployer
        if run("grep -c \"^%s:\" /etc/passwd" % (setting["deployer_name"]), quiet=True) == "0":
            run("adduser -g root %s" % (setting["deployer_name"]) )

        # build each package
        for item_name in setting["OBJ"]:
            with cd("%s/%s" % (setting["remote_path"], item_name)):
                if item_name == "nginx": nginx.setup(setting)
                if item_name == "python": python.setup(setting)
                if item_name == "nodejs": nodejs.setup(setting)
                if item_name == "gcc": gcc.setup(setting)

