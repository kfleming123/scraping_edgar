# Unzip a GZ file

import os
import gzip
import shutil

cwd = os.getcwd()
with gzip.open('GM-pre-debut-metrics.csv.gz', 'rb') as f_in:
    with open('GM-pre-debut-metrics.txt', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)