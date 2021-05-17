import bencoding
from hashlib import sha1



class Torrent:
      def __init__(self, torrentFilename):
          torrentFile = open(torrentFilename,'rb') # the 'rb' is for read binary format
          torrentStr = torrentFile.read()
          torrentFile.close()
          meta = bencoding.Decoder(torrentStr).decode()
          self.meta = meta
          info = bencoding.Encoder(meta[b'info']).encode()
          self.info_hash = sha1(info).digest()
          #info hash is used to prove that a client is dealing with correct torrent
          self.total_size = int(meta[b'info'][b'length'])
          self.announce = meta[b'announce'].decode('utf-8')
          self.piece_length = int(meta[b'info'][b'piece length'])
          self.product_name = meta[b'info'][b'name'].decode('utf-8')
          # product_name should be used in two cases on startup:
          # - starting in Seedermode: read the file byte by byte AND compare the hashed pieces
          # to the pieces list here
          # - starting in Leacher: used to write file when all pieces are assembled
          
          self.pieces = []
          #NOTE: the pieces list holds the sha1 hash of each piece of the file
          #torrented. It is used check pieces of a local file, or downloaded pieces
          offset = 0
          length = len(meta[b'info'][b'pieces'])

          while offset < length:
              self.pieces.append(meta[b'info'][b'pieces'][offset:offset + 20])
              offset += 20

      def checkPiece(self, downloadedPiece, pieceNum):
            return sha1(downloadedPiece).digest() == self.pieces[pieceNum]
                  

        
#torObj = Torrent('moby.txt.torrent')


#with open('moby.txt','rb') as f:
 #   piece = f.read(torObj.piece_length)
    #print(sha1(piece).digest())
    #print(torObj.pieces[0] == sha1(piece).digest())
    
