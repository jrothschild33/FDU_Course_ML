# -*- coding: gbk -*-
# author: �ܼ��

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression as LR
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import linear_model
from logistic import import_my_train_file, clean_my_data, extract_my_data, process_my_test_file

def cal_z_value(lines, x_total, y_total, pos_index, neg_index):
    # ����N1��N2:
    N1 = np.array(pos_index).shape[1]
    N2 = np.array(neg_index).shape[1]
    print('�������50K��(N1)��', N1, '��')
    print('����С��50K��(N2)��', N2, '��')

    # ����P(C1)��P(C2):
    prob_c1 = np.array(pos_index).shape[1] / (lines.shape[0] - 1)
    prob_c2 = np.array(neg_index).shape[1] / (lines.shape[0] - 1)
    print('���������50K��P(C1):', prob_c1)
    print('������С��50K��P(C2):', prob_c2)

    # �����ֵmu1��mu2
    mu1 = x_total[pos_index].mean(axis=0)
    mu2 = x_total[neg_index].mean(axis=0)
    print('��ֵmu1(����):', mu1)
    print('��ֵmu2(����):', mu2)

    # ����Э�������1��Э�������2
    covar1 = np.dot(np.transpose((x_total[pos_index] - mu1)), (x_total[pos_index] - mu1)) / np.array(pos_index).shape[1]
    covar2 = np.dot(np.transpose((x_total[neg_index] - mu1)), (x_total[neg_index] - mu1)) / np.array(neg_index).shape[1]
    covar = (prob_c1 * covar1) + (prob_c2 * covar2)

    # ����zֵ
    w = np.dot((mu1 - mu2), np.linalg.inv(covar)).reshape(-1, 1)
    b = (np.dot(np.dot(mu1, np.linalg.inv(covar)), np.transpose(mu1)) \
         - np.dot(np.dot(mu2, np.linalg.inv(covar)), np.transpose(mu2))) / 2 \
        + np.log(N1 / N2)
    z = np.dot(x_total, w) + b

    # ���õ���zֵ����ΪԤ����
    z = z.flatten()
    y_pred = []
    for i in z:
        if i > 0:
            y_pred.append(1)
        else:
            y_pred.append(0)

    # ��ѵ�����ϼ���׼ȷ��
    y_pred = np.array(y_pred)
    print('׼ȷ��(ԭ����):', (y_pred == y_total).mean())

    return w,b

def cal_test_pred(w,b,x_test):
    # ��x_test������������ѵ���õ���z���̣��õ�y_test_pred
    z = np.dot(x_test, w) + b
    z = z.flatten()
    y_test_pred = []
    for i in z:
        if i > 0:
            y_test_pred.append(1)
        else:
            y_test_pred.append(0)
    # ��y_test_pred��������csv
    y_test_pred = np.array(y_test_pred, dtype='float')
    y_test_pred = pd.DataFrame(y_test_pred)
    y_test_pred.columns = ['label']
    y_test_pred.index.name = 'id'
    y_test_pred.to_csv('submission_PGM.csv')

if __name__ == '__main__':
    print('1.����׼��:')
    print('-----------------------------------------------------------------------------')
    print('1.1 ��������:')
    print('-----------------------------------------------------------------------------')
    data, lines, quant_var, quali_var = import_my_train_file('train.csv')
    print('1.2 ���ݴ�������ȱʧֵ������������һ�������Ա���ת��Ϊ�Ʊ���:')
    print('-----------------------------------------------------------------------------')
    newdata, dummy = clean_my_data(data, quant_var, quali_var)
    print('1.3 ��ȡ����õ�����:')
    print('-----------------------------------------------------------------------------')
    x_total, y_total, pos_index, neg_index = extract_my_data(newdata)
    print('2. ��������ģ��:')
    print('2.1 ������õ��������룬����zֵ:')
    print('-----------------------------------------------------------------------------')
    w, b = cal_z_value(lines, x_total, y_total, pos_index, neg_index)
    print('2.2 ������Լ����ݣ������д���:')
    print('-----------------------------------------------------------------------------')
    x_test = process_my_test_file('test.csv', quant_var, quali_var, dummy)
    print('2.3 ������õ���������ѵ���õ�ģ�ͣ��õ�Ԥ����:"submission_PGM.csv"')
    print('-----------------------------------------------------------------------------')
    cal_test_pred(w, b, x_test)