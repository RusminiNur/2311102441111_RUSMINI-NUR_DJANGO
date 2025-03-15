from django.shortcuts import render


def home(request):
    template_name = 'portfolio/home.html'
    context = {
        'title': 'Akhmad Qasim',
        'description': 'Bukan developer rumah',
        'body': 'Halaman Utama'
    }
    return render(request, template_name, context)