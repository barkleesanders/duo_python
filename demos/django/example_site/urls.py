from django.urls import include, re_path as url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin
admin.autodiscover()

from example_site.views import (private, public, duo_private,
    duo_private_manual, profile,
)
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', private),
    url(r'^private/$', private),
    url(r'^public/$', public),
    url(r'^duo_private/$', duo_private),
    url(r'^duo_private_manual/$', duo_private_manual),
    url(r'^accounts/profile/$', profile),
    url(r'^accounts/login', LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^', include('duo_app.urls')),
]

urlpatterns += staticfiles_urlpatterns()
