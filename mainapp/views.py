from django.shortcuts import render
from django.http import HttpResponse
import pypugjs
from pypugjs.ext.django.compiler import enable_pug_translations

enable_pug_translations()




# Create your views here.


def get_index(request):
    return render(request,'index.html')

def get_hello(request):
    return render(request,'hello.pug')



