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


def assert_available(setting):
    pass


def setup(setting):
    print "in python setup: %s" % setting

    assert_available(setting)

    if not run("python --version") == "Python 2.7.11":

        old_python_path = run("echo `head -n1 /usr/bin/yum`|readlink -f `cut -c3-`")
        if run("%s --version" % (old_python_path) ) == "Python 2.6.6" : old_python_path = "/usr/bin/python2.6"

        run("tar xf %s" % ( "Python-2.7.11.tgz" ) )
        with cd("Python-2.7.11"):
            run("./configure >> fabric.log")
            run("make -j %s >> fabric.log && make install >> fabric.log" % (setting["_cpu_count"]) )
            run("ln -sf /usr/local/bin/python /usr/bin/python")

        for old_require_file in ("/usr/bin/yum", "/usr/libexec/urlgrabber-ext-down", "/usr/sbin/yum-complete-transaction"):
            if fab_exists(old_require_file):
                run("sed -i \"1c #!%s\" %s" % (old_python_path, old_require_file) )

        run("python get-pip.py >> fabric.log")
        run("ln -sf /usr/local/bin/pip /usr/bin/pip")
        if not fab_exists("~/.pip/"): run("/bin/mkdir -p %s" % ( "~/.pip/" ) )
        run("/bin/cp -f pip.conf ~/.pip/")

        # use proxy to install pip modules if proxy exists
        if setting.get("all_proxy"):
            with("export all_proxy=\"%s\"" % (setting["all_proxy"]) ):
                run("pip install supervisor virtualenv >> fabric.log")
        else:
            run("pip install supervisor virtualenv >> fabric.log")

        if not fab_exists("/etc/supervisor/supervisord.conf"):
            run("mkdir -p /etc/supervisor/conf")
            run("/bin/cp -f supervisord.conf /etc/supervisor/")
            run("/bin/cp -f start /etc/supervisor/")
            run("chown -R %s /etc/supervisor" % (setting["deployer_name"]) )
            sudo("/usr/local/bin/supervisord -c /etc/supervisor/supervisord.conf", user=setting["deployer_name"])

        if not fab_exists("/home/%s/python_project/logs" % (setting["deployer_name"])):
            sudo("mkdir -p /home/%s/python_project/logs" % (setting["deployer_name"]), user=setting["deployer_name"])

    else:
        print "%s had been built" % "Python-2.7.11"
