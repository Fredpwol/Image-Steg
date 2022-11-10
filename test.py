from steg.algo import ImageParser, Format
import time

img = 'test_data/wal.jpg'
encoded = 'encoded-wal.png'


def encode(type, value):
    imparser = ImageParser(img)
    imparser.encode(type, value)

def decode():
    imparser = ImageParser(encoded)
    print(imparser.decode())

test_image = 'test_data/tesfred.jpg'

test_text = open('test_data/se').read()

if __name__ == '__main__':
    s = time.time()
    encode(Format.JPG.value, 'test_data/tesfred.jpg')
    decode()
    print(f"Finished at {time.time() - s}(sec)!")
