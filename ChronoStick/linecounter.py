# for Python 3; originally in Python 2
#This will get the line count (not number of operations) of all the *.end files, where end is given by user.

import os
extension = input("Gimme extension: ")
total = 0

cwd = os.getcwd()
for root, dirs, files in os.walk(cwd):
##    print(root, dirs, files, sep="\n")
    for name in files:
        if name.endswith("." + extension):
            num = len(list(filter(lambda x:not (x.isspace() or x.strip().startswith("//")),(open(root+"\\"+name,"r").read().strip().split("\n"))))) # sorry about the filter
            a = root[len(cwd):]+"\\"+name
            print(a + " "*(max(0,75-len(a))),num)
            total += num
print(total,"lines in total.")
