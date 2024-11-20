import json
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from .utils import *
from django.conf import settings
from operator import itemgetter
import os
import csv
import pandas as pd
from .predict import * 
import pickle as pkl

# Create your views here.
def home(request):
    return render(request, "home.html", locals())

def about(request):
    return render(request, "about.html", locals())

def contact(request):
    return render(request, "contact.html", locals())

def register(request):
    if request.method == "POST":
        re = request.POST
        rf = request.FILES
        user = User.objects.create_user(username=re['username'], first_name=re['first_name'], last_name=re['last_name'], password=re['password'])
        register = Register.objects.create(user=user, address=re['address'], mobile=re['mobile'], image=rf['image'])
        messages.success(request, "Registration Successful")
        return redirect('signin')
    return render(request, "signup.html", locals())


def update_profile(request):
    if request.method == "POST":
        re = request.POST
        rf = request.FILES
        try:
            image = rf['image']
            data = Register.objects.get(user=request.user)
            data.image = image
            data.save()
        except:
            pass
        user = User.objects.filter(id=request.user.id).update(username=re['username'], first_name=re['first_name'], last_name=re['last_name'])
        register = Register.objects.filter(user=request.user).update(address=re['address'], mobile=re['mobile'])
        messages.success(request, "Updation Successful")
        return redirect('update_profile')
    return render(request, "update_profile.html", locals())


def signin(request):
    if request.method == "POST":
        re = request.POST
        user = authenticate(username=re['username'], password=re['password'])
        if user:
            login(request, user)
            messages.success(request, "Logged in successful")
            return redirect('home')
    return render(request, "signin.html", locals())

    
def admin_signin(request):
    if request.method == "POST":
        re = request.POST
        user = authenticate(username=re['username'], password=re['password'])
        if user.is_staff:
            login(request, user)
            messages.success(request, "Logged in successful")
            return redirect('home')
    return render(request, "admin_signin.html", locals())


def change_password(request):
    if request.method == "POST":
        re = request.POST
        user = authenticate(username=request.user.username, password=re['old-password'])
        if user:
            if re['new-password'] == re['confirm-password']:
                user.set_password(re['confirm-password'])
                user.save()
                messages.success(request, "Password changed successfully")
                return redirect('home')
            else:
                messages.success(request, "Password mismatch")
        else:
            messages.success(request, "Wrong password")
    return render(request, "change_password.html", locals())


def logout_user(request):
    logout(request)
    messages.success(request, "Logout Successfully")
    return redirect('home')


def search_product(request):
    product = []
    dictobj = {'object':[]}
    if request.method == "POST":
        re = request.POST
        name = re['search']
        flipkart_price, flipkart_name, flipkart_image, flipkart_link=flipkart(name)
        amazon_price, amazon_name, amazon_image, amazon_link=amazon(name)
        croma_price, croma_name, croma_image, croma_link=croma(name)
        gadgetsnow_price, gadgetsnow_name, gadgetsnow_image, gadgetsnow_link=gadgetsnow(name)
        reliance_price, reliance_name, reliance_image, reliance_link=reliance(name)
        dictobj["object"].append({'logo':'/static/assets/' + 'img/' + 'flipkart-logo.png', 'price':convert(flipkart_price), 'name':flipkart_name, 'link':flipkart_link, 'image':flipkart_image})
        dictobj["object"].append({'logo':'/static/assets/' + 'img/' + 'amazon-logo.png', 'price':convert(amazon_price), 'name':amazon_name, 'link':amazon_link, 'image':amazon_image})
        dictobj["object"].append({'logo':'/static/assets/' + 'img/' + 'croma-logo.png', 'price':convert(croma_price), 'name':croma_name, 'link':croma_link, 'image':croma_image})
        dictobj["object"].append({'logo':'/static/assets/' + 'img/' + 'gadgetsnow-logo.png', 'price':convert(gadgetsnow_price), 'name':gadgetsnow_name, 'link':gadgetsnow_link, 'image':gadgetsnow_image})
        dictobj["object"].append({'logo':'/static/assets/' + 'img/' + 'reliance-logo.png', 'price':convert(reliance_price), 'name':reliance_name, 'link':reliance_link, 'image':reliance_image})
        data = dictobj['object']
        data = sorted(data, key=itemgetter('price'))
        history = History.objects.create(user=request.user, product=dictobj)
        # messages.success(request, "History Saved")
    return render(request, "search_product.html", locals())

