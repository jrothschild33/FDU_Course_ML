# -*- coding: gbk -*-
# author: �ܼ��

# �������õĿ�
import sys
import csv
import numpy as np
import pandas as pd
import seaborn as sns
from math import sqrt
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime
from sklearn import metrics
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression

def readMyFile():   # ��ȡ���ݲ�����ȱֵ
    train = pd.read_csv('train.csv', parse_dates=['Date'])
    test = pd.read_csv('test.csv')
    train.replace(['NR'], [0.0], inplace=True)
    test.replace(['NR'], [0.0], inplace=True)
    return train, test

def myStandardize(file):                                                    # ����ֵ����:��һ��
    cols = list(file.columns)                                               # ��ȡԭ�ļ�������
    vals = []                                                               # ׼�����б�����һ���������
    for i in cols[2:]:                                                      # ��ԭ�ļ���2�к�ʼ����
        x = file.loc[:, i]                                                  # ѡ�е�i��
        new_x = list(preprocessing.scale(x))                                # ���й�һ����Standardize��
        vals.append(new_x)                                                  # ����һ��������䵽vals�б���
    vals = np.array(vals).transpose()                                       # ����һ�����б�ת����array��ת��
    vals = pd.DataFrame(vals)                                               # ����һ���õ���array���dataframe
    cols_id = file.iloc[:, :2]                                              # ��ȡԭ�ļ���ǰ2�б������
    new_file = pd.merge(cols_id, vals, left_index=True, right_index=True)   # ����һ���������źϲ����±�
    return new_file                                                         # �鿴��һ����������ݱ�


def extractFeaLab(file_1, file_2, file_3):                                  # ��ȡѵ��feature��ѵ��label������feature
    my_indexs1 = file_1.iloc[:, 0].drop_duplicates()
    my_indexs2 = file_3.iloc[:, 0].drop_duplicates()
    train_X = []
    train_Y = []
    test_X = []
    for id in my_indexs1:
        fea_array1 = np.array(file_1[file_1.iloc[:, 0] == id].iloc[:, 2:], dtype=np.float32)
        lab_array1 = np.array(file_2[file_2.iloc[:, 0] == id].iloc[:, 2:], dtype=np.float32)
        for hour in range(24 - 8):
            fea = fea_array1[:, hour:hour + 8].flatten()                    # ��arrayƽ̹������ά��
            label = lab_array1[9, hour + 8].flatten()                       # ��arrayƽ̹������ά��
            train_X.append(fea)
            train_Y.append(label)

    for id in my_indexs2:
        fea_array2 = np.array(file_3[file_3.iloc[:, 0] == id].iloc[:, 2:], dtype=np.float32)
        fea2 = fea_array2.flatten()                                         # ��arrayƽ̹������ά��
        test_X.append(fea2)

    train_X_ = np.array(train_X)
    train_Y_ = np.array(train_Y)
    test_X_ = np.array(test_X)
    # print(train_X_.shape)                       # (16*240=3840,18*8=144)����new_train�õ�3840��144ά����
    # print(train_Y_.shape)                       # (3840,1)����train�õ�3840��PM2.5ԭԤ��ֵ
    # print(test_X_.shape)                        # (240,18*8=144)����240�����������������Ԥ��test�е�PM2.5ֵ
    return train_X_, train_Y_, test_X_

def myLinearReg(train_X_, train_Y_,test_X_):    # ��ѵ������ѵ��ģ�ͣ�������16:1��֤��������֤������RMSE
    X_train, X_test, y_train, y_test = train_test_split(train_X_, train_Y_, test_size=240 / 3840, random_state=123)

    print('ѵ�������Լ�����:')
    print(' X_train.shape={}\n y_train.shape ={}\n X_test.shape={}\n y_test.shape={}'
          .format(X_train.shape, y_train.shape, X_test.shape, y_test.shape))

    linreg = LinearRegression()
    model = linreg.fit(X_train, y_train)
    print('ģ�Ͳ���:\n', model)
    print('ģ�ͽؾ�:\n', linreg.intercept_)
    print('����Ȩ��:\n', linreg.coef_)

    y_pred = linreg.predict(X_test)
    sum_mean = 0
    for i in range(len(y_pred)):
        sum_mean += (y_pred[i] - y_test[i]) ** 2
    sum_erro = np.sqrt(sum_mean / len(y_pred))
    print("RMSE(����֤����):", sum_erro)

    # ������֤��Ԥ�����
    plt.figure()
    plt.plot(range(len(y_pred)), y_pred, 'b', linestyle='--', label="predict")
    plt.plot(range(len(y_pred)), y_test, 'r', linestyle='solid', label="test")
    plt.legend(loc = "best")
    plt.xlabel("Number of test data")
    plt.ylabel('PM2.5')
    plt.show()

    # ��ѵ���õ�ģ������test�����Ͻ���Ԥ��
    y_pred2 = linreg.predict(test_X_)

    # ����Ԥ�����
    plt.figure()
    plt.plot(range(len(y_pred2)), y_pred2, 'g', linestyle='--', label="Real predict")
    plt.legend(loc="best")
    plt.xlabel("id")
    plt.ylabel('Real predict PM2.5')
    plt.show()

    # ������洢���ݵ�sampleSubmission.csv
    result = pd.DataFrame(y_pred2)
    result.columns = ['values']
    id_names = []
    for i in range(len(result)):
        id_names.append('id_%d' % i)
    result.index = id_names
    result.index.name = 'id'
    result.to_csv('sampleSubmission.csv')