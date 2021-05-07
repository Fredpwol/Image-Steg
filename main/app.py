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
        self.height = parsed_image[1]
        self.width = parsed_image[2]
        self.nchannel = parsed_image[3]

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
            res += return_binary(ascii_dec)
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
        res = ""
        b = bin(number)[2:]
        res += b.zfill(bitlen)
    return res


    def __encode_image_to_binary(self, image, height, width, num_channel):
        """
        Encodes an Image to binary
        """
        res = ""
        for i in range(height):
            for j in range(width):
                for k in range(num_channel):
                    value = image[i][j][k]
                    res += return_binary(value)
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
                        b = return_binary(channel)
                        dec = eval(
                            f"0b{b[:6]}{text_encoded[prev_index:2+prev_index]}")
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
        _range = self.image[0][:(32 // (self.nchannel * 2) + 1)]  #add 1 pixel to catch overlap
        res = ""
        count = 0
        for i in range(len(_range)):
            for channel in _range[i]:
                if count < 16:
                    res += return_binary(channel)[-2:]
                    # print(res)
                    count += 1
                else:
                    break
        dec = eval(f"0b{res}")
        return dec

    @property
    def encoding_type(self):
        """
        retrieve the encoding type of the secret message stored in the Image.
        """
        _range = image[0][(32 // (self.nchannel * 2)):]
        start_channel = (32 % self.nchannel) / 2
        res = ""
        count = 0
        for i in range(len(_range)):
            for j, channel in enumerate(_range[i]):
                if i == 0 and j < start_channel:
                    continue  # skip overlap by data length bits
                if count < 12:
                    res += return_binary(channel)[-2:]
                    count += 1
                else:
                    break
            if count >= 12:
                break

        res = decode_binary_to_ascii(res)
        return res


    def encode_audio_to_binary(self, audiofile):
        return NotImplementedError


    @staticmethod
    def __get_image_data(image, starting_pixel, start_channel):
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
                    res += return_binary(channel)[-2:]
                    count += 2
                else:
                    break
            if count >= 40:
                break
        height = eval(f"0b{res[0: 16]}")
        width = eval(f"0b{res[16: 32]}")
        channel = eval(f"0b{res[32: ]}")
        return (height, width, channel)


    def decode_image(self):
        """
        Decodes a Encoded Image and return message.
        """
        data_len = get_data_len(self.image, self.)
        encoding = get_encoding_type(image, num_channel)
        starting_pixel = 56 // (num_channel * 2)
        start_channel = (56 % num_channel) / 2
        if encoding == PNG or encoding == JPG:
            hidden_image_height, hidden_image_width, hidden_image_channel = self.__get_image_data(
                image, starting_pixel, start_channel)
            starting_pixel = (56 + 40) // (num_channel * 2)
            start_channel = ((56 + 40) % num_channel) / 2
        length = 0
        res = ""
        for i in range(height):
            start = 0 if i != 0 else starting_pixel  # skip header pixels
            for j in range(start, width):
                for k, channel in enumerate(image[i][j]):
                    if i == 0 and j == starting_pixel and k < start_channel:
                        continue  # skip encoding overlap bits
                    if length < data_len:
                        res += bin(channel)[2:].zfill(8)[-2:]
                        length += 2
                    else:
                        break
                if length >= data_len: break
            if length >= data_len: break
        if encoding == TXT:
            res = decode_binary_to_ascii(res)
        if encoding == JPG or encoding == PNG:
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
    def __get_bit_space(image, iscover=False):
        """
        Calculates the total number of bits in a image and returns it
        args
        ----
            image: image to retrive info
            is_cover: if image is cover it multiplies by 2. 
        """
        n_bit = 2 if iscover else 8
        return image.shape[0] * image.shape[1] * image.shape[1] * n_bit

    @staticmethod
    def __get_image_bit_len(height, width, nchannel, iscover=False):
        num_bit = 2 if iscover else 8

        return height * width * nchannel * num_bit


    def encode(self, image, format, message_data):
        format = format.lower()
        if format == TXT.lower():
            encoding = TXT
            text = self.__encode_text_to_binary(message_data)
            bitlen = len(text)
            encoding_bin = self.__encode_text_to_binary(encoding)
            bitlen_bin = self.__return_binary(bitlen, 32)
            data = bitlen_bin + encoding_bin + text
        elif format == PNG.lower() or format == JPG.lower():
            assert self.__get_image_bit_len(im_arr.shape[0], im_arr.shape[1], im_arr.shape[2], True) > get_image_bit_len(image_arr.shape[0], image_arr.shape[1], image_arr.shape[2]), "Image file is to large to hide!"
            num_channel = image_arr.shape[-1]
            image_bits = self.__encode_image_to_binary(self.image, self.height, self.width, self.nchannel)
            bitlen = self.__return_binary(len(image_bits), 32)
            format = PNG if format == PNG.lower() else JPG
            format_bin = self.__encode_text_to_binary(format)
            data = bitlen + format_bin + return_binary(image_height, 16) + return_binary(image_width, 16) + return_binary(num_channel, 8) + image_bits
        else:
            raise ValueError("Please Enter a valid format")

        encoded_image = self.__encode_image(data)
        filename = os.path.basename(args.image_dir)
        filename = filename[:filename.find(".")]
        # print(encoded_image[0][:6], cover_image[0][:6])
        Image.fromarray(encoded_image.copy()).save(
            f"encoded-{filename}.png", )

        
        def decode(self):
            data, encoding = self.__decode_image(cover_image, height, width,
                                            cover_image.shape[-1])
            print(encoding)
            if encoding == TXT:
                print(data)
            elif encoding == JPG or encoding == PNG:
                # print(data[0][:5])
                Image.fromarray(data).save(
                    f"{secrets.token_hex(16)}.{encoding.lower()}")


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
            cover_image, height, width = load_image(args.image_dir)
            print(cover_image.shape)
            if args.mode == "encode":

            elif args.mode == "decode":
                # print(cover_image[0][: 6 ])
             
        else:
            raise FileNotFoundError
    else:
        print("Please specify a mode!")


if __name__ == '__main__':
    main()
