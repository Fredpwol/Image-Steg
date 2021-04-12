from PIL import Image
import argparse
import numpy as np
import os

#we use INT32_MAX for our maximum bit length

"""
Encoding constants
"""
XML = "XML"
JSON = "JSN"
TXT = "TXT" #done
PNG = "PNG"
JPG = "JPG" #work
WAV = "WAV"
MP3 = "MP3"


def return_binary(string):
	res = ""
	for char in string:
		if type(char) == int: char = chr(char)
		ascii_dec = ord(char)
		b = bin(ascii_dec)[2:]
		res += b.zfill(8)
	return res

def decode_binary_to_ascii(binary):
	res = ""
	for i in range(0, len(binary), 8):
		b = binary[i :i+8]
		dec = eval(f"0b{b}")
		char = chr(dec)
		res += char
	return res

def load_image(im_dir):
	im = Image.open(im_dir)
	im_arr = np.array(im)
	return im_arr, im.height, im.width


def encode_image(image, height, width, text_encoded):
	img_copy = image 
	for i in range(height):
		for j in range(width):
			for k, channel in enumerate(img_copy[i][j]):
				if text_encoded != "":
					b = bin(channel)[2:].zfill(8)
					dec = eval(f"0b{b[:6]}{text_encoded[:2]}")
					img_copy[i][j][k] = dec
					text_encoded = text_encoded[2:]
				else:
					return img_copy
		print(i)
	return img_copy

def get_data_len(image):
	_range = image[0][:6]
	res = ""
	count = 0
	for i in range(len(_range)):
		for channel in _range[i]:
			if count < 16:
				res += bin(channel)[2:].zfill(8)[-2:]
				# print(res)
				count += 1
			else:
				break
	dec = eval(f"0b{res}")
	return dec

def get_encoding_type(image):
	_range = image[0][5:  ]
	res = ""
	count = 0
	for i in range(len(_range)):
		for j, channel in enumerate(_range[i]):
			if j == 0 and i == 0: continue # skip overlap by data length bits
			if count < 12:
				res += bin(channel)[2:].zfill(8)[-2:]
				count += 1
			else:
				break
		if count >= 12:
			break

	res = decode_binary_to_ascii(res)
	return res

	

def decode_image(image, height, width):
	data_len = get_data_len(image)
	encoding = get_encoding_type(image)
	length = 0
	res = ""
	for i in range(height):
		start = 0 if i != 0 else 9 # skip header pixels
		for j in range(start, width):
			for k, channel in enumerate(image[i][j]):
				if i == 0 and j == 9 and k == 0: continue # skip encoding overlap bits
				if length < data_len:
					res += bin(channel)[2:].zfill(8)[-2:]
					length += 2
				else:
					break
			if length >= data_len: break
		if length >= data_len: break 
	if encoding == TXT:
		res = decode_binary_to_ascii(res)

	return res


def main():
	parser = argparse.ArgumentParser()
	subparser = parser.add_subparsers(dest="mode")
	encode_parser = subparser.add_parser("encode", help="encodes the image")
	encode_parser.add_argument("-d", dest="directory", type=str)
	encode_parser.add_argument("-t", dest="text", type=str, default="")
	encode_parser.add_argument("-i", dest="image_dir", type=str)
	decode_parser = subparser.add_parser("decode", help="decodes data hidden in image aand prints it.")
	decode_parser.add_argument("-i", dest="image_dir", type=str)
	args = parser.parse_args()
	if args.mode:
		if args.image_dir:
			im_arr, height, width = load_image(args.image_dir)
			if args.mode == "encode":
				text = args.text
				if args.directory:
					text = open(args.directory, "rb").read()
				encoding = TXT
				text = return_binary(text)
				bitlen = len(text)
				encoding_bin = return_binary(encoding)
				bitlen_bin = bin(bitlen)[2:].zfill(32)
				data = bitlen_bin + encoding_bin + text
				encoded_image = encode_image(im_arr, height, width, data)
				filename = os.path.basename(args.image_dir)
				filename = filename[:filename.find(".")]
				Image.fromarray(encoded_image).save(f"encoded-{filename}.png")
			elif args.mode == "decode":
				data = decode_image(im_arr, height, width)
				print(data)
		else:
			raise FileNotFoundError
	else:
		print("Please specify a mode!")
	# bins = return_binary("Hello my name is Fredick i am a boy and i suck at evrything call me for mental health disorder isssues on +2358057695833 shi!!")
	# print(bins)
	# print(f"value in ascii is => {decode_binary_to_ascii(bins)}")

if __name__ == '__main__':
	main()