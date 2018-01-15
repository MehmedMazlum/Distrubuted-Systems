#!/usr/bin/env python3
import sys
import re

# pattern aciklamasi
# basta istenilen kadar bosluk olabilir
# sonra en az bir rakamli sayi gelecek
# "en az bir tane bosluk ve en az iki harfli kelimeler" grubundan istenilen
# sayida olabilir
# "en az bir tane bosluk ve en az iki harfli kelimeler" grubundan bir tane
# olacak
# en az bir tane bosluk olup, en az 1 en cok 3 rakamli bir sayi olacak
# en sonda istenilen sayida bosluk olabilir

pattern = r'\s*([0-9]+)' \
          r'((\s+[a-zA-Z]{2,})+)' \
          r'\s+([a-zA-Z]{2,}){1}' \
          r'\s+([0-9]{1,3})\s*$'

# argv'yi duzgunce alma bolgesi
if len(sys.argv) > 1 and sys.argv[1].isnumeric():
    N = int(sys.argv[1])
else:
    print("Usage:\n\t %s <number of entries>" % (sys.argv[0]) )
    sys.exit()

if N == 0: # None, False, 0
    print("Please enter a valid number of entries.")
    sys.exit()

fihrist = {} # dict()

# kullanicidan alinan verilerin okunmasi ve duzenlenmesi
for count in range(N):
    line = input("Numara, isim, soyisim, yas: ")
    searchObj = re.search(pattern, line)

    if not searchObj:
        print("Invalid format!")
        continue

    no = int(searchObj.group(1))
    ad = searchObj.group(2).strip()
    soyad = searchObj.group(searchObj.lastindex - 1).strip()
    yas = int(searchObj.group(searchObj.lastindex))

    if no in fihrist.keys():
        print("Entry exists: %s" % (no))
    else:
        fihrist[no] = (ad, soyad, yas)

# ekrana basilmasi
for key in sorted(fihrist.keys()):
    print("Numara: %s, Ogrenci: %s %s, Yas: %s" % (
        key,
        fihrist[key][0],
        fihrist[key][1],
        fihrist[key][2]
    ) )

