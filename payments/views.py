from django.shortcuts import render

def main_all(request):
    #View for all apps

    if request.method == "POST":
        return render(request, 'main.html')

    return render(request, 'main.html')
    