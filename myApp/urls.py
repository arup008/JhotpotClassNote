from django.conf.urls import url
from django.views import generic

from myApp import views

app_name = 'myApp'

urlpatterns = [
    url(r'home$', views.home , name='home'),
    url(r'registration$', views.registration , name='registration'),
    url(r'login$', views.login , name='login'),
    url(r'logout$', views.logout , name='logout'),
    url(r'deptPage$', views.deptPage , name='deptPage'),
    url(r'termPage$', views.termPage , name='termPage'),
    url(r'coursePage$', views.coursePage , name='coursePage'),
    url(r'Lecture$', views.Lecture , name='Lecture'),
    url(r'showPdf$', views.showPdf , name='showPdf'),
    url(r'SortBy$', views.SortBy , name='SortBy'),
    url(r'uploadBook$', views.uploadBook , name='uploadBook'),
    url(r'VoteChange$', views.VoteChange , name='VoteChange'),
    url(r'validateLogin$', views.validateLogin , name='validateLogin'),
    url(r'addEntry', views.addEntry , name='addEntry'),
    url(r'goBackToWhereYouEnded', views.goBackToWhereYouEnded , name='goBackToWhereYouEnded'),
    url(r'SendUserName', views.SendUserName , name='SendUserName'),
    url(r'UserProfile$', views.UserProfile , name='UserProfile'),
    url(r'ChangeInfo', views.ChangeInfo , name='ChangeInfo'),
    url(r'UpdateInterest', views.UpdateInterest , name='UpdateInterest'),
    url(r'deletePdf', views.deletePdf , name='deletePdf'),
    url(r'train', views.trainMachine , name='train'),
    url(r'VoteUpdate', views.VoteUpdate , name='VoteUpdate'),
]