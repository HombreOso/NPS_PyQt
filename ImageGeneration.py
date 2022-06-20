import gc
import re
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askdirectory
import numpy as np
import os
import xlsxwriter as xlsx
import openpyxl as opxl
from natsort import natsorted, ns
import pydicom
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
from PIL import Image, ImageTk
import itertools
import cv2
import time
import functools as fut
import pandas as pd
import docx
from scipy import optimize as opt
import multiprocessing as mp
import json



def create_image_from_2d_array(arr_2d, filename):
    """
    Normalize passed 2d_array between values 0 and 255 and create image saved as filename.

    :param arr_2d: ndarray (2d)
        Array the image to be created from.
    :param filename: string
        Absolute path to created image.
    :return: string
        filename
    """

    print('create_image_from_2d_array is being executed')

    image_array = np.array(StartClass.norm_2d_array(arr_2d=arr_2d,
                                                    value_min=0,
                                                    value_max=255))
    cv2.imwrite(filename=filename, img=image_array)

    print('create_image_from_2d_array is done')

    return filename


def create_png_image(key):
    """
    Create .png-image from current dicom-file.
    :param key: string
        Absolute path to dicom file
    :return: string
        Absolute path to created image.
    """

    print('create_png_image is being executed')

    # pixel array for current image
    curr_array = create_base_array(key)['base_array']
    # name of image file without extension
    name_of_file_without_extension = os.path.basename(key)[:-4]
    # create png-image
    png_image_path = StartClass.create_image_from_2d_array(arr_2d=curr_array,
                                                           filename='03.PNG_images/%s.png' %
                                                                    name_of_file_without_extension)
    # store path to png image in list
    # self.all_images.append(png_image_path)
    # return self.all_images

    print('create_png_image is done')

    return png_image_path


def create_base_array(self, image_file):

    """
    Read current dicom file and retrieve pixel array.
    Retrieve part of meta data
    and update attribute metadata_dict
    :param image_file: string
        Absolute path to current image.
    :return: dict
        Key: 'base_array' : Value: pixel array of current image;
        Key: 'meatdata_subdict' : Value: dict of specified metadata;
        Key: 'whole_dcm' : Value: Dataset object of current dicom.
    """

    print('create_base_array is being executed')

    # if we handle with dicom-file
    if os.path.basename(image_file)[-4:] == '.dcm':
        try:
            # create data element object from dicom
            image_dcm = pydicom.dcmread(image_file, force=True)
        except:
            print('\n\n\nThere is a problem with the file: ')
            print(image_file)
        gc.collect()
        _array = image_dcm.pixel_array
        # self.metadata_subdict = StartClass.create_dataset_dictionary(
        #     list_of_indices=self.metadata_tags_list,
        #     dataset_dicom=image_dcm
        # )
        # metadata_subdict = self.metadata_subdict
        # self.metadata_dict.update({image_file: self.metadata_subdict})

    # if we handle file with another file-extension
    else:
        # read image as list with PIL-library
        img = Image.open(image_file)
        # convert list into numpy-array
        _array = np.array(img)
        # if we have colored image
        if len(self.array.shape) > 2:
            _array = rgb2gray(_array)
        # self.metadata_subdict = {'undefined': 'undefined'}
        # metadata_subdict = {'undefined': 'undefined'}

        # if the image is not a dicom, store 'undefined' in metadata_dict
        self.metadata_dict.update({image_file: {'undefined_tag': 'undefined'}})
        image_dcm = ''
    # image measurements
    self.px_height = _array.shape[0]
    self.px_width = _array.shape[1]
    # image file base name without extension
    self.basename = os.path.basename(image_file)[:-4]
    # image file base name with extension
    self.basename_w_ext = os.path.basename(image_file)

    # ret_dict = {'base_array': self.array.astype(np.int16),
    #             'metadata_subdict': metadata_subdict,
    #             'whole_dcm': image_dcm}

    ret_dict = {'base_array': _array.astype(np.int16),
                'whole_dcm': image_dcm}

    print('create_base_array is done')

    return ret_dict


def rgb2gray(rgb):

    """
    If we handle with RGB-image, convert it to grayscale.
    :param rgb: ndarray
        ndarray (3d) of image to be transformed.
    :return: ndarray
        ndarray (2d) of the converted image
    """
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])