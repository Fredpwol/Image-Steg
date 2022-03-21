#!usr/bin/python3

from PIL import Image
import argparse
import numpy as np
import os
import copy
import secrets

#we use INT32_MAX for our maximum bit length
"""
Image Steganography using Lowest Significant Bits (LCB) works by fliping the last two bits of a channel in an Image.
#TODO: work on Discrete Cosine Transform (DCT) AND huffman encoding.
"""
"""
Encoding constants

This are header encoding constants which will be used to define what type of data is embeded in the Image.
"""


TXT = "TXT"  #done
PNG = "PNG"  #done
JPG = "JPG"  #done
WAV = "WAV"  #work
MP3 = "MP3"  # work


class ImageParser:
    def __init__(self, dir):
        parsed_image = self.__load_image(dir)
        self.image = parsed_image[0]
        self.dir = dir
        self.height = parsed_image[1]
        self.width = parsed_image[2]
        self.nchannel = parsed_image[3]
        self.__encoding = None
        self.__data_len = None

    @staticmethod
    def __load_image(im_dir):
        """
        Loads Image from a directory and returns the array representaion of the image and it's height and width
        args
        ----
            im_dir: str
            Image local directory
        returns
        -------
            tuple: (np.array, int, int)
        """
        im = Image.open(im_dir)
        im_arr = np.array(im)
        return im_arr, im.height, im.width, im_arr.shape[-1]


    def __encode_text_to_binary(self, string):
        """
        Returns a string of bits representation of the string.
        the characters in the string are decomosed to their decimal
        value on the ASCII table. Then converted to a string of 8bit
        binary.

        args
        ----
            string: str
        
        returns
        -------
            res: str
        """
        res = ""
        for char in string:
            if type(char) == int: char = chr(char)
            ascii_dec = ord(char)
            res += self.__return_binary(ascii_dec)
        return res
    
    @staticmethod
    def __return_binary(number, bitlen=8):
        """
        returns the binary value of a number.

        args
        ----
            number: int
            bitlen: int
        returns
        -------
            res: str
        """
        b = bin(number)[2:]
        return b.zfill(bitlen)


    def __encode_image_to_binary(self, image, height, width, num_channel):
        """
        Encodes an Image to binary
        """
        res = ""
        for i in range(height):
            for j in range(width):
                for k in range(num_channel):
                    value = image[i][j][k]
                    res += self.__return_binary(value)
        return res

    
    @staticmethod
    def __decode_binary_to_ascii(binary):
        """
        Returns an ascii string representation of a string of binary
        args
        ----
            binary: str
            A string of binary e.g 101001 
        returns
        -------
            str
        """
        res = ""
        for i in range(0, len(binary), 8):
            b = binary[i:i + 8]
            dec = eval(f"0b{b}")
            char = chr(dec)
            res += char
        return res


    def __encode_image(self, bitstream):
        """
        Encodes the a image with a binary string and returns a encoded image array.
        args
        ----
            bitstream: str
        returns
        -------
            np.array 
        """
        img_copy = copy.deepcopy(self.image)
        prev_index = 0
        data_len = len(bitstream)
        for i in range(self.height):
            for j in range(self.width):
                for k, channel in enumerate(img_copy[i][j]):
                    if (prev_index + 2) < data_len:
                        b = self.__return_binary(channel)
                        dec = eval(
                            f"0b{b[:6]}{bitstream[prev_index:2+prev_index]}")
                        img_copy[i][j][k] = dec
                        prev_index += 2
                    else:
                        return img_copy
        return img_copy

    
    @property
    def data_len(self):
        """
        gets the data length from header bits.
        """
        if self.__data_len is not None:
            return self.__data_len
        _range = self.image[0][:(32 // (self.nchannel * 2) + 1)]  #add 1 pixel to catch overlap
        res = ""
        count = 0
        for i in range(len(_range)):
            for channel in _range[i]:
                if count < 16:
                    res += self.__return_binary(channel)[-2:]
                    # print(res)
                    count += 1
                else:
                    break
        dec = eval(f"0b{res}")
        self.__data_len = dec
        return dec

    @property
    def encoding_type(self):
        """
        retrieve the encoding type of the secret message stored in the Image.
        """
        if self.__encoding is not None:
            return self.__encoding
        _range = self.image[0][(32 // (self.nchannel * 2)):]
        start_channel = (32 % self.nchannel) / 2
        res = ""
        count = 0
        for i in range(len(_range)):
            for j, channel in enumerate(_range[i]):
                if i == 0 and j < start_channel:
                    continue  # skip overlap by data length bits
                if count < 12:
                    res += self.__return_binary(channel)[-2:]
                    count += 1
                else:
                    break
            if count >= 12:
                break

        res = self.__decode_binary_to_ascii(res)
        self.__encoding = res
        return res


    def encode_audio_to_binary(self, audiofile):
        return NotImplementedError


    def __get_image_data(self, image, starting_pixel, start_channel):
        """
        retrieve image data from image i.e height, width, channel
        """
        _range = image[0][starting_pixel:]
        res = ""
        count = 0
        for i in range(len(_range)):
            for j, channel in enumerate(_range[i]):
                if i == 0 and j < start_channel:
                    continue  # skip overlap by data length bits
                if count < 40:
                    res += self.__return_binary(channel)[-2:]
                    count += 2
                else:
                    break
            if count >= 40:
                break
        height = eval(f"0b{res[0: 16]}")
        width = eval(f"0b{res[16: 32]}")
        channel = eval(f"0b{res[32: ]}")
        return (height, width, channel)


    def __decode_image(self):
        """
        Decodes a Encoded Image and return message.
        """
        starting_pixel = 56 // (self.nchannel * 2)
        start_channel = (56 % self.nchannel) / 2
        if self.encoding_type == PNG or self.encoding_type == JPG:
            hidden_image_height, hidden_image_width, hidden_image_channel = self.__get_image_data(
                self.image, starting_pixel, start_channel)
            starting_pixel = (56 + 40) // (self.nchannel * 2)
            start_channel = ((56 + 40) % self.nchannel) / 2
        length = 0
        res = ""
        for i in range(self.height):
            start = 0 if i != 0 else starting_pixel  # skip header pixels
            for j in range(start, self.width):
                for k, channel in enumerate(self.image[i][j]):
                    if i == 0 and j == starting_pixel and k < start_channel:
                        continue  # skip encoding overlap bits
                    if length < self.data_len:
                        res += self.__return_binary(channel)[-2:]
                        length += 2
                    else:
                        break
                if length >= self.data_len: break
            if length >= self.data_len: break
        if self.encoding_type == TXT:
            res = self.__decode_binary_to_ascii(res)
        if self.encoding_type == JPG or self.encoding_type == PNG:
            _image = np.zeros(
                (hidden_image_height, hidden_image_width, hidden_image_channel),
                dtype=np.uint8)
            prev_index = 0
            print(len(res))
            for i in range(hidden_image_height):
                for j in range(hidden_image_width):
                    for k in range(hidden_image_channel):
                        if prev_index + 8 > len(res): break
                        _image[i][j][k] = eval(
                            f"0b{res[prev_index:prev_index+8]}")
                        prev_index += 8
            res = _image
        return res
    

    @staticmethod
    def __get_image_bit_len(height, width, nchannel, iscover=False):
        """
        Calculates the total number of bits in a image and returns it
        args
        ----
            image: image to retrive info
            is_cover: if image is cover it multiplies by 2. 
        """
        num_bit = 2 if iscover else 8

        return height * width * nchannel * num_bit


    def compare_image_bitspace(self, im1, im2):
        return self.__get_image_bit_len(im1.shape[0], im1.shape[1], im1.shape[2], True) > self.__get_image_bit_len(im2.shape[0], im2.shape[1], im2.shape[2])


    def encode(self, format, message_data):
        """
        message_data: str, dir_to_image
        """
        if format == TXT:
            encoding = TXT
            text = self.__encode_text_to_binary(message_data)
            bitlen = len(text)
            encoding_bin = self.__encode_text_to_binary(encoding)
            bitlen_bin = self.__return_binary(bitlen, 32)
            data = bitlen_bin + encoding_bin + text
        elif format == PNG or format == JPG:
            message_image, message_image_height, message_image_width, message_image_channels = self.__load_image(message_data)
            assert self.compare_image_bitspace(self.image, message_image) , "Image file is to large to hide!"
            image_bits = self.__encode_image_to_binary(message_image, message_image_height, message_image_width, message_image_channels)
            bitlen = self.__return_binary(len(image_bits), 32)
            format = PNG if format == PNG else JPG
            format_bin = self.__encode_text_to_binary(format)
            data = bitlen + format_bin + self.__return_binary(message_image_height, 16) + \
            self.__return_binary(message_image_width, 16) + self.__return_binary(message_image_channels, 8) + image_bits
        else:
            raise ValueError("Please Enter a valid format")

        encoded_image = self.__encode_image(data)
        filename = os.path.basename(self.dir)
        filename = filename[:filename.find(".")]
        # print(encoded_image[0][:6], cover_image[0][:6])
        Image.fromarray(encoded_image.copy()).save(f"encoded-{filename}.png", )

        
    def decode(self):
        data = self.__decode_image()
        if self.encoding_type == TXT:
            print(data)
        elif self.encoding_type == JPG or self.encoding_type == PNG:
            # print(data[0][:5])
            Image.fromarray(data).save(
                f"{secrets.token_hex(16)}.{self.encoding_type.lower()}")


#height, width, channel


def main():
    """
    TO add encode images and hide data in it.
    """
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="mode")
    encode_parser = subparser.add_parser("encode", help="encodes the image")
    encode_parser.add_argument("-d", dest="directory", type=str)
    encode_parser.add_argument("-t", dest="text", type=str, default="")
    encode_parser.add_argument("-i", dest="image_dir", type=str)
    encode_parser.add_argument("-f", dest="format", type=str)
    decode_parser = subparser.add_parser("decode", help="decodes data hidden in image and prints it.")
    decode_parser.add_argument("-i", dest="image_dir", type=str)
    args = parser.parse_args()
    if args.mode:
        if args.image_dir:
            if args.mode == "encode":
                im = ImageParser(args.image_dir)
                im.encode(args.format.upper(), args.text )
            elif args.mode == "decode":
                ImageParser(args.image_dir).decode()
                # print(cover_image[0][: 6 ])
             
        else:
            raise FileNotFoundError
    else:
        print("Please specify a mode!")


if __name__ == '__main__':
    main()
