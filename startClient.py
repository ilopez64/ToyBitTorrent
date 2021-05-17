import argparse
import ToyBitTorrentClient

parser = argparse.ArgumentParser()
#Torrent file arg
parser.add_argument('--t')
#Seeding File arg: such a case means trying to start with seeder mode
parser.add_argument('--f')
#optional ip argument for linux and macOS users. auto ip detection is unreliable for them
parser.add_argument('--ip')
args = parser.parse_args()

client = ToyBitTorrentClient.Client(args)
client.run()
