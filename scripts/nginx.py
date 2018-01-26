#!/usr/local/bin/python
#encoding:utf8
import sys, os, datetime, time, pty, pprint, shutil, re
sys.path.insert(0, "..")

from fabric.api import (
    run, env, prompt, put, cd
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
    print "in nginx setup: %s" % setting

    assert_available(setting)

    # build luajit if luajit do not exists
    if not fab_exists("/usr/local/bin/%s" % ("luajit-2.0.4") ):
        if fab_exists("LuaJIT-2.0.4"): run("rm %s -rf" % ("LuaJIT-2.0.4") )

        run("tar xf %s" % ( "LuaJIT-2.0.4.tar.gz" ) )
        with cd("LuaJIT-2.0.4"):
            run("make -j %s >> fabric.log && make install >> fabric.log" % (setting["_cpu_count"]) )
    else:
        print "%s had been built" % "luajit-2.0.4"

    if not fab_exists("/opt/dependence"): run("/bin/mkdir -p %s" % ( "/opt/dependence" ) )

    if not fab_exists("/opt/dependence/%s" % ("lua-nginx-module-0.10.2") ):
        run("tar xf %s" % ("lua-nginx-module-0.10.2.tar.gz") )
        run("/bin/mv -f %s /opt/dependence" % ("lua-nginx-module-0.10.2") )

    if not fab_exists("/opt/dependence/%s" % ("ngx_devel_kit-0.2.19") ):
        run("tar xf %s" % ("ngx_devel_kit-0.2.19.tar.gz") )
        run("/bin/mv -f %s /opt/dependence" % ("ngx_devel_kit-0.2.19") )

    # build nginx if nginx do not exists
    if not fab_exists("/opt/%s/conf" % ("nginx-1.10.0") ):
        if fab_exists("nginx-1.10.0"): run("rm %s -rf" % ("nginx-1.10.0") )

        run("tar xf %s" % ("nginx-1.10.0.tar.gz") )
        with cd("nginx-1.10.0"), prefix("export LUAJIT_LIB=/usr/local/lib"), prefix("export LUAJIT_INC=/usr/local/include/luajit-2.0"):
            run(" ".join([
                "./configure --prefix=%s" % ("/opt/nginx-1.10.0"),
                "--with-ld-opt=\"-Wl,-rpath,/usr/local/lib\"",
                "--with-http_stub_status_module",
                "--with-http_ssl_module",
                "--add-module=/opt/dependence/%s" % ("ngx_devel_kit-0.2.19"),
                "--add-module=/opt/dependence/%s" % ("lua-nginx-module-0.10.2"),
                ">> fabric.log",
            ]) )
            run("make -j %s >> fabric.log && make install >> fabric.log" % (setting["_cpu_count"]) )
            run("chmod 733 /opt/%s/logs" % ("nginx-1.10.0") )

        run("/bin/cp -f nginx.conf /opt/%s/conf" % ("nginx-1.10.0") )
        run("/bin/cp -f nginx /etc/init.d/")
        run("chmod +x /etc/init.d/nginx")

        run("chkconfig nginx --add")
        run("chkconfig nginx on")

        run("service nginx start")
        run("service nginx status")
    else:
        print "%s had been built" % "nginx-1.10.0"
