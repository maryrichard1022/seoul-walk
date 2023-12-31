# Created or modified on May 2022
# Author: 임일
# Surprise - Neighbor size 비교

import numpy as np
import pandas as pd

# 필요한 Surprise 알고리즘 불러오기
from surprise import BaselineOnly 
from surprise import KNNWithMeans
from surprise import SVD
from surprise import SVDpp
from surprise import NMF
from surprise import Dataset
from surprise import accuracy
from surprise import Reader
from surprise.model_selection import cross_validate
from surprise.model_selection import train_test_split

# MovieLens 100K 데이터 불러오기
data = Dataset.load_builtin('ml-100k')

# Train/Test 분리 
trainset, testset = train_test_split(data, test_size=0.25)

##### (1)

# 다양한 Neighbor size 비교 
result = []
for neighbor_size in (10, 20, 30, 40, 50, 60):
    algo = KNNWithMeans(k=neighbor_size, sim_options={'name':
           'pearson_baseline', 'user_based': True})
    algo.fit(trainset)
    predictions = algo.test(testset)
    result.append([neighbor_size, accuracy.rmse(predictions)])
result
