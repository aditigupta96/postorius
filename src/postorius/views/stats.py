import datetime
import requests

from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import View
from postorius.auth.decorators import (
    list_owner_required, list_moderator_required)
from postorius.models import UnsubscriberStats,List
from postorius.forms import UnsubscriberStatsForm

@login_required
@list_owner_required
def stats(request,list_id):
    if request.method == 'POST':
        form = UnsubscriberStatsForm(request.POST)
        if form.is_valid():
            startdate = request.POST.get('start_date')
            enddate = request.POST.get('end_date')
            list_stats = UnsubscriberStats.objects.filter(list_id = list_id , date__range=[startdate, enddate]).order_by('-date')
            list_stats = list(set(list_stats))

            stats_member_mgt_page = [stat for stat in list_stats if stat.channel == 'Member mgt page']
            stats_members_option_page = [stat for stat in list_stats if stat.channel == 'Members option page']
            stats_admin_mass_unsubscription = [stat for stat in list_stats if stat.channel == 'Admin mass Unsubscription']
            stats_disabled = [stat for stat in list_stats if stat.channel == 'Disabled']

            # Number of unique subject lines
            # Use of hyperkitty api
            base_url = settings.HYPERKITTY_API_URL

            list_id = list_id.split('.')
            list_id = list_id[0] + '@' + list_id[1] + '.' +list_id[2]

            url = base_url + list_id + '/' + 'emails/'+ '?format=json'
            Response = requests.get(url)

            json = Response.json()

            # Change type of startdate and enddate
            startdate = datetime.strptime(startdate,'%Y-%m-%d')
            enddate = datetime.strptime(enddate,'%Y-%m-%d')

            for item in json:
            	item['date'] = datetime.strptime(item['date'],'%Y-%m-%dT%H:%M:%SZ')

            subject_list = [item for item in json if item['date'] <= enddate and item['date'] >= startdate]
            unique_subject_list = {x['subject']:x for x in subject_list}.values()
            
            # Number of subscribers that posted

            emails_url = base_url + list_id + '/' + 'emails/'
            emails_Response = requests.get(emails_url)

            emails_json = emails_Response.json()

            for item in emails_json:
                item['date'] = datetime.strptime(item['date'],'%Y-%m-%dT%H:%M:%SZ')
		       
            emails_subject_list = [item for item in emails_json if item['date'] <= enddate and item['date'] >= startdate]
		    #emails_subject_list = [item for item in emails_subject_list if item['date'].month == month]

            emails_dict = {}

            for i in emails_subject_list:
                emails_dict[i['subject']] = []

            for i in emails_subject_list:
                emails_dict[i['subject']].append(i['sender']['name'])

            for i in emails_subject_list:
                emails_dict[i['subject']] = set(emails_dict[i['subject']])

            count = 0
            for i in emails_dict:
                count += len(emails_dict[i])

            return render(request , 'postorius/lists/stats.html', {'list_stats':list_stats,
                          'stats_member_mgt_page':stats_member_mgt_page, 
                          'stats_members_option_page': stats_members_option_page,
                          'stats_admin_mass_unsubscription':stats_admin_mass_unsubscription, 'stats_disabled':stats_disabled,
                          'unique_subject_list':unique_subject_list,'emails_count':count})

    else:
        form = UnsubscriberStatsForm()
        list_id = list_id
        return render(request, 'postorius/lists/stats_form.html', {'form': form,'list_id':list_id})

# class statsDeleteView(View):
#     template_name = 'postorius/lists/delete_stats.html'
#     def get(self,request,list_id):
#        list_stats = UnsubscriberStats.objects.filter(list_id=list_id)
#        list_stats.delete()

#        return render(request , self.template_name)
