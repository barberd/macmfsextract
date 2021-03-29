#!/usr/bin/env python3

#Created by Don Barber, don@dgb3.net
#Pass the raw disk image on the command line as argument 1
#add verbose as argument 2 if you want some extra details

#MFS implementation details from https://www.macgui.com/news/article.php?t=482

#If the image is a diskcopy 4.2 image, extract the raw MFS image first via:
# dd if=INPUTFILE of=OUTPUTFILE bs=84 skip=1

#Idea for improvement: extract files as macbinary format instead of
#individual data and resource forks

import sys
import os
import math

filename=sys.argv[1]

file_size = os.path.getsize(filename)
fh=open(filename,"rb")

fh.seek(1026)

drCrDate = int.from_bytes(fh.read(4),'big')
drLsBkUp = int.from_bytes(fh.read(4),'big')
drAtrb=int.from_bytes(fh.read(2),'big')
drNmFls=int.from_bytes(fh.read(2),'big')
drDirSt=int.from_bytes(fh.read(2),'big')
drBlLen=int.from_bytes(fh.read(2),'big')
drNmAlBlks=int.from_bytes(fh.read(2),'big')
drAlBlkSiz=int.from_bytes(fh.read(4),'big')
drClpSiz=int.from_bytes(fh.read(4),'big')
drAlBlSt=int.from_bytes(fh.read(2),'big')
drNxtFNum=int.from_bytes(fh.read(4),'big')
drFreeBks=int.from_bytes(fh.read(2),'big')
drVNl=int.from_bytes(fh.read(1),'big')
drVN=fh.read(drVNl)
print("Volume Name:",drVN)
if 'verbose' in sys.argv:
    print("Volume Create Datestamp:",drCrDate)
    print("Volume Modify Datestamp:",drLsBkUp)

maplocation=0x440

def getmapentry(blocknum):
    location=((blocknum-2)*12/8)
    if location==math.ceil(location):
        fh.seek(maplocation+int(location))
        entry=(int.from_bytes(fh.read(2),'big') >> 4)
    else:
        fh.seek(maplocation+math.floor(location))
        entry=(int.from_bytes(fh.read(2),'big') & 0xFFF )
    return entry

def getfilecontents(block,length):
    blocklist=[block]
    while True:
        block=getmapentry(block)
        #print(block)
        if block==1:
            break
        blocklist.append(block)
        if block==0:
            raise Exception("Unused Block")
    if 'verbose' in sys.argv:
        print("Blocklist:",blocklist)
    contents=b''
    for block in blocklist:
        if 'verbose' in sys.argv:
            print("Seeking to:",hex(drAlBlSt*512+(block-2)*drAlBlkSiz),"for block",block)
        fh.seek(drAlBlSt*512+(block-2)*drAlBlkSiz)
        data=fh.read(drAlBlkSiz)
        contents+=data
    return contents[:length]

fh.seek(drDirSt*512)
i=0
while True:
    flFlgs=fh.read(1)
    if flFlgs==b'\x00':
        fh.read(50)
        i+=50
    else:
        flType=int.from_bytes(fh.read(1),'big')
        flUsrWds=fh.read(16)
        flFlNum=int.from_bytes(fh.read(4),'big')
        flStBlk=int.from_bytes(fh.read(2),'big')
        flLgLen=int.from_bytes(fh.read(4),'big')
        flPyLen=int.from_bytes(fh.read(4),'big')
        flRStBlk=int.from_bytes(fh.read(2),'big')
        flRLgLen=int.from_bytes(fh.read(4),'big')
        flRPyLen=int.from_bytes(fh.read(4),'big')
        flCrDat=int.from_bytes(fh.read(4),'big')
        flMdDat=int.from_bytes(fh.read(4),'big')
        flNaml=int.from_bytes(fh.read(1),'big')
        flNam=fh.read(flNaml)
        i+=51+flNaml
        if flFlNum!=0:
            print(hex(fh.tell()),flFlNum,flNaml,flNam)
            if 'verbose' in sys.argv:
                print("Create Datestamp:",flCrDat)
                print("Modify Datestamp:",flMdDat)
            location=fh.tell()
            oh=open(flNam+b".info","wb")
            oh.write(flUsrWds)
            oh.close()

            if(flStBlk==0 and flRStBlk==0):
                print("Error:",flNam,"has neither data nor resource fork")
            if flStBlk!=0:
                content=getfilecontents(flStBlk,flLgLen)
                oh=open(flNam+b".data","wb")
                oh.write(content)
                oh.close()
            if flRStBlk!=0:
                content=getfilecontents(flRStBlk,flRLgLen)
                oh=open(flNam+b".rsrc","wb")
                oh.write(content)
                oh.close()
            fh.seek(location)
    if (fh.tell()%2==1):
        fh.read(1)
        i+=1
    if i>512:
        fh.seek(math.floor(fh.tell()/512)*512)
        i=0
    if fh.tell()>=((drDirSt+drBlLen-1)*512):
        break

fh.close()


