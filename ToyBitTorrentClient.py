import asyncio
import socket
import random
import Torrent
from sendAnnouncePlus import sendAnnounce 

class Client:
    def __init__(self, args):
        self.p_id = '-PC0001-' + ''.join([str(random.randint(0, 9)) for _ in range(12)])
        print('I am ' + self.p_id)
        self.port = 0
        self.ip = ''
        self.hostTuple = ''
        s = socket.socket()
        for i in range(6881,6890):
           try:
               s.bind((socket.gethostbyname(socket.gethostname()),i))
               self.hostTuple = s.getsockname()
               self.port = self.hostTuple[1]
               self.ip = self.hostTuple[0]
               s.close() #DEBUG: might not free the socket
               break
           except:
               print('wha?!')
               continue
        if self.port == 0 or self.ip == '':
            print('could not find available socket')
            exit()

        if args.ip != None:
            self.ip = args.ip

        print('listening on ' + self.ip)
        self.mode = 'l' 
        self.torrent = Torrent.Torrent(args.t)#create an object describing the torrent file
        #self.torrent.announce = 'http://149.61.172.213:6969/announce' #DEBUG
        self.downloadedFile = []
        self.piece_amt_obtained = 0
        self.uploaded = 0

        if args.f != None:
            self.mode = 's'
            
            with open(args.f,'rb') as file:
                
                piece = file.read(self.torrent.piece_length)
                while piece:
                    if self.torrent.checkPiece(piece, self.piece_amt_obtained) == False:
                        print('ERROR: The given file does not match the torrent')
                        exit()
                    self.downloadedFile.append(piece)
                    piece = file.read(self.torrent.piece_length)
                    self.piece_amt_obtained +=1
                
            #print(piece_amt_obtained)
        else:
            
            for i in range(len(self.torrent.pieces)):
                self.downloadedFile.append(None)
        print('client ready to start on "' + self.mode + '" mode')
        

    @asyncio.coroutine
    def wakeup(self): # hack to allow keyboard interrupt from the command line
        while True: #basically a function needs to be running for the program
            yield from asyncio.sleep(1) #to interrupt
            if self.mode == 's':
                pass
                #TODO: perhaps do seeder announce here?

    @asyncio.coroutine
    def getFile(self,loop):
        peerMatrix = []
        
        while self.piece_amt_obtained < len(self.torrent.pieces):
        #first arg to request_piece is info_hash(20bytes) + peer_id of peer(20bytes) , and later + piece#(var bytes)
        #TODO: async might cause premature announces!!
            yield from asyncio.sleep(1) #DEBUG
            peerMatrix = \
                       sendAnnounce(self.torrent, self.p_id, self.downloadedFile, self.mode, self.uploaded,self.hostTuple,False)
            if len(peerMatrix) == 0:
                print('low on peers, will retry....')
                yield from asyncio.sleep(3)
                continue
            else:
                
                for peers_id,ip,port,piece_num in peerMatrix:
                    #print('response: {} , {} , {} , {}'.format(peers_id,ip,port,piece_num))
                    yield from self.request_piece(self.torrent.info_hash + peers_id.encode(),ip,port, piece_num, loop)
                   
        print('***Done leaching - coroutine ended!')
        #This announce down here always intiates seeder status on the tracker side
        sendAnnounce(self.torrent, self.p_id, self.downloadedFile, self.mode, self.uploaded,self.hostTuple,False)

    @asyncio.coroutine
    def request_piece(self,message,ip, port, piece_num, loop):
        #add the piece number requested to the byte string (in bytes form)
        message = message + str(piece_num).encode()
        
        reader, writer = yield from asyncio.open_connection(ip, int(port),
                                                            loop=loop)

        print('Asked {} for piece {} of length {}'.format(message[20:40].decode(),piece_num,self.torrent.piece_length))
        writer.write(message)

        if int(piece_num) == len(self.torrent.pieces) - 1:
            expectedSize = self.torrent.total_size % self.torrent.piece_length
        else:
            expectedSize = self.torrent.piece_length
        
        data = yield from reader.readexactly(expectedSize)
        print('bytes downloaded: ' + str(len(data)))

        #print('Close the socket')
        writer.close()

        if self.torrent.checkPiece(data,int(piece_num)) == True:
            self.downloadedFile[int(piece_num)] = data
            self.piece_amt_obtained += 1
            if self.piece_amt_obtained == len(self.torrent.pieces):
                with open('downloaded' + self.torrent.product_name,'w+b') as fileTarget:
                    for piece in self.downloadedFile:
                        fileTarget.write(piece)
                print('file complete')
                self.mode = 's'
        else:
            print('error! piece recieved was apparently incorrect!')

    @asyncio.coroutine
    def pieceGiver(self,reader, writer): #NOTE: This is the server function
        data = yield from reader.read(100) #TODO: for some reason it wont work with no arg
        info_hash = data[:20]
        p_id = data[20:40].decode()
        piece_wanted = int(data[40:].decode())
        
        #message at this point should be a string with an index number for piece desired
        
        addr = writer.get_extra_info('peername')
        print("Received request for piece %r from %r" % (str(piece_wanted), addr))
        #yield from asyncio.sleep(3)
        if info_hash == self.torrent.info_hash \
           and self.downloadedFile[piece_wanted] != None\
           and p_id == self.p_id:
            print("Sent piece: %r" %str(piece_wanted))
            writer.write(self.downloadedFile[piece_wanted])
            yield from writer.drain()
        else:
            print("Rejected!, info_hash incorrect or piece not available or p_id wrong!!")
            writer.write('error'.encode())
            #writer.write(bytearray(self.torrent.piece_length)) #returns 0s in btyes form
            self.uploaded +=1
            yield from writer.drain()

        writer.close()

    def run(self):
        try:
            #NOTE: all of the async functions must be called in the try
            # so that the CRTL+C can be caught at all stages!
            loop = asyncio.get_event_loop()
            serv_coro = asyncio.start_server(self.pieceGiver, self.ip, self.port, loop=loop)
            server = loop.run_until_complete(serv_coro)
            loop.create_task(self.wakeup())
            loop.run_until_complete(self.getFile(loop))
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        print('closing')
        sendAnnounce(self.torrent, self.p_id, self.downloadedFile, self.mode, self.uploaded,self.hostTuple,True)
        #TODO: Change tracker to handle new arguments
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
    
