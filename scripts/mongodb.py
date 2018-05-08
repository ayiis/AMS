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

    if not fab_exists("/opt/%s" % ("mongodb-3.4.3") ):

        run("tar xf %s" % ("mongodb-linux-x86_64-rhel62-3.4.3.tgz") )
        run("/bin/mv -f %s %s" % ("mongodb-linux-x86_64-rhel62-3.4.3", "mongodb-3.4.3") )
        with cd("mongodb-3.4.3"):
            run("mkdir %s %s %s %s %s %s" % ("data", "log", "scripts", "backup", "conf", "keys") )
            run("openssl rand -base64 741 >%s" % ("keys/replkey") )
            run("chmod 400 %s" % ("keys/replkey") )

        run("/bin/cp -f %s %s" % ("mongodb.conf", "mongodb-3.4.3/conf/") )

        run("groupadd mongodb")
        run("useradd -r -g mongodb -s /bin/false mongodb")
        run("chown -R mongodb.mongodb %s" % ("mongodb-3.4.3") )

        run("echo \"never\" > /sys/kernel/mm/transparent_hugepage/enabled")
        run("echo \"never\" > /sys/kernel/mm/transparent_hugepage/defrag")
        run("sysctl vm.swappiness=1")

        run("/bin/mv -f %s /opt/%s" % ("mongodb-3.4.3", "mongodb-3.4.3") )

        run("/bin/cp -f mongodb /etc/init.d/")
        run("chmod +x /etc/init.d/mongodb")
        run("chkconfig mongodb --add")
        run("chkconfig mongodb on")
        run("service mongodb start")

        print '''
        ############ 配置服务并且启动
        ## > bin/mongo

        use admin
        db.createUser({user:"sysdba", pwd:"g/fHthsi83d3*d+9dg", roles:[{role:"root", db:"admin"}]})
        db.auth("sysdba", "g/fHthsi83d3*d+9dg")
        show dbs

        ############ 配置身份验证并且重启mongodb
        ## ..mongodb.conf:  authorization: enabled

        ## > service mongodb stop && service mongodb start
        '''

    else:
        print "%s had been built" % "mongodb-3.4.3"