def my_history(request):
    history = History.objects.filter(user=request.user)
    if request.user.is_staff:
        history = History.objects.filter()
    return render(request, "my_history.html", locals())

def all_user(request):
    data = Register.objects.filter()
    return render(request, "all_user.html", locals())

def history_detail(request, pid):
    history = History.objects.get(id=pid)
    product = (history.product).replace("'", '"')
    product = json.loads(str(product))
    product = product['object']
    product = sorted(product, key=itemgetter('price'))
    try:
        user = Register.objects.get(user=history.user)
    except:
        pass
    return render(request, "history_detail.html", locals())


def delete_user(request, pid):
    user = User.objects.get(id=pid)
    user.delete()
    messages.success(request, "User Deleted")
    return redirect('all_user')


def delete_history(request, pid):
    data = History.objects.get(id=pid)
    data.delete()
    messages.success(request, "History Deleted")
    return redirect('my_history')

def dataNormalize(test_data):
    test_data = pd.read_csv(test_data)
    patient_data = pd.read_csv(os.path.join(str(settings.BASE_DIR), 'myapp', 'static', 'diabetespractice.csv'))
    size = len(patient_data)
    print(patient_data.dtypes, size)
    max_pregn = patient_data.Pregnancies.max()
    min_pregn = patient_data.Pregnancies.min()
    max_glucose = patient_data.Glucose.max()
    min_glucose = patient_data.Glucose.min()
    max_bp = patient_data.BloodPressure.max()
    min_bp = patient_data.BloodPressure.min()
    max_dpf = patient_data.DiabetesPedigreeFunction.max()
    min_dpf = patient_data.DiabetesPedigreeFunction.min()
    max_ins = patient_data.Insulin.max()
    min_ins = patient_data.Insulin.min()
    max_bmi = patient_data.BMI.max()
    min_bmi = patient_data.BMI.min()
    max_age = patient_data.Age.max()
    min_age = patient_data.Age.min()
    max_st = patient_data.SkinThickness.max()
    min_st = patient_data.SkinThickness.min()
    
    # Normalizing the data and obtaining the new DataFrame
    patient_data = patient_data.apply((lambda x: normalize(x, max_pregn, min_pregn, max_glucose, min_glucose, max_bp, min_bp, max_dpf, min_dpf, max_ins, min_ins, max_bmi, min_bmi, max_age, min_age, max_st, min_st)), axis='columns')
    test_data = test_data.apply((lambda x: normalize(x, max_pregn, min_pregn, max_glucose, min_glucose, max_bp, min_bp, max_dpf, min_dpf, max_ins, min_ins, max_bmi, min_bmi, max_age, min_age, max_st, min_st)), axis='columns')
    return patient_data, test_data


def predict_data(request):
    if request.method == "POST":
        data = request.POST
        path_model = str(settings.BASE_DIR)+'/FakeNewsDetection/model.pkl'
        with open(path_model,'rb') as file:
            model = pkl.load(file)
        # test with save cntvectoriser
        path_vectorizer = str(settings.BASE_DIR)+'/FakeNewsDetection/cntvectorizer.pkl'
        with open(path_vectorizer,'rb') as file:
            vectorizer = pkl.load(file)
        new_test = [data['content']]
        r = vectorizer.transform(new_test)
        res = model.predict(r)
        print(type(res), type(res[0]), res[0], "Res is here")
        if res[0] == 0:
            output = "Fake"
        else:
            output = "Real"
        search_data = {'content': data['content']}
        History.objects.create(user=request.user, search_data=search_data, output=output)
        messages.success(request, "Prediction Saved")
        # print(patient_data, predData)
    return render(request, "predict_data.html", locals())
    