from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from duo_app import duo_auth


@login_required
@duo_auth.duo_auth_required
def duo_private(request):
    """
    View which requires a login and Duo authentication.
    """
    return render(request, 'private.html', {'secondary': True})


@login_required
def duo_private_manual(request):
    """
    View which requires a login, and manually checks for Duo authentication.
    """
    if not duo_auth.duo_authenticated(request):
        return HttpResponseRedirect(
            '%s?next=%s' % (settings.DUO_LOGIN_URL, request.path))
    return render(request, 'private.html', {'secondary': True})


@login_required
def private(request):
    """
    View which requires a login.
    """
    return render(request, 'private.html', {'secondary': False})


def public(request):
    """
    Public view.
    """
    return HttpResponse('Public content.')


def profile(request):
    """
    View for all Django profiles.
    """
    return HttpResponse('Profile view.')
