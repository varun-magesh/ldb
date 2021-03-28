import os

def ldbdir(path=os.getcwd()):
    cpath = os.getcwd()
    dpath = os.path.dirname(cpath)
    while dpath != cpath: # while not root dir
        if ".ldb" in os.listdir(cpath):
            return cpath
        cpath, dpath = dpath, os.path.dirname(dpath)
    return None

def ldbopen(path):
    """
    Opens a particular work in Zathura and the corresponding notes in st+vim
    """
    from glob import glob
    print(path)
    if not ldbdir(path):
        raise ValueError("Path is not in an ldb instance!")
    try:
        notefile = glob(f"{path}/*.md")[0]
        pdffile = glob(f"{path}/*.pdf")[0]
    except IndexError:
        raise ValueError("PDF and Note files not found!")
    if os.fork():
        os.system(f"zathura {pdffile}")
        return
    if os.fork():
        os.system(f"st vim {notefile}")
        return
