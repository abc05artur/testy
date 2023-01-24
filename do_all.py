import os
import shutil

from git import Repo


# python do_all.py

def f1(data):
    i = 0
    for l in data:
        if l.startswith("__version__"):
            vf = l.split("=")[1].strip().strip('"').split(".")
            v = int(vf[2]) + 1
            vf[2] = str(v)
            vf = ".".join(vf)
            return i, vf
        i += 1
    raise Exception()


def list_all_files(path):
    if os.path.isfile(path):
        return [path]

    ans = list()
    for p2 in os.listdir(path):
        ans.extend(list_all_files(os.path.join(path, p2)))
    return ans


def commit(repo, message, folders_to_commit):
    for p in folders_to_commit:
        for f in list_all_files(p):
            repo.index.add(f)
    Repo().index.commit(message)


if __name__ == "__main__":
    print("main")

    #   remove dist
    dirpath = os.path.join('dist')
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)

    # upgrade_version

    filename = os.path.join("testy_quick", "__init__.py")
    with open(filename, "r") as f:
        data = f.readlines()
    i, v = f1(data)
    data[i] = f'__version__ = "{v}"\n'
    with open(filename, "w") as f:
        f.writelines(data)

    # commit
    repo = Repo()
    commit(repo, "c " + str(v),
           ["docs", "tests", "testy_quick", 'do_all.py', 'LICENSE', 'README.md', 'requirements.txt', 'setup.cfg',
            'setup.py'])

    # build
    from setuptools import setup

    setup(script_args=["sdist", "bdist_wheel"])

    # deploy
    from twine.cli import dispatch

    dispatch(["upload", "dist/*", "-u", os.getenv('pip_id'), "-p", os.getenv('pip_password')])
