import unittest
from bencoding import Decoder

class TestBencoding(unittest.TestCase):
	def test_list_int(self):
		with open('moby.txt.torrent','rb') as f:
			meta = f.read()
			torrent = Decoder(meta).decode()
		self.assertEqual(torrent[b'announce'],(b'http://192.168.1.152:6969/announce'))

if __name__ == '__main__':
    unittest.main()
