from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class AdminRequiredMixin(object):
    @classmethod
    def as_view(self, *args, **kwargs):
        view = super(AdminRequiredMixin, self).as_view(*args, **kwargs)
        return staff_member_required(view)

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super(AdminRequiredMixin, self).dispatch(request,
                                                            *args, **kwargs)
        raise Http404


class LoginRequiredMixin(object):
    @classmethod
    def as_view(self, *args, **kwargs):
        view = super(LoginRequiredMixin, self).as_view(*args, **kwargs)
        return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request,
                                                        *args, **kwargs)


class CacheMixin(object):
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(
            super(CacheMixin, self).dispatch)(*args, **kwargs)
