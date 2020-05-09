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

'1. ����׼�� ============================================================================'

# 1. ����׼��
# 1.1 ��������
def import_my_train_file(file):
    # ��������
    lines = np.loadtxt(file, delimiter=',', dtype='str')
    print('���ݼ���С:', lines.shape[0] - 1)
    print('���ݼ�����:', lines.shape[1] - 1)
    print('���ݼ������б�:', lines[0])

    # ת��ΪDataFrame
    data = pd.DataFrame(lines[1:], columns=lines[0])

    # �鿴��������
    quant_var = list(data.iloc[:, [0, 2, 4, 10, 11, 12]].columns)
    print('���������У�', len(quant_var), '��')
    print('��������Ϊ��', quant_var)
    print('��������������\n', data.iloc[:, [0, 2, 4, 10, 11, 12]].astype('float').describe())

    # �鿴���Ա���
    quali_var = list(data.iloc[:, [1, 3, 5, 6, 7, 8, 9, 13]].columns)
    print('���������У�', len(quali_var), '��')
    print('��������Ϊ��', quali_var)
    print('��������������\n', data.iloc[:, [1, 3, 5, 6, 7, 8, 9, 13]].describe())

    # �Ա����˳����е���
    my_cols = list(data.columns)[:-1]
    my_cols.insert(0, 'income')
    data = data[my_cols]

    return data, lines, quant_var, quali_var


# 1.2 ���ݴ���ȱʧֵ����������������һ���������Ա���ת��Ϊ�Ʊ���
def clean_my_data(data, quant_var, quali_var):
    # �鿴ÿ�������Ƿ���ȱʧֵ��û��ȱʧֵ����" ��"���д���
    # data.info()

    # ʹ���������" ��"
    imp_mode = SimpleImputer(missing_values=' ?', strategy='most_frequent')
    data['workclass'] = imp_mode.fit_transform(np.array(data['workclass']).reshape(-1, 1))

    # �Զ�����������һ������
    data[quant_var] = MinMaxScaler().fit_transform(data[quant_var])

    # ���Ա���(���ˮƽ�����Ʊ�������8�����Ա������������õ�101������
    dummy = pd.get_dummies(data.loc[:, quali_var])

    # ��incomeһ�л�Ϊ0-1�ͱ���
    data['income'] = data['income'].map({' <=50K': 0, ' >50K': 1})

    # ������õĶ��Ա�����ԭ���ƴ�ӣ���ɾȥԭ���������
    newdata = pd.concat([data, dummy], axis=1)
    newdata.drop(quali_var, axis=1, inplace=True)

    return newdata, dummy


# 1.3 ��ȡ����õ�����
def extract_my_data(newdata):
    # ��ȡ����е�����features����ǩlabels
    x_total = np.array(newdata.iloc[:, 1:].astype('float'))
    y_total = np.array(newdata.iloc[:, :1].astype('float')).flatten()  # ��y_total��Ϊ������

    # ��ǩ���ඨλ
    pos_index = np.where(y_total == 1)  # ��λ������y_totalΪ1������ֵ��pos_index����Ϊtuple��
    neg_index = np.where(y_total == 0)  # ��λ������y_totalΪ0������ֵ��neg_index����Ϊtuple��

    return x_total, y_total, pos_index, neg_index

'2. �߼��ع� ============================================================================'

# 2. �߼��ع�ģ��
# 2.1 ����������µ�ģ��
def my_logi_regression(x_total, y_total):
    # ѵ��ģ��
    # ʵ����lr_clf��������ʾ�߼��ع�ģ��
    lr_clf = linear_model.LogisticRegression()
    # ����fit����������ѵ������x_total, y_total����ģ�ͽ���ѵ��
    lr_clf.fit(x_total, y_total)
    # coef_[0]��ģ�Ͳ���w_i
    print(lr_clf.coef_[0])
    # intercept_��ģ�ͽؾ���b
    print(lr_clf.intercept_)

    # ʹ��ģ��Ԥ��
    # ����predict��������x_total����ѵ���õ�ģ�ͣ��õ�Ԥ���ǩy_pred
    y_pred = lr_clf.predict(x_total)
    # ��y_pred == y_total��Ϊ1������Ϊ0���������ֵ����Ϊģ��׼ȷ��
    print('׼ȷ��(δ����):', (y_pred == y_total).mean())


# 2.2 ����������µ�ģ��: �ֱ���L1��L2���򻯣�����ͼѡ�����Ų���
def find_best_logi_arg(x_total, y_total):
    l1 = []
    l2 = []
    l1test = []
    l2test = []
    # ����ѵ���������Լ���7��3��
    Xtrain, Xtest, Ytrain, Ytest = train_test_split(x_total, y_total, test_size=0.3, random_state=420)

    for i in np.linspace(0.05, 1, 19):
        lrl1 = LR(penalty="l1", solver="liblinear", C=i, max_iter=1000)
        lrl2 = LR(penalty="l2", solver="liblinear", C=i, max_iter=1000)

        lrl1 = lrl1.fit(Xtrain, Ytrain)
        l1.append(accuracy_score(lrl1.predict(Xtrain), Ytrain))
        l1test.append(accuracy_score(lrl1.predict(Xtest), Ytest))

        lrl2 = lrl2.fit(Xtrain, Ytrain)
        l2.append(accuracy_score(lrl2.predict(Xtrain), Ytrain))
        l2test.append(accuracy_score(lrl2.predict(Xtest), Ytest))

    graph = [l1, l2, l1test, l2test]
    color = ["green", "black", "lightgreen", "gray"]
    label = ["L1", "L2", "L1test", "L2test"]

    # ����ѧϰͼ
    # ���˵����ѡ��L1���򻯣�����ǿ�ȵ���Cѡ��0.8��������ģ��Ч�����
    plt.figure(figsize=(6, 6))
    for i in range(len(graph)):
        plt.plot(np.linspace(0.05, 1, 19), graph[i], color[i], label=label[i])
    plt.legend(loc=4)
    plt.show()

