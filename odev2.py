#!/usr/bin/env python3.4
import re
from difflib 
import SequenceMatcher


pattern = "([0-9\s]*)\s---\s(.*)$"


def parser(fileName):
    
ret = {}
    with open(fileName,'r') as f:
        for line in f:
           
 searchObj = re.match(pattern,line)
           
 if searchObj:
               
 ret[searchObj.group(2)] = searchObj.group(1)
    
return ret

def save_fihrist(fihrist, fileName):
   
 temp = []
    for key in fihrist.keys():
       
 temp.append((fihrist[key], key))
    
temp = sorted(temp)
   
 with open(fileName, 'w+') as f:
        
for element in temp:
           
 f.write("%s, %s\n" % (element[0], element[1]))

def main():
   
 fihrist = parser("codes.txt")
    save_fihrist(fihrist, "codes.csv")

  
  # ask for country
    while True:
       
 ask = input("Country Name: ")
    
    if ask in fihrist.keys():
          
  print("Code for %s is %s" % (ask, fihrist[ask]))
       
 else:
            print("Country not found.")
          
  similarity = lambda x: SequenceMatcher(None, ask, x).ratio()
         
   m = sorted(fihrist.keys(), key= similarity)
          
  m.reverse()
          
  print("Did you mean: %s or %s or %s" % (m[0], m[1], m[2]))


if __name__ == '__main__':
    main()
