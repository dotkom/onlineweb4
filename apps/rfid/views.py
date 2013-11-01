from django.shortcuts import render

def rfid(request):
    return render(request, 'rfid/index.html', {})
