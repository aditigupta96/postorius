from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from postorius.auth.decorators import list_owner_required
from postorius.models import EssaySubscribe

@login_required
@list_owner_required
def EssayList(request,list_id,email):
    list_essay = EssaySubscribe.objects.filter(list_id=list_id, email=email).order_by('-date')
    return render(request , 'postorius/lists/application.html', {'object':list_essay})