'''
Created on 03-Mar-2020

@author: srinivasan
'''
import os
from pathlib import Path
"""
List the Directory with Full path
"""


def listdir_fullpath(d):
    return [(os.path.join(dp, f),
             os.path.join(dp, f).replace(os.path.dirname(d) + "/", "")) 
             for dp, _, filenames in os.walk(d)
             for f in filenames]

"""
check and create Directory
"""


def createDirIfNotExist(pathfile):
    Path(pathfile).parent.mkdir(parents=True,
                             exist_ok=True)
    return pathfile
