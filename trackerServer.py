from aiohttp import web
import Torrent
import urllib.parse
import math
import random
import argparse
import socket

#Torrent file arg
parser = argparse.ArgumentParser()
parser.add_argument('--t')
args = parser.parse_args()
torrent = Torrent.Torrent(args.t)

routes = web.RouteTableDef()

seeders = dict()
leechers = dict()
seedersKeys=[]
leechersKeys=[]

@routes.get('/announce')
async def tracker(request):
    #print(request.url)
    questionSplit = str(request.url).split('?')
    requestParams = questionSplit[1]
    splitParams = requestParams.split('&')
    print(splitParams)
    clientDict = dict()
    for ele in splitParams:
        eleSplit = ele.split('=')
        clientDict[eleSplit[0]] = eleSplit[1]

    # for some reason the info_hash gets turned into a string and url encoded in the GET request
    clientDict['info_hash'] = urllib.parse.unquote(clientDict['info_hash'])
    # so i decode it, trim the b'~' at the ends, decode then encode it (solution found online)
    clientDict['info_hash'] = clientDict['info_hash'][2:-1].encode().decode('unicode-escape').encode('ISO-8859-1')

    if clientDict['info_hash'] != torrent.info_hash:
        # if this tracker is not handling the torrent in the request
        return web.Response(text="ERROR:info_hash")
    else:
        if int(clientDict['left']) == 0: #this client is a seeder

            if clientDict['peer_id'] in leechers:
                #in the case of a leecher becoming a seeder
                del leechers[clientDict['peer_id']]
                leechersKeys.remove(clientDict['peer_id'])

            if clientDict['peer_id'] not in seeders: #new seeder case
                print('true')
                seedersKeys.append(clientDict['peer_id'])

            seeders[clientDict['peer_id']] = clientDict #update seeder info
            
            print('number of leechers: {} , number of seeders: {}'.format(len(leechersKeys),len(seedersKeys)))
            return web.Response(text="Thanks for the update seeder!")

        elif int(clientDict['left']) < 0: #this is the case for a peer leaving the swarm
            
            if clientDict['peer_id'] in leechers:
                del leechers[clientDict['peer_id']]
                leechersKeys.remove(clientDict['peer_id'])
                print('number of leechers: {} , number of seeders: {}'.format(len(leechersKeys),len(seedersKeys)))
                return web.Response(text="Goodbye leacher")

            if clientDict['peer_id'] in seeders:
                del seeders[clientDict['peer_id']]
                seedersKeys.remove(clientDict['peer_id'])
                print('number of leechers: {} , number of seeders: {}'.format(len(leechersKeys),len(seedersKeys)))
                return web.Response(text="Goodbye seeder")

            return web.Response(text="ERROR: You were not found in the swarm")

        else: #if this client is a leacher
            if len(seedersKeys) < 1:
                print('number of leechers: {} , number of seeders: {}'.format(len(leechersKeys),len(seedersKeys)))
                return web.Response(text = "ERROR: No seeders online")
            else:
                if clientDict['peer_id'] not in leechers: # new leacher case
                    leechersKeys.append(clientDict['peer_id']) 
                leechers[clientDict['peer_id']] = clientDict #update leacher info
                

                #now we return some peers for the leaching requestor
                
                peersNeededA = int(math.ceil(float(len(leechersKeys))/4))#the amount of peers we should try to get;
                peersNeededB = int(math.ceil(float(len(seedersKeys))/4)) #separate amount of leacher and seeder peers
                
                peersString = '' #this is the string of peer info which will be sent to the requestor
                rolledLeechers = []# these lists are used to make sure we don't consider re-rolled peers
                rolledSeeders = []
                piecePlan = clientDict['piecesStatus']
                while peersNeededA > 0:
                    randLeechKey = leechersKeys[random.randint(0,len(leechersKeys)-1)]
                    if randLeechKey not in rolledLeechers and randLeechKey != clientDict['peer_id']:
                        rolledLeechers.append(randLeechKey)
                        valid, pieceNum = findRequestablePiece(piecePlan,leechers[randLeechKey]['piecesStatus'])
                        if valid:
                            piecePlan =  piecePlan[0:pieceNum] + '1' + piecePlan[pieceNum+1:len(piecePlan)]
                            peersString += leechers[randLeechKey]['peer_id'] +':'+ leechers[randLeechKey]['ip'] + ':' + leechers[randLeechKey]['port']+':'+str(pieceNum)+',' 
                    peersNeededA -=1

                while peersNeededB > 0: #seeders considered last, because they are a last resort
                    randSeedersKey = seedersKeys[random.randint(0,len(seedersKeys)-1)]
                    if randSeedersKey not in rolledSeeders:
                        rolledSeeders.append(randSeedersKey)
                        valid, pieceNum = findRequestablePiece(piecePlan,seeders[randSeedersKey]['piecesStatus'])
                        if valid:
                            piecePlan = piecePlan[0:pieceNum] + '1' + piecePlan[pieceNum+1:len(piecePlan)]
                            peersString += seeders[randSeedersKey]['peer_id'] + ':' +seeders[randSeedersKey]['ip'] + ':' + seeders[randSeedersKey]['port'] +':'+str(pieceNum)+','
                    peersNeededB-=1
                print('number of leechers: {} , number of seeders: {}'.format(len(leechersKeys),len(seedersKeys)))
                return web.Response(text = peersString)
            
def findRequestablePiece(clientPieces, peerPieces):
    #TODO: decide if random or sequential pieces downloads are best; this is sequential
    if len(clientPieces) != len(peerPieces):
        print('Error piece lists are not the same size!?!?')
        return False, None
    else:
        for i in range(len(clientPieces)):
            if peerPieces[i] =='1' and clientPieces[i] == '0':
                return True, i
        return False, None
app = web.Application()
app.add_routes(routes)
tempIp = torrent.announce[7:]
ip = tempIp[:tempIp.index(':')]
web.run_app(app, host = ip,port = 6969)
