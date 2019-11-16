import re
import csv
import operator
import math
import argparse
from progress.bar import Bar
from progress.spinner import PixelSpinner

ap = argparse.ArgumentParser()

ap.add_argument("-f", "--filename", required=True,
   help="set file for parce")

args = vars(ap.parse_args())

# isParce = False

def parseCsv(f):
    firstline = True
    reader = csv.reader(f, delimiter=';')
    a =[]
    for row in reader:
        if firstline: 
            firstline = False
            continue
        a.append(row[:])
    # global isParce
    # isParce = True
    return a

def findLines(content):
    RL = []
    for i in content[:-1]:
            if 'TCP' in i[1]:
                if len(i) >= 6 and ('FIN sent' in i[5] or 'Connection reset' in i[5]):
                    RL.append(i)
    return RL

def multiReplace(text):
    for ch in [',','(',')','\'']:
        if ch in text:
            text = text.replace(ch,'')
    return text

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])


if __name__ == "__main__":
    countBytes = "(\d+)\s(bytes)"
    fromToPair = "(from\s[^\:]+):[0-9]{2,}\s(to\s[^\:]+):[0-9]{2,}"
    dictOfSourcesAndDestinations = {}
    
    with open(args['filename']) as f:
        content = parseCsv(f)
        # spinner = PixelSpinner('Convert log file to csv: ')
        # while isParce == False:
            # spinner.next()
        resList = findLines(content)
        print("\n")
        bar = Bar('Processing', max=(len(resList)))
        for i in resList:
            nstr = " ".join(i)
            fromToPairStr = ' '.join([str(elem) for elem in (re.findall(fromToPair,nstr))])
            clearFromToPairStr = multiReplace(fromToPairStr)
            countBytesStr = re.findall(countBytes,nstr)
            if clearFromToPairStr not in dictOfSourcesAndDestinations:
                dictOfSourcesAndDestinations[clearFromToPairStr] = int(countBytesStr[1][0])
            else:
                dictOfSourcesAndDestinations[clearFromToPairStr] = (int(dictOfSourcesAndDestinations.get(clearFromToPairStr)) + int(countBytesStr[1][0]))
            bar.next()
        bar.finish()
    
    sortedDictOfSourcesAndDestinations = sorted(dictOfSourcesAndDestinations.items(), key=lambda kv: kv[1], reverse=True)

    print("\n" * 3, "*" * 60, "\n", "\t" * 3, "TOP 10", "\n", "*" * 60, "\n")
    for k, v in sortedDictOfSourcesAndDestinations[:10]: 
        print(k, ":", convert_size(v))  