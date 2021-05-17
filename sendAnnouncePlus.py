import requests
import Torrent
import socket
#import sys

#torrent = Torrent.Torrent("moby.txt.torrent")
#print(torrent.product_name)
#downloadedFile = []

def sendAnnounce(torrent,pid,downloadedFile,mode,uploaded,sock,leave):
    #amountLeft = 20
    #URL = "http://149.61.174.15:6969/announce"
    #print(torrent.info_hash.decode())

    piecesStatus = ''
    amtLeft = 0 
    amtDown = 0
    for piece in downloadedFile:
        if piece == None:
            piecesStatus += '0'
            amtLeft += 1
        else:
            piecesStatus += '1'
            amtDown += 1
    if leave == True:
        amtLeft = -1

    PARAMS = {
                'info_hash': str(torrent.info_hash),
                'peer_id': pid,
                'port': sock[1],
                'uploaded': uploaded,
                'downloaded': amtDown,
                'left': amtLeft,
                'ip':sock[0],
                #'compact': 1,
                'mode': mode,
                'piecesStatus': piecesStatus
                #'leave': leave
                }

    r = requests.get(url=torrent.announce,params=PARAMS)
    
    # if r.text[0:5] == 'ERROR':
    #     print(r.text)
    # return []
    
    temp = r.text[:-1]
    temp2 = temp.split(',')
    temp3 = []
    for ele in temp2:
        temp3.append(ele.split(':'))
    return (temp3)

    #print (r)
    #print (r.text)
    #print (r.url)
    #print (r.status_code)
