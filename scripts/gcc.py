#!/usr/local/bin/python
#encoding:utf8
import sys, os, datetime, time, pty, pprint, shutil, re
sys.path.insert(0, "..")

from fabric.api import(
    run, env, prompt, put, cd
)
from fabric.contrib.files import (
    exists as fab_exists,
    append as fab_append,
)
from fabric.context_managers import (
    prefix
)

def setup(setting):
    pass
