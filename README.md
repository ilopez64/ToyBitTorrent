# ToyBitTorrent

This is a "Toy" implementation of BitTorrent built with Python3 and asyncio
The client is not a practical BitTorrent client as it lacks too many
features to really be useful. This project was created for my graduate
networking class and to learn more about BitTorrent as well as Python's asyncio library.

Current features:

- [x] Download pieces (leeching)
- [x] Contact tracker periodically
- [X] Seed (upload) pieces
- [ ] Support multi-file torrents
- [ ] Resume a download

## Getting started

Install pipenv for virtual enviornment

    $ pip install pipenv

Install the needed dependencies

    $ pipenv install

This client requires a file to be shares (can be anything) and its 
torrent file. Every torrent file has a tracker server field which is 
used to hold the IP address of the tracker server. This server lists 
all the availible seeders for a given file. The IP must be specified
as: http://IP:PORT/announce

## Design considerations

The pieces are all requested in order, not implementing 
a rarestfirst algorithm, and the pieces are all kept in memory until 
the entire torrent is downloaded.

### Code walkthrough

`trackerServer` is run by the server for a given torrent file. It listens
for connections from other seeder or leecher clients and keeps a list of 
all peers a seeder can leech from. 

`ToyBitTorrentClient` is the center piece, it:

* Connects to the tracker in order to receive the peers to connect to.

* Based on that result, creates a Queue of peers that can be connected
  to.

* Determine the order in which the pieces should be requested from the
  remote peers.

* Assigns seeders to leecher roles once downloads are completed

`Torrent` is a custom class that holds all the torrent file information

For a tracker server, the commands are

    $ pipenv run python3 trackerServer --t (torrentFileName)

For a seeder client,

    $ pipenv run python3 startClient --t (torrentFileName) --f (fileName)

For a leecher client,

    $ pipenv run python3 startClient --t (torrentFileName)

Commands should be ran in this order, as there needs to first be a tracker server
to keep track of all peers and there must also first be a seeder for a leecher to
download from.

Included are sample files that can be used to test the client. Transmission on MacOS
was used to create the torrent files for both moby.txt and moby.jpg. New torrent files
must be created since the tracker server IP addresses in these torrent files may be different from 
the IP address that will be ran locally.

## References

Eliasson, M. (2016, August 24). A BitTorrent client in Python 3.5. Retrieved November 3, 2019, 
* https://markuseliasson.se/article/bittorrent-in-python/

Cohen, B. (2008, January 10). The BitTorrent Protocol Specification. Retrieved November 3, 2019
* http://bittorrent.org/beps/bep_0003.html