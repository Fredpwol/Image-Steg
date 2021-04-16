# Main App
 
 This is the testing stage of the algorithm and the web app haven't been built yet. but we are currently working on that.

## Installation and Usage

 To use this algorithm in it's current form, clone the repo to your PC. then make sure you have pillow or numpy in the python version you are using. else navigate to the repo on your pc in your command line and enter `pip install -r requirement.txt`.

 Once that's done naviagate to the main folder by typing `cd main`.

 ### Encoding
 To encode text into an Image on your pc run

 ```shell
 python app.py encode -i {PATH_TO_IMAGE} -t {TEXT_TO_ENCODE}
 ``` 
 Where: 
 - `{PATH_TO_IMAGE}` is the path to your image file on your machine, and 

 - `{TEXT_TO_ENCODE}` is a text to encode in your image.
 <br>
 <br>
 
 To encode text files i.e non encoded files e.g .txt, .html, .json e.t.c.
 ```shell
 python app.py encode -i {PATH_TO_IMAGE} -f txt -d {FILE_PATH}
 ``` 
  To encode text files i.e non encoded files e.g .txt, .html, .json e.t.c.
 ```shell
 python app.py encode -i {PATH_TO_IMAGE} -f txt -d {FILE_PATH}
 ``` 
 
To encode Images for now jpegs and png.
 ```shell
 python app.py encode -i {PATH_TO_IMAGE} -f png|jpg -d {PATH_TO_EMBEDED_IMAGE}
 ``` 
The format flag can be either png or jpg depending on the embeded image type.
 
 ### Decoding
Afer encoding a image will be created with the encoded-{IMAGE_NAME} in the main dir, This is the chipher image or the encoded image. to decode the image and retrive hidden message run.

```shell
python app.py decode -i encoded-{IMAGE_NAME}
```

if the embeded message is text it will be printed on the terminal, if its an image a image with 16 digits hex will be created in the main dir which is th hidden image.

> <b>Note</b>
<br>
Might have issues when hiding images if the cover image does'nt have enought pixels to hold the secert image. will work on validating images soon but for now just note that not all pixels in your image can fit in any image make sure your cover image has enough pixels to hold it.