# 2.3 �������ģ��
def my_best_logi_model(newdata, x_total, y_total):
    # L1����ѵ��ģ��
    lrl1 = LR(penalty="l1", solver="liblinear", C=0.8, max_iter=1000)
    lrl1 = lrl1.fit(x_total, y_total)
    print('ģ��׼ȷ�ȣ�', accuracy_score(lrl1.predict(x_total), y_total))
    print('ģ��ϵ����\n', lrl1.coef_)
    print('��ά������У�', (lrl1.coef_ != 0).sum(axis=1), '��')

    # �ҳ�ϵ�����Ĳ�������Ϊ�Խ��Ӱ�����Ĳ�����
    print('�Խ��Ӱ�����Ĳ���Ϊ:', newdata.columns[lrl1.coef_.argmax() + 1])
    print('�Խ��Ӱ�����Ĳ�����ϵ��Ϊ:', lrl1.coef_.flatten()[lrl1.coef_.argmax()])
    return lrl1


'3. Ԥ���� ============================================================================'

# 3.1 ������Լ����ݣ������д���

def process_my_test_file(file, quant_var, quali_var, dummy):
    # ����test���ݼ����������ݴ���
    lines = np.loadtxt(file, delimiter=',', dtype='str')
    print('���Լ����ݴ�С:', lines.shape[0] - 1)

    # ת��ΪDataFrame
    data = pd.DataFrame(lines[1:], columns=lines[0])

    # ʹ���������" ��"
    imp_mode = SimpleImputer(missing_values=' ?', strategy='most_frequent')
    data['workclass'] = imp_mode.fit_transform(np.array(data['workclass']).reshape(-1, 1))

    # �Զ�����������һ������
    data[quant_var] = MinMaxScaler().fit_transform(data[quant_var])

    # ���Ա���(���ˮƽ�����Ʊ�������8�����Ա������������õ�100������������һ��������Ҫ��һ������
    dummy2 = pd.get_dummies(data.loc[:, quali_var])

    # �������������Ƿ�ȱ��������
    if len(dummy2.columns) != len(dummy.columns):
        testls = []
        for i in list(dummy.columns):
            if i in list(dummy2.columns):
                pass
            else:
                testls.append(i)
        # ���ȱʧ����ȱʧ����ԭ��������������������������������ԭ������ͬ����λ��
        for i in range(len(testls)):
            dummy2.insert(
                # ��ȡȱʧԪ����ԭ�б��е�����ֵ
                list(dummy.columns).index(testls[i]),
                # �����������ԭ���ݵ�ָ���в���ȱʧ��
                testls[i], dummy[testls[i]]
            )

    # ������õĶ��Ա�����ԭ���ƴ�ӣ���ɾȥԭ���������
    newdata = pd.concat([data, dummy2], axis=1)
    newdata.drop(quali_var, axis=1, inplace=True)

    # ������õ�����ת��Ϊarray��ʽ
    x_test = np.array(newdata.astype('float'))

    return x_test

# 3.2 ������õ���������ѵ���õ�ģ�ͣ��õ�Ԥ����

def pred_my_data(lrl1, x_test):
    y_test_pred = lrl1.predict(x_test)
    # ��y_test_pred��������csv
    y_test_pred = pd.DataFrame(y_test_pred)
    y_test_pred.columns = ['label']
    y_test_pred.index.name = 'id'
    y_test_pred.to_csv('submission_LR.csv')

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
    print('2. �߼��ع�ģ��:')
    print('2.1 ����������µ�ģ��:')
    print('-----------------------------------------------------------------------------')
    my_logi_regression(x_total, y_total)
    print('2.2 ����������µ�ģ��:�ֱ���L1��L2���򻯣�����ͼѡ�����Ų���')
    print('-----------------------------------------------------------------------------')
    find_best_logi_arg(x_total, y_total)
    print('2.3 �������ģ��:')
    print('-----------------------------------------------------------------------------')
    lrl1 = my_best_logi_model(newdata, x_total, y_total)
    print('3.1 ������Լ����ݣ������д���:')
    print('-----------------------------------------------------------------------------')
    x_test = process_my_test_file('test.csv', quant_var, quali_var, dummy)
    print('3.2 ������õ���������ѵ���õ�ģ�ͣ��õ�Ԥ����:"submission_LR.csv"')
    print('-----------------------------------------------------------------------------')
    pred_my_data(lrl1, x_test)