import sys;sys.path.append('../')
from Model import GBDT
from Model import XGBoost
from Model import LightGBM
import pandas as pd
from Model.ModelProxy import ModelProxy
from sklearn.metrics import f1_score, roc_curve, auc
import DataLinkSet as DLSet
import datetime
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def get_clf(choice):
    if choice == 'GBDT':
        return GBDT.generate_clf()
    elif choice == 'XGBoost':
        return XGBoost.generate_clf()
    elif choice == 'LightGBM':
        return LightGBM.generate_clf()


def main():
    df_clean_train = pd.read_csv(DLSet.clean_train_link)
    df_clean_test = pd.read_csv(DLSet.clean_test_link)

    # confirm features
    features_used = df_clean_train.columns.difference(['id', 'earliesCreditLine', 'isDefault', 'n2.2', 'n2.3'])

    # state clf
    model_choice = 'GBDT'
    # model_choice = 'XGBoost'
    # model_choice = 'LightGBM'
    model = ModelProxy(clf=get_clf(model_choice))
    pca = PCA(n_components=30)

    # training
    train_X = df_clean_train[features_used].values
    # scaler = StandardScaler().fit(train_X)
    # train_X = scaler.transform(train_X)
    # train_X = pca.fit_transform(train_X)
    train_y = df_clean_train['isDefault'].values

    # add PCA
    model.fit(train_X, train_y)
    model.save(DLSet.model_link % (model_choice, datetime.datetime.today()))

    # evaluate model
    # model = ModelProxy(data_link=DLSet.model_link % ('LightGBM', '2020-09-15 11:45:09.713017'))
    pred_y = model.predict(train_X)
    result = f1_score(train_y, pred_y)
    print('total F1 = {}'.format(result))

    pred_y_prob = model.predict_proba(train_X)[:, 1]
    fpr, tpr, thresholds = roc_curve(train_y, pred_y_prob)
    print('auc is', auc(fpr, tpr))

    # predicting
    test_X = df_clean_test[features_used].values
    # test_X = scaler.transform(test_X)
    # test_X = pca.transform(test_X)

    pred_y_prob = model.predict_proba(test_X)[:, 1]
    id_list = df_clean_test['id'].values
    num = len(id_list)
    with open(DLSet.result_link % datetime.datetime.today(), 'w') as f:
        f.write('id,isDefault\n')
        for i in range(num):
            f.write('%d,%f\n' % (id_list[i], pred_y_prob[i]))


if __name__ == '__main__':
    main()
