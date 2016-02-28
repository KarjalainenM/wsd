from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^confirm/(?P<activation_key>\w+)/', views.register_confirm, name="register_confirm"),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^logout/$', views.user_logout, name='user_logout'),

]