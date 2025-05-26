import numpy as np
from tensorflow.keras.preprocessing import image


def convert_strings_to_floats(input_array):
    output_array = []
    for element in input_array:
        if element == '':
            continue
        converted_float = float(element)
        output_array.append(converted_float)
    return output_array


def preprocess_image(img_path, target_size=(224, 224)):
    cat_image = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(cat_image)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0
    return img_array


def str_processing(text):
    text = text.replace('\n', ' ')
    while '  ' in text:
        text = text.replace('  ', ' ')
    while '[' in text:
        text = text.replace('[', '')
    while ']' in text:
        text = text.replace(']', '')
    return text
