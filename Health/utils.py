from django.http import HttpResponseRedirect

def checksession(request):
    try:
        userId = request.session['userId']
        if userId == '':
            return HttpResponseRedirect("../login/")
        else:
            return True
    except:
        return HttpResponseRedirect("../login/")