import logging

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from website.core.auth import recaptcha
from website.core.session import SESSION_KEY_POST_SIGN_IN_REDIRECT, SESSION_KEY_RESERVATION_ID
from website.forms.user.sign_in import UsernamePasswordForm, ReservationCodeForm
from website.models.reservation import Reservation
from website.views.decorators.auth import require_unauthenticated

logger = logging.getLogger(__name__)


@require_unauthenticated
def index(request):
    redirect_on_success = 'redirect' in request.GET and \
                          request.GET['redirect'] == "true" and \
                          SESSION_KEY_POST_SIGN_IN_REDIRECT in request.session
    return render(request, "user/sign_in/index.html", {
        'page_title': 'Sign in',
        'redirect': redirect_on_success
    })


@require_unauthenticated
def reservation(request):
    recaptcha_action = recaptcha.RECAPTCHA_ACTION_SIGN_IN_RESERVATION
    redirect_on_success = 'redirect' in request.GET and \
                          request.GET['redirect'] == "true" and \
                          SESSION_KEY_POST_SIGN_IN_REDIRECT in request.session
    if not redirect_on_success and SESSION_KEY_POST_SIGN_IN_REDIRECT in request.session:
        del request.session[SESSION_KEY_POST_SIGN_IN_REDIRECT]
        request.session.modified = True
    if request.method == 'POST':
        form = ReservationCodeForm(request.POST)
        validation_error = None
        if form.is_valid():
            try:
                recaptcha.validate_recaptcha_token(request, form.cleaned_data['recaptcha_token'], recaptcha_action)
                reservation_code = form.cleaned_data['reservation_code']
                try:
                    res = Reservation.objects.filter(access_code__iexact=reservation_code).only('user', 'id').get()
                except Reservation.DoesNotExist:
                    raise ValidationError("Invalid reservation code")

                request.session[SESSION_KEY_RESERVATION_ID] = res.id
                request.session.modified = True

                success_view = determine_sign_in_success_view(request, "reservation")
                if res.user is None:
                    return redirect("reservation/activate")
                else:
                    login(request, res.user)
                    return redirect(success_view)
            except ValidationError as e:
                validation_error = e
        if settings.DEBUG:
            logger.debug("reservation login failed with form data '%s'" % form.cleaned_data)
        form.clear_sensitive_form_data()
        if validation_error is not None:
            form.add_error(None, validation_error.message)
    else:
        form = ReservationCodeForm()
    return render(request, "user/sign_in/reservation/index.html", {
        'page_title': 'Sign in - Reservation',
        'form': form,
        'redirect': redirect_on_success,
        'recaptcha_action': recaptcha_action
    })


@require_unauthenticated
def user(request):
    recaptcha_action = recaptcha.RECAPTCHA_ACTION_SIGN_IN_USER
    redirect_on_success = 'redirect' in request.GET and \
                          request.GET['redirect'] == "true" and \
                          SESSION_KEY_POST_SIGN_IN_REDIRECT in request.session
    if not redirect_on_success and SESSION_KEY_POST_SIGN_IN_REDIRECT in request.session:
        del request.session[SESSION_KEY_POST_SIGN_IN_REDIRECT]
        request.session.modified = True
    if request.method == 'POST':
        form = UsernamePasswordForm(request.POST)
        validation_error = None
        if form.is_valid():
            try:
                recaptcha.validate_recaptcha_token(request, form.cleaned_data['recaptcha_token'], recaptcha_action)
                target_user = authenticate(request, username=form.cleaned_data['username'],
                                           password=form.cleaned_data['password'])
                if target_user is not None:
                    login(request, target_user)
                    return redirect(determine_sign_in_success_view(request, 'user/profile'))
                else:
                    raise ValidationError("Invalid username or password")
            except ValidationError as e:
                validation_error = e
        if settings.DEBUG:
            logger.debug("user login failed with form data '%s'" % form.cleaned_data)
        form.clear_sensitive_form_data()
        if validation_error is not None:
            form.add_error(None, validation_error.message)
    else:
        form = UsernamePasswordForm()
    return render(request, "user/sign_in/user/index.html", {
        'page_title': 'Sign in - User',
        'form': form,
        'redirect': redirect_on_success,
        'recaptcha_action': recaptcha_action
    })


def determine_sign_in_success_view(request, default_view):
    target_view = default_view
    if SESSION_KEY_POST_SIGN_IN_REDIRECT in request.session:
        target_view = request.session[SESSION_KEY_POST_SIGN_IN_REDIRECT]
        del request.session[SESSION_KEY_POST_SIGN_IN_REDIRECT]
        request.session.modified = True
    return target_view
