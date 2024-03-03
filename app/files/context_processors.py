from django.conf import settings

def static_files(request):
    context = {
        'css': settings.STATIC_URL + 'assets/css/',
        'imgs': settings.STATIC_URL + 'assets/imgs/',
        'js': settings.STATIC_URL + 'assets/js/'
    }
    return context

def template_shortuts(request):
    context = {
        'user': request.user,
        'page': request.resolver_match.url_name
    }
    return context