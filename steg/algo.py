#!usr/bin/python3

from PIL import Image
from scipy.io.wavfile import write
from bitstring import BitArray

import enum
import argparse
import numpy as np
import os
import copy
import secrets

import librosa
import librosa.display

from steg.constants import ENCODING_HEADER_BIT_LEN


# we use INT32_MAX for our maximum bit length
"""
Image Steganography using Lowest Significant Bits (LCB) works by fliping the last two bits of a channel in an Image.
#TODO: work on Discrete Cosine Transform (DCT) AND huffman encoding.
"""
"""
Encoding constants

This are header encoding constants which will be used to define what type of data is embeded in the Image.
"""


class Format(enum.Enum):
    TXT = "TXT"  # done
    PNG = "PNG"  # done
    JPG = "JPG"  # done
    WAV = "WAV"  # work
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
        self.__audio_samplerate = None
        self.__audio_frames_length = None
        self.__hidden_image_width = None
        self.__hidden_image_height = None
        self.__hidden_image_nchannel = None

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
            if type(char) == int:
                char = chr(char)
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

    
    def __bitwise_replace_lsb(self, data, val):
        bin_ = data & 0b1111_1100
        
        res = bin_ | val

        return res
        

    def __get_lsb(self, value, n=2):
        mask = (2 ** n) - 1

        return value & mask
        


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
            b = binary[i : i + 8]
            dec = eval(f"0b{b}")
            char = chr(dec)
            res += char
        return res
    

    def get_bitlen(self, num):
        res = 0

        while num != 0:
            num >>= 1
            res += 1
        return res


    def __decode_number_to_ascii_string(self, num):

        bitmask = 0b1111_1111
        st = ""
        bitlen = self.get_bitlen(num)
        for shift in range(0, bitlen, 8):
            charid = (num & (bitmask << shift)) >> shift
            char = chr(charid)
            st = char + st
        return st
             

    def __encode_image(self, binary_data, bitstream=None):
        """
        Encodes the a image with a binary string and returns a encoded image array.
        args
        ----
            binary_data: str
        returns
        -------
            np.array
        """
        img_copy = copy.deepcopy(self.image)
        prev_index = 0
        data_len = len(binary_data)
        for i in range(self.height):
            for j in range(self.width):
                for k, channel in enumerate(img_copy[i][j]):
                    if (prev_index + 2) < data_len:
                        sbit = int(binary_data[prev_index : 2 + prev_index], base=2)
                        prev_index += 2
                    elif bitstream is not None:
                        try:
                            sbit = int(bitstream.__next__(), base=2)
                        except StopIteration:
                            return img_copy
                    else:
                        return img_copy
                    img_copy[i][j][k] = self.__bitwise_replace_lsb(channel, sbit)
        return img_copy

    @property
    def data_len(self):
        """
        gets the data length from header bits.
        """
        if self.__data_len is not None:
            return self.__data_len
        _range = self.image[0][
            : (32 // (self.nchannel * 2) + 1)
        ]  # add 1 pixel to catch overlap
        res = 0
        count = 0
        for i in range(len(_range)):
            for channel in _range[i]:
                if count < 16:
                    res = (res << 2) | self.__get_lsb(channel)
                    # print(res)
                    count += 1
                else:
                    break
        self.__data_len = res
        return res

    @property
    def encoding_type(self):
        """
        retrieve the encoding type of the secret message stored in the Image.
        """
        if self.__encoding is not None:
            return self.__encoding
        _range = self.image[0][(32 // (self.nchannel * 2)) :]
        start_channel = (32 % self.nchannel) / 2
        res = 0
        count = 0
        for i in range(len(_range)):
            for j, channel in enumerate(_range[i]):
                if i == 0 and j < start_channel:
                    continue  # skip overlap by data length bits
                if count <  ENCODING_HEADER_BIT_LEN / 2:
                    res = (res << 2) | self.__get_lsb(channel)
                    count += 1
                else:
                    break
            if count >= ENCODING_HEADER_BIT_LEN / 2:
                break
        self.__encoding = self.__decode_number_to_ascii_string(res)
        return self.__encoding

    def encode_audio_to_binary(self, audiofile, bins=2):
        frames, samplerate = librosa.load(audiofile, sr=44100 / 20)
        self.__audio_samplerate = samplerate
        self.__audio_frames_length = len(frames)
        for i in range(len(frames)):
            freq = frames[i]
            bin_ = BitArray(float=freq, length=32).bin
            for i in range(0, len(bin_), bins):
                yield bin_[i : i + bins]

    def __get_image_data(self, image, starting_pixel, start_channel):
        """
        retrieve image data from image i.e height, width, channel
        """
        _range = image[0][starting_pixel:]
        res = 0
        count = 0
        for i in range(len(_range)):
            for j, channel in enumerate(_range[i]):
                if i == 0 and j < start_channel:
                    continue  # skip overlap by data length bits
                if count < 40:
                    res = (res << 2) | self.__get_lsb(channel)
                    count += 2
                else:
                    break
            if count >= 40:
                break

        bitmask = 0b11111111_11111111_00000000_00000000_00000000
        height = (res & bitmask) >> 24
        width = (res & (bitmask >> 16)) >> 8
        channel = res & 0b11111111
        return (height, width, channel)

    def __get_audio_data(self, starting_pixel, start_channel):
        count = 0
        _range = self.image[0][starting_pixel:]
        res = 0
        for i in range(len(_range)):
            for j, channel in enumerate(_range[i]):
                if i == 0 and j < start_channel:
                    continue  # skip overlap by data length bits
                if count < 32:
                    res = (res << 2) | self.__get_lsb(channel)
                    count += 2
                else:
                    break
            if count >= 32:
                break
        return res

    def __decode_image(self):
        """
        Decodes a Encoded Image and return the binary data.
        """
        starting_pixel = 56 // (self.nchannel * 2)
        start_channel = (56 % self.nchannel) / 2
        if (
            self.encoding_type == Format.PNG.value
            or self.encoding_type == Format.JPG.value
        ):
            (
                self.__hidden_image_height,
                self.__hidden_image_width,
                self.__hidden_image_nchannel,
            ) = self.__get_image_data(self.image, starting_pixel, start_channel)
            starting_pixel = (56 + 40) // (self.nchannel * 2)
            start_channel = ((56 + 40) % self.nchannel) / 2
        elif self.encoding_type in [Format.WAV.value, Format.MP3.value]:
            self.__audio_samplerate = self.__get_audio_data(
                starting_pixel, start_channel
            )
            starting_pixel = (56 + 32) // (self.nchannel * 2)
            start_channel = ((56 + 32) % self.nchannel) / 2
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
                if length >= self.data_len:
                    break
            if length >= self.data_len:
                break
        return res

    @staticmethod
    def get_pixel_count(imgarr):
        """
        Calculates the total number of bits in a image and returns it
        args
        ----
            image: image to retrive info
            is_cover: if image is cover it multiplies by 2.
        """

        return imgarr[0] * imgarr[1] * imgarr[2]

    @property
    def available_bitspace(self):
        return self.height * self.width * self.nchannel * 2

    def compare_image_bitspace(self, other_image):
        other_image_pixels = ImageParser.get_pixel_count(other_image)
        return self.available_bitspace > other_image_pixels * 8

    def encode(self, format, message_data, as_generator=False, output_dir=None):
        """
        message_data: str, dir_to_image
        """
        encoding_bin = self.__encode_text_to_binary(format)

        if as_generator:
            yield 2
        
        if format == Format.TXT.value:
            text = self.__encode_text_to_binary(message_data)

            if as_generator:
                yield 20

            bitlen = len(text)
            bitlen_bin = self.__return_binary(bitlen, 32)
            data = bitlen_bin + encoding_bin + text

            if as_generator: yield 50
        elif format == Format.PNG.value or format == Format.JPG.value:
            (
                message_image,
                message_image_height,
                message_image_width,
                message_image_channels,
            ) = self.__load_image(message_data)
            if as_generator: yield 20

            assert self.compare_image_bitspace(
                (message_image_height, message_image_width, message_image_channels)
            ), "Image file is to large to hide!"


            image_bits = self.__encode_image_to_binary(
                message_image,
                message_image_height,
                message_image_width,
                message_image_channels,
            )

            if as_generator: yield 45
            
            bitlen = self.__return_binary(len(image_bits), 32)


            data = (
                bitlen
                + encoding_bin
                + self.__return_binary(message_image_height, 16)
                + self.__return_binary(message_image_width, 16)
                + self.__return_binary(message_image_channels, 8)
                + image_bits
            )

            if as_generator: yield 50

        elif format == Format.MP3.value or format == Format.WAV.value:
            audio_bins = self.encode_audio_to_binary(message_data)

            if as_generator:yield 30

            tempbin = audio_bins.__next__()
            sample_rate = self.__audio_samplerate or 44100
            if self.available_bitspace < self.__audio_frames_length * 32:
                raise ValueError(
                    f"Sorry the audio bits is greater the the amount of available signiicant bit in the image. AVAILABE: {self.available_bitspace} EXPECTED {self.__audio_frames_length * 32}"
                )
            data = (
                self.__return_binary(self.__audio_frames_length * 32, 32)
                + encoding_bin
                + self.__return_binary(int(sample_rate), 32)
                + tempbin
            )


            if as_generator: yield 50
        else:
            raise ValueError("Please Enter a valid format")
            
        bitstream = (
            None if format not in [Format.MP3.value, Format.WAV.value] else audio_bins
        )
        encoded_image = self.__encode_image(data, bitstream)

        if as_generator: yield 75

        filename = os.path.basename(self.dir)[: filename.find(".")]
        # print(encoded_image[0][:6], cover_image[0][:6])
        output_dir = "tmp" if output_dir else output_dir

        Image.fromarray(encoded_image.copy()).save(
            os.path.join(output_dir, f"encoded-{filename}.png"),
        )
        
        if as_generator: yield 100

    def decode(self):
        data = self.__decode_image()
        if self.encoding_type == Format.TXT.value:
            data = self.__decode_binary_to_ascii(data)
            print(data)
            return data
        elif (
            self.encoding_type == Format.JPG.value
            or self.encoding_type == Format.PNG.value
        ):
            _image = np.zeros(
                (
                    self.__hidden_image_height,
                    self.__hidden_image_width,
                    self.__hidden_image_nchannel,
                ),
                dtype=np.uint8,
            )
            prev_index = 0
            for i in range(self.__hidden_image_height):
                for j in range(self.__hidden_image_width):
                    for k in range(self.__hidden_image_nchannel):
                        if prev_index + 8 > len(data):
                            break
                        _image[i][j][k] = eval(f"0b{data[prev_index:prev_index+8]}")
                        prev_index += 8
            # print(data[0][:5])
            im = Image.fromarray(_image)
            im.save(f"{secrets.token_hex(16)}.{self.encoding_type.lower()}")
            im.show()
            return f"Image file saved at {secrets.token_hex(16)}.{self.encoding_type.lower()}"

        elif self.encoding_type in [Format.MP3.value, Format.WAV.value]:
            audio_frames = np.zeros(len(data) // 32)
            for i in range(0, len(data) // 32, 32):
                freq_val = BitArray(bin=data[i : i + 32]).float
                audio_frames[i] = freq_val
            write(f"{secrets.token_hex(16)}.wav", self.__audio_samplerate, audio_frames)
            print("audio file saved")


# height, width, channel


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
    decode_parser = subparser.add_parser(
        "decode", help="decodes data hidden in image and prints it."
    )
    decode_parser.add_argument("-i", dest="image_dir", type=str)
    args = parser.parse_args()
    if args.mode:
        if args.image_dir:
            if args.mode == "encode":
                im = ImageParser(args.image_dir)
                im.encode(args.format.upper(), args.text)
            elif args.mode == "decode":
                ImageParser(args.image_dir).decode()
                # print(cover_image[0][: 6 ])

        else:
            raise FileNotFoundError
    else:
        print("Please specify a mode!")


if __name__ == "__main__":
    main()
