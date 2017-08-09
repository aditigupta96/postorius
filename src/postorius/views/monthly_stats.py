import datetime
import requests

from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from postorius.auth.decorators import list_owner_required
from postorius.models import UnsubscriberStats,List

@login_required
@list_owner_required
def present_month_stats(request,list_id):
    years = []
    months = ['Jan','Feb','March','April','May','June','July','Aug','Sep','Oct','Nov','Dec']

    current_month = datetime.now().month
    current_monthName = months[current_month-1]
    current_year = datetime.now().year

    # Number of unsubscribers through different channels

    list_stats = UnsubscriberStats.objects.filter(list_id = list_id,date__month=current_month).order_by('-date')
    for i in list_stats:
        print i
        print
    list_stats = list(set(list_stats))

    stats_member_mgt_page = [stat for stat in list_stats if stat.channel == 'Member mgt page']
    stats_members_option_page = [stat for stat in list_stats if stat.channel == 'Members option page']
    stats_admin_mass_unsubscription = [stat for stat in list_stats if stat.channel == 'Admin mass Unsubscription']
    stats_disabled = [stat for stat in list_stats if stat.channel == 'Disabled']


    # Number of subscribers posted
    base_url = settings.HYPERKITTY_API_URL

    list_name = list_id.split('.')
    list_name = list_name[0] + '@' + list_name[1] + '.' +list_name[2]

    emails_url = base_url + list_name + '/' + 'emails/'
    emails_Response = requests.get(emails_url)

    emails_json = emails_Response.json()

    emails_years = []

    for item in emails_json:
    	item['date'] = datetime.strptime(item['date'],'%Y-%m-%dT%H:%M:%SZ')
        emails_years.append(item['date'].year)

    emails_years = set(emails_years)

    emails_subject_list = [item for item in emails_json if item['date'].year in emails_years]
    emails_subject_list = [item for item in emails_subject_list if item['date'].month == current_month]

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


    
    # Number of unique subject lines
    # Use of hyperkitty api

    url = base_url + list_name + '/' + 'emails/'+ '?format=json'
    Response = requests.get(url)

    json = Response.json()

    if len(json) > 0:
        for item in json:
            item['date'] = datetime.strptime(item['date'],'%Y-%m-%dT%H:%M:%SZ')
            years.append(item['date'].year)

        years = set(years)
        
        subject_list = [item for item in json if item['date'].year in years]
        unique_subject_list = {x['subject']:x for x in subject_list}.values()

        present_month_subject_list = [item for item in subject_list if item['date'].month == current_month]
        present_month_unique_subject_list = {x['subject']:x for x in present_month_subject_list}.values()

                
        return render(request , 'postorius/lists/monthly_stats.html', {'list_id':list_id,
        	                 'current_year':current_year,
                                'current_monthName':current_monthName,
                                'years':years, 'months':months, 
                                'unique_subject_list':present_month_unique_subject_list,
                                'list_stats':list_stats,
                                'stats_member_mgt_page':stats_member_mgt_page,
                                'stats_members_option_page': stats_members_option_page,
                                'stats_admin_mass_unsubscription':stats_admin_mass_unsubscription, 
                                'stats_disabled':stats_disabled,
                                'emails_count':count})

    else:
        present_month_unique_subject_list = []
        years.append(current_year)

        return render(request , 'postorius/lists/monthly_stats.html', {'list_id':list_id,
        	                 'current_year':current_year,
                                'current_monthName':current_monthName,
                                'years':years, 
                                'months':months, 
                                'unique_subject_list':present_month_unique_subject_list,
                                'list_stats':list_stats,
                                'stats_member_mgt_page':stats_member_mgt_page,
                                'stats_members_option_page': stats_members_option_page,
                                'stats_admin_mass_unsubscription':stats_admin_mass_unsubscription,
                                'stats_disabled':stats_disabled,
                                'emails_count':count})


@login_required
@list_owner_required
def monthly_stats(request,list_id,year,month):
    year = int(year)
    month = int(month)

    list_stats = UnsubscriberStats.objects.filter(list_id = list_id,date__year=year,date__month=month).order_by('-date')
    list_stats = list(set(list_stats))

    stats_member_mgt_page = [stat for stat in list_stats if stat.channel == 'Member mgt page']
    stats_members_option_page = [stat for stat in list_stats if stat.channel == 'Members option page']
    stats_admin_mass_unsubscription = [stat for stat in list_stats if stat.channel == 'Admin mass Unsubscription']
    stats_disabled = [stat for stat in list_stats if stat.channel == 'Disabled']


    base_url = settings.HYPERKITTY_API_URL

    list_name = list_id.split('.')
    list_name = list_name[0] + '@' + list_name[1] + '.' +list_name[2]

    emails_url = base_url + list_name + '/' + 'emails/'
    emails_Response = requests.get(emails_url)

    emails_json = emails_Response.json()

    emails_years = []

    for item in emails_json:
    	item['date'] = datetime.strptime(item['date'],'%Y-%m-%dT%H:%M:%SZ')
        emails_years.append(item['date'].year)

    emails_years = set(emails_years)

    emails_subject_list = [item for item in emails_json if item['date'].year in emails_years]
    emails_subject_list = [item for item in emails_subject_list if item['date'].month == month]

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


    # Number of unique subject lines
    # Use of hyperkitty api

    url = base_url + list_name + '/' + 'emails/'+ '?format=json'
    Response = requests.get(url)

    json = Response.json()

    years = []
    months = ['Jan','Feb','March','April','May','June','July','Aug','Sep','Oct','Nov','Dec']

    if len(json) > 0:
        for item in json:
            item['date'] = datetime.strptime(item['date'],'%Y-%m-%dT%H:%M:%SZ')
            years.append(item['date'].year)

        years = set(years)

        subject_list = [item for item in json if item['date'].year == year]
        unique_subject_list = {x['subject']:x for x in subject_list}.values()

        month_subject_list = [item for item in subject_list if item['date'].month == month]
        month_unique_subject_list = {x['subject']:x for x in month_subject_list}.values()

        current_monthName = months[month-1]

        return render(request , 'postorius/lists/monthly_stats.html', {'list_id':list_id,
        	                 'current_year':year,
                                'current_monthName':current_monthName,
                                'unique_subject_list':month_unique_subject_list,
                                'years':years, 
                                'months':months, 
                                'list_stats':list_stats,
                                'stats_member_mgt_page':stats_member_mgt_page,
                                'stats_members_option_page': stats_members_option_page,
                                'stats_disabled':stats_disabled,
                                'stats_admin_mass_unsubscription':stats_admin_mass_unsubscription,
                                'emails_count':count})

    else:
        current_month = datetime.now().month
        current_monthName = months[current_month-1]
        current_year = datetime.now().year

        month_unique_subject_list = []
        years.append(current_year)

        return render(request , 'postorius/lists/monthly_stats.html', {'list_id':list_id,
        	                 'current_year':year,
                                'current_monthName':current_monthName,
                                'unique_subject_list':month_unique_subject_list,
                                'years':years, 
                                'months':months,
                                'list_stats':list_stats,
                                'stats_member_mgt_page':stats_member_mgt_page,
                                'stats_members_option_page': stats_members_option_page,
                                'stats_disabled':stats_disabled,
                                'stats_admin_mass_unsubscription':stats_admin_mass_unsubscription,
                                'emails_count':count})
