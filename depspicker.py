#depspicker.py
#changes from Windows to Linux version commented

logFile = r".\\logFile.CSV" #Linux: ./logFile
basePath = r".\\foo\\" #base of the file-tree to be copied (where the needed dependencies originally reside)
destPath = r".\\foo\\" #destination of copy


import csv, shutil
from pathlib import Path

logF = Path(logFile)
basePath = Path(basePath).resolve()
destPath = Path(destPath).resolve()

with open(logF, newline='', encoding="utf-8") as log:
    checked = set()
    reader = csv.DictReader(log) # Linux: -
    for row in reader: #Linux: for row in log:
        try:
            src = Path(row["Path"]) # Linux: src = Path(row.split('"')[1])
            src = src.resolve()
            if src in checked or not (src.is_file() and\
                basePath.parts == src.parts[:len(basePath.parts)]):
                continue
        except (OSError, IndexError): #not a file
            continue
        finally:
            checked.add(src)
    dst = destPath / src.relative_to(basePath)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst.parent)