import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import KFold
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from django.conf import settings
import os
import csv

def normalize(srs, max_pregn_val, min_pregn_val, max_glucose_val, min_glucose_val, max_bp_val, min_bp_val, max_dpf_val, min_dpf_val, max_ins_val, min_ins_val, max_bmi_val, min_bmi_val, max_age_val, min_age_val, max_st_val, min_st_val):
    # print("This is SRS Data = ", type(srs), srs)
    srs.Pregnancies = float((srs.Pregnancies-min_pregn_val)/(max_pregn_val-min_pregn_val))
    srs.Glucose = float((srs.Glucose - min_glucose_val)/(max_glucose_val - min_glucose_val))
    srs.BloodPressure = float((srs.BloodPressure - min_bp_val)/(max_bp_val - min_bp_val))
    srs.DiabetesPedigreeFunction = float((srs.DiabetesPedigreeFunction - min_dpf_val)/(max_dpf_val - min_dpf_val))
    srs.Insulin = float((srs.Insulin - min_ins_val)/(max_ins_val - min_ins_val))
    srs.BMI = float((srs.BMI - min_bmi_val)/(max_bmi_val - min_bmi_val))
    srs.Age = float((srs.Age - min_age_val)/(max_age_val - min_age_val))
    srs.SkinThickness = float((srs.SkinThickness - min_st_val)/(max_st_val - min_st_val))
    return srs

def create_and_fit_svm(train, features_test):
    parameters = {'kernel':('linear', 'rbf', 'poly'), 'C':[1, 5, 10, 0.1], 'gamma': ['auto', 'scale']}
    svc = svm.SVC()
    clf = GridSearchCV(svc, parameters)
    size = len(train)
    labels = train.Outcome
    # Choosing only Pregnancies, Glucose, BloodPressure, dpf, insulin and bmi as features
    features = pd.DataFrame(train.iloc[:, [1,2,4,5,6,7]])
    clf.fit(features, labels)
    pred = clf.predict(features_test.iloc[0:1])
    print("All Features Test = ", features_test.iloc[:1], pred)
    return pred