import requests
import time
import csv
from datetime import timedelta
import os
import re
import pylatex
import sys
import subprocess

class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        pass    


if __name__ == "__main__":
    # Paths
    cwdpath = os.getcwd()
    logpath = os.path.join(cwdpath, "logs")
    buildpath = os.path.join(cwdpath, "build")

    if not os.path.exists(logpath):
        os.makedirs(logpath)

    if not os.path.exists(buildpath):
        os.makedirs(buildpath)
    
    sys.stdout = Logger(os.path.join(logpath, "vinyl.log"))

    # Main entry
    ans = "n"
    if os.path.exists(os.path.join(logpath, "collectiondb.csv")):
        print("'collectiondb.csv' was found. Do you want continue with it? [y/n] ")
        ans = input()

    # Start from local file ...
    if ans == "y":
        with open(os.path.join(logpath, "collectiondb.csv"), newline = "") as io:
            reader = csv.DictReader(io, delimiter = ";")
            data = []

            for row in reader:
                data.append(row)

        print("Imported.")
    
    # ... or from online source
    else:
        api = "https://api.discogs.com"
        user = "L-Nafaryus"
        url = "{}/users/{}/collection/folders/0/releases?per_page=300&sort=artist".format(api, user)
        res = requests.get(url)
        print("[status {}] {}".format(res.status_code, url))

        if res.status_code == 200:
            ratelimit = res.headers["X-Discogs-Ratelimit"]
            collection = res.json()
            data = []

            for c in collection["releases"]:
                base = c["basic_information"]

                data.append({
                    "artist" : base["artists"][0]["name"],
                    "master_id" : base["master_id"],
                    "title" : base["title"],
                    "year": base["year"] if float(base["master_id"]) == 0 else ""
                })
            
            delay = 60.0 / float(ratelimit)
            n = 0
            print("Collection size: {}".format(len(data)))
            print("Estimated time: {} s".format(timedelta(seconds=(len(data) * delay))))

            for d in data:
                url = "{}/masters/{}".format(api, d["master_id"])
                time.sleep(delay)
                res = requests.get(url)
                n = n + 1
                print("[status {}] {}".format(res.status_code, url))

                if res.status_code == 200:
                    master = res.json()
                    d["year"] = master["year"] 
                
                print("({}/{}) {}".format(n, len(data), d))
        
        try:
            with open(os.path.join(logpath, "collectiondb.csv"), mode="w", encoding="utf8", newline="") as io:
                header = data[0].keys()

                dwr = csv.DictWriter(io, delimiter = ";", fieldnames = header)
                dwr.writeheader()
                dwr.writerows(data)
            
            print("Exported to logs/collectiondb.csv")

        except IOError as io:
            print(io)
    
    # Sort
    data = sorted(data, key = lambda item: "{} {} {}".format(item["artist"], item["year"], item["title"]))

    for d in data:
        m = re.search(r"\s+\(.\)", d["artist"])

        if type(m) != type(None):
            d["artist"] = d["artist"].replace(m.group(0), "")
        
        m = re.search(r"\s+=(\W+\w+)*\s*$", d["title"])

        if type(m) != type(None):
            d["title"] = d["title"].replace(m.group(0), "")

        #d["artist"] = d["artist"].replace("&", "\\&")
        #d["title"] = d["title"].replace("&", "\\&")
    
    # Tex processing
    geometry = {
        "left": "2cm",
        "right": "2cm",
        "top": "0.5cm",
        "bottom": "1.5cm"
    }
    doc = pylatex.Document(page_numbers = True, geometry_options = geometry)

    header = pylatex.PageStyle("header")
    
    with header.create(pylatex.Foot("L")):
        header.append("Link: https://www.discogs.com/user/{}/collection".format("L-Nafaryus"))
    
    with header.create(pylatex.Foot("R")):
        header.append(pylatex.simple_page_number())
    
    doc.preamble.append(header)
    doc.change_document_style("header")

    with doc.create(pylatex.LongTable("l l l l")) as table:
        table.add_hline()
        table.add_row(["ID", "Artist", "Year", "Title"])
        table.add_hline()
        table.end_table_header()

        table.add_hline()
        table.end_table_footer()

        table.add_hline()
        table.end_table_last_footer()
        
        buf = data[0]["artist"]
        for n in range(len(data)):
            if buf != data[n]["artist"]:
                table.add_hline()

            table.add_row([str(n + 1), data[n]["artist"], data[n]["year"], data[n]["title"]])
            buf = data[n]["artist"]

    doc.generate_tex(os.path.join(buildpath, "collection"))
    
    # Fix encoding package
    with open(os.path.join(buildpath, "collection.tex"), "r") as io:
        filedata = io.read()

    filedata = filedata.replace("usepackage[T1]", "usepackage[T2A]")

    with open(os.path.join(buildpath, "collection.tex"), "w") as io:
        io.write(filedata)
    
    # Generate pdf
    print("Do you want to generate pdf? [y/n] ")
    ans = input()

    if ans == "y":
        subprocess.run(["latexmk", "-pdf", os.path.join(buildpath, "collection.tex"), "-outdir={}".format(buildpath)])


    print("Done.")

