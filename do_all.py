import os
import shutil
#remove dist
dirpath = os.path.join('dist')
if os.path.exists(dirpath) and os.path.isdir(dirpath):
    shutil.rmtree(dirpath)

#upgrade_version
def f1(data):
    i=0
    for l in data:
        if l.startswith("__version__"):
            vf=l.split("=")[1].strip().strip('"').split(".")
            v=int(vf[2])+1
            vf[2]=str(v)
            vf=".".join(vf)
            return i,vf
        i+=1
    raise Exception()
filename=os.path.join("testy_quick","__init__.py")
with open(filename,"r") as f:
    data=f.readlines()
i,v=f1(data)
data[i]=f'__version__ = "{v}"\n'
with open(filename,"w") as f:
    f.writelines(data)

#build
from setuptools import setup
setup(script_args=["sdist","bdist_wheel"])

#deploy
from twine.cli import dispatch
dispatch(["upload","dist/*","-u",os.getenv('pip_id'),"-p",os.getenv('pip_password')])

