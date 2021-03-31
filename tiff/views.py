from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
# from django.http import HttpResponse, Http404,JsonResponse
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.parsers import FormParser,MultiPartParser,FileUploadParser,JSONParser
import json
# import requests
# import os
import time

# from urllib.request import urlopen
# from io import BytesIO
# from zipfile import ZipFile
# from subprocess import Popen
# from os import chmod
# from os.path import isfile

import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import os, cv2, json, random, itertools, rasterio, math, time, psutil
import os, json, random, rasterio, math, time

# from tqdm import tqdm
# from IPython.display import SVG
# from tensorflow.keras.utils import plot_model, model_to_dot, to_categorical, Sequence
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.preprocessing import *

from tensorflow.keras.models import Sequential, Model, load_model
# from tensorflow.keras.layers import (Add, Input, Conv2D, Dropout, Activation, BatchNormalization, MaxPooling2D, ZeroPadding2D, AveragePooling2D, Flatten, Dense, Concatenate)
# from tensorflow.keras.optimizers import Adam, SGD
# from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint, Callback, LearningRateScheduler
# from tensorflow.keras.preprocessing.image import ImageDataGenerator
# from tensorflow.keras.initializers import *
# from tensorflow.keras.regularizers import *

# from tensorflow.keras.preprocessing.image import img_to_array, load_img

from .models import TifImage

# import tempfile
from rasterio.io import MemoryFile



indices = {'AnnualCrop': 0, 'Forest': 1, 'HerbaceousVegetation': 2, 'Highway': 3, 'Industrial': 4, 'Pasture': 5, 'PermanentCrop': 6, 'Residential': 7, 'River': 8, 'SeaLake': 9}
bands = {'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'8a':9,'9':10,'10':11,'11':12,'12':13}

key_list = list(indices.keys())
val_list = list(indices.values())

model_test = load_model("deepsight/6bands_v5-5.h5")
model_test.load_weights("deepsight/6bands_weights_v5-5.h5")

def Normalise(arr_band):    
    arr_band = Normalizer().fit_transform(arr_band)
    return arr_band

def obtain_tif_images(path):
	X = []
	# src = rasterio.open(path)
	# src = rasterio.open('F:\\SUMEDH\\BE project\\code\\eurosat_all\\Residential_329.tif')
	with MemoryFile(path) as memfile:
		with memfile.open() as src:
			# print('###',dataset.profile)
			arr_3, arr_4, arr_8 = src.read(bands['3']), src.read(bands['4']), src.read(bands['8']) 
			arr_6, arr_7 = src.read(bands['6']), src.read(bands['7'])
			arr_11 = src.read(bands['11'])

			arr_3 = np.array(arr_3, dtype=np.float32)
			arr_4 = np.array(arr_4, dtype=np.float32)
			arr_6, arr_7 = np.array(arr_6, dtype=np.float32), np.array(arr_7, dtype=np.float32)
			arr_8 = np.array(arr_8, dtype=np.float32)
			arr_11 = np.array(arr_11, dtype=np.float32)

			arr_3 = Normalise(arr_3)
			arr_4 = Normalise(arr_4)
			arr_6, arr_7 = Normalise(arr_6), Normalise(arr_7)
			arr_8 = Normalise(arr_8)
			arr_11 = Normalise(arr_11)

			bands_10_20 = np.dstack((arr_3, arr_4, arr_6, arr_7, arr_8, arr_11))    

			X.append(bands_10_20)
			X = np.array(X)

			return X

class Test(APIView):
	permission_classes = (AllowAny,)
	parser_classes = (MultiPartParser, FormParser, JSONParser)

	def post(self,request):
		data = request.data
		upload = request.FILES['img'].read()
		if upload:
			test_tifs = obtain_tif_images(upload)
			test_pred = model_test.predict(test_tifs)
			test_pred = np.argmax(test_pred, axis=1)
			position = val_list.index(test_pred[0])
			return Response({"class":key_list[position]})
		else:
			return Response({"error":"no image provided"})