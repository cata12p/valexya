def static_files(request):
    context = {
        'css': 'assets/css/',
        'imgs': 'assets/imgs/',
        'js': 'assets/js/'
    }
    return context