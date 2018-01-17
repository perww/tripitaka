from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^list/$', views.sutra_index, name='tripitaka_list'),
    url(r'^picked/$', views.pic_show, name='img_lst'),
    url(r'^op/$', views.sutra_op, name='op'),
]
