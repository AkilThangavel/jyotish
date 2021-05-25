import random
import psycopg2
import googlemaps
from urllib.parse import unquote
from .my_scripts.logic import match_all, bdate_time_place_to_degs
from .my_scripts.match3 import match3
from .forms import PersonAddForm, PersonEditForm, PersonMatchForm, SignInForm
from .models import Person, User, Label, MapSession, UserVideoLink
from django.shortcuts import render, redirect, render_to_response
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.forms import Form, ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.http import JsonResponse


from .my_scripts.NO_NEED_f50000 import data as data_50

def get_degrees(request):
    name = request.GET['name']
    bdate = request.GET['bdate'].replace('-', '.')
    btime = request.GET['btime']
    bplace = request.GET['bplace']

    def decdeg2dms(dd):
        mnt, sec = divmod(dd*3600,60)
        deg, mnt = divmod(mnt,60)
        if deg < 0:
            deg = -deg
        return deg, mnt

    person = Person.objects.filter(name=name, bplace=bplace)
    if person:
        person = person[0]
        if person.Su == '':
            KEY = 'AIzaSyASsKRcBk1D1J_oWy7teTjodHQ5N1uOl1M'
            api = googlemaps.Client(key=KEY)
            degs = bdate_time_place_to_degs(api, bdate, btime, bplace)

            context = {
                'Su': round(degs[0], 4),
                'Mo': round(degs[1], 4),
                'Me': round(degs[2], 4),
                'Ma': round(degs[3], 4),
                'Ju': round(degs[4], 4),
                'Ve': round(degs[5], 4),
                'Sa': round(degs[6], 4),
                'Ra': round(degs[7], 4),
                'Ke': round(degs[8], 4),
                'As': round(degs[9], 4)
            }

            for k, v in context.items():
                d, m = decdeg2dms(v)
                context[k] = str(int(d)) + '° ' + str(int(m)) + "'"
        else:
            context = {
                'Su': person.Su,
                'Mo': person.Mo,
                'Me': person.Me,
                'Ma': person.Ma,
                'Ju': person.Ju,
                'Ve': person.Ve,
                'Sa': person.Sa,
                'Ra': person.Ra,
                'Ke': person.Ke,
                'As': person.As
            }
    return JsonResponse(context)

class Load50(TemplateView):
    def get(self, request, **kwargs):
        for i in data_50[Person.objects.all().count():]:
            if Person.objects.filter(name=i[0][:30], bdate=i[1]).exists():
                continue
            else:
                person = Person()
                person.name = i[0][:30]
                person.bdate = i[1]
                person.btime = i[2]
                person.bplace = i[3][:190]
                person.gender = random.choice(['Male', 'Female'])
                person.save()

        return render(request, 'NO_NEED_load50000.html', context=None)

class AdminPanelView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_superuser:
            users = []
            for i in User.objects.filter(is_superuser=False):
                try:
                    p = Person.objects.get(user=i.username)
                    gender = p.gender
                    place = p.bplace
                    time = p.btime
                    date = p.bdate
                    password = p.password
                except:
                    gender = ""
                    place = ""
                    time = ""
                    date = ""
                    password = ""
                finally:
                    users.append([i.first_name, i.username, gender, password, place, time, date])
            return render(request, 'admin_panel.html', context={'users': users})
        else:
            if request.user.is_authenticated:
                return redirect('/index')
            else:
                return redirect('/login')

    def post(self, request, **kwargs):
        form = Form(request.POST)
        if 'autocomplete1' in request.POST:    # Add user
            if form.is_valid:
                name = request.POST['nameAdd']
                username = request.POST['usernameAdd']
                gender = request.POST['genderAdd']
                password = request.POST['passwordAdd']
                place = request.POST['autocomplete1']
                time = request.POST['timeAdd']
                date = request.POST['dateAdd']

                try:
                    user = User.objects.get(username=username)
                    messages.add_message(request, messages.ERROR, 'User with such name already exists')
                except:
                    user = User()
                    user.first_name = name
                    user.username = username
                    user.set_password(password)
                    user.save()

                    person = Person()
                    person.name = name
                    person.bdate = date
                    person.btime = time
                    person.bplace = place
                    person.gender = gender
                    person.user = username
                    person.password = password
                    person.save()

        elif 'autocomplete2' in request.POST:  # Edit user
            if form.is_valid:
                name = request.POST['nameEdit']
                username = request.POST['usernameEdit']
                gender = request.POST['genderEdit']
                password = request.POST['passwordEdit']
                place = request.POST['autocomplete2']
                time = request.POST['timeEdit']
                date = request.POST['dateEdit']

                user = User.objects.get(username=username)
                user.first_name = name
                user.username = username
                user.set_password(password)
                user.save()

                person = Person.objects.get(user=username)
                person.name = name
                person.bdate = date
                person.btime = time
                person.bplace = place
                person.gender = gender
                person.user = username
                person.password = password
                person.save()
        return redirect('/admin_panel')

class AdminSettingsView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_superuser:
            return render(request, 'admin_settings.html', context=None)
        else:
            if request.user.is_authenticated:
                return redirect('/index')
            else:
                return redirect('/login')

    def post(self, request, **kwargs):
        user = User.objects.get(username=request.user.username)
        user.set_password(request.POST['newp'])
        user.save()
        return redirect('/admin_settings')

class MapSessionsView(TemplateView):
    def get(self, request, **kwargs):
        username = request.user.username
        labels = []
        for i in MapSession.objects.filter(user=username):
            labels.append([i.id, i.name, i.date, 'google.com'])
        return render(request, 'map_sessions.html', context={'labels': labels})

class VideosPDFView(TemplateView):
    def get(self, request, **kwargs):
        username = request.user.username
        links = []
        for i in UserVideoLink.objects.filter(user=username):
            links.append([i.name, i.url, i.description])
        return render(request, 'videos.html', context={'links': links})

def ajax_save_session(request):
    index = request.GET['index']
    name = request.GET['name']
    session = MapSession.objects.get(id=index)
    session.name = name
    session.save()
    return JsonResponse({})

def delete_user_video_link(request):
    link_id = int(request.GET['link_id'])
    link = UserVideoLink.objects.get(id=link_id)
    link.delete()
    return JsonResponse({})

def add_user_video_link(request):
    username = request.GET['username'].strip()
    link = UserVideoLink()
    link.username = username
    link.name = ''
    link.url = ''
    link.description = ''
    link.save()
    return JsonResponse({'link_id': str(link.id).strip()})

def edit_video_links(request):
    username = request.GET['username'].strip()
    html = ''
    for link in UserVideoLink.objects.filter(user=username):
        html += '''
        <div class="d-flex video-link mb-1 mt-1">
            <input id="link_name" type="text" class="form-control mr-1" name="" value="{}" placeholder="Name for link">
            <input id="link_url" type="text" class="form-control" name="" value="{}" placeholder="Url">
            <input id="link_id" type="text" name="" value="{}" hidden>
            <textarea class="form-control" id="link_desc">{}</textarea>
            <button onclick="remove_link('{}', this)" class="btn btn-danger" type="button" name="button">x</button>
        </div>
        '''.format(link.name, link.url, str(link.id).strip(), link.description, str(link.id).strip())
    return JsonResponse({'html': html})



def save_video_link(request):
    link_id = int(request.GET['link_id'])
    link_url = request.GET['link_url']
    link_name = request.GET['link_name']
    link_desc = request.GET['link_desc']
    username = request.GET['username']

    link = UserVideoLink.objects.get(id=link_id)
    link.user = username
    link.url = link_url
    link.name = link_name
    link.description = link_desc
    link.save()
    return JsonResponse({})

def ajax_save_labels(request):
    labels = request.GET.getlist('labels[]')
    username = request.GET['user']
    already = request.GET['already']
    labelName = (request.GET['labelname'])
    label_db = Label.objects.filter(**{"user": labelName})
    if label_db:
        label_db = Label.objects.filter(**{"user": labelName})
        label_db.delete()
        for i in labels:
            tc = i.split("_____")
            label = Label(session=str(1), text=tc[0], lat=tc[1], lon=tc[2], user= labelName)
            label.save()
    else:
        for i in labels:
            tc = i.split("_____")
            label = Label(session=str(1), text=tc[0], lat=tc[1], lon=tc[2], user= labelName)
            label.save()
    return JsonResponse({})

def ajax_delete_session(request):
    idx = request.GET['index']
    session = MapSession.objects.get(id=int(idx))
    for i in Label.objects.filter(session=str(idx)):
        i.delete()
    session.delete()
    return JsonResponse({})

def ajax_delete_user(request):
    username = request.GET['username']
    user = User.objects.get(username=username)
    person = Person.objects.get(user=username)
    if user:
        user.delete()
    if person:
        person.delete()
    return JsonResponse({})

def logout_view(request):
    logout(request)
    return redirect('/login')

class SignInView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return redirect('/relocation_map3d?inputSession=')
        else:
            return render(request, 'login.html', context=None)

    @method_decorator(csrf_protect)
    def post(self, request, **kwargs):
        form = SignInForm(request.POST)

        if User.objects.filter(username=request.POST['username']).exists():
            user = User.objects.get(username=request.POST['username'])
            user = authenticate(request, username=user.username, password=request.POST['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user.is_superuser:
                        return redirect('/relocation_map_input')
                    else:
                        return redirect('/relocation_map3d?inputSession=')
                else:
                    messages.error(request, 'Your account is not active, it must be reviewed by admin of the site')
            else:
                messages.error(request, 'You entered incorrect password')
        else:
            messages.error(request, 'User with this username not found')

        return render(request, 'login.html', context=None)

class RelocationMap3dInputView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            context = {
                'sessions': []
            }
            for i in MapSession.objects.filter(user=request.user.username):
                context['sessions'].append([i.name, i.date, i.id])
            return render(request, 'relocation_map_input.html', context=context)
        else:
            return redirect('/login')

class RelocationMap3dView(TemplateView):
    def get(self, request, **kwargs):
        labelName = request.GET['inputName1']
        label_db = Label.objects.filter(**{"user": labelName})
        
        if request.user.is_authenticated:
            context = {
                "polygons": "",
                "user_name": request.user.username
            }

            def dmstodeg(dm):
                d = dm.split(' ')[0][:-1]
                m = dm.split(' ')[1][:-1]
                deg = float(d) + float(m) / 60
                return deg

            if request.method == 'GET':
                form = Form(request.GET)
                if form.is_valid():
                    ses = request.GET['inputSession'].split('    ')
                    if len(ses) == 3:
                        session = MapSession.objects.get(id=int(ses[2]))
                        if session:
                            labels = []
                            for i in Label.objects.filter(session=str(session.id)):
                                labels.append([i.text, i.lat, i.lon])
                            context['labels'] = labels
                            if len(labels) == 0:
                                context['already_yes'] = 'yes'
                            else:
                                context['already_yes'] = ''
                        else:
                            context['labels'] = []
                    #
                    if request.user.is_superuser:
                        name = request.GET['inputName1']
                        ttime = request.GET['time']
                        ddate = request.GET['date'].replace('-', '.')
                        pplace = request.GET['autocomplete1']
                        #
                        KEY = 'AIzaSyASsKRcBk1D1J_oWy7teTjodHQ5N1uOl1M'
                        api = googlemaps.Client(key=KEY)
                        person = Person.objects.filter(name=name, bplace=pplace)[0]
                        person.Su = request.GET['CD_Su']
                        person.Mo = request.GET['CD_Mo']
                        person.Me = request.GET['CD_Me']
                        person.Ma = request.GET['CD_Ma']
                        person.Ju = request.GET['CD_Ju']
                        person.Ve = request.GET['CD_Ve']
                        person.Sa = request.GET['CD_Sa']
                        person.Ra = request.GET['CD_Ra']
                        person.Ke = request.GET['CD_Ke']
                        person.As = request.GET['CD_As']
                        person.save()
                        #
                        degs = []
                        degs.append(request.GET['CD_Su'])
                        degs.append(request.GET['CD_Mo'])
                        degs.append(request.GET['CD_Me'])
                        degs.append(request.GET['CD_Ma'])
                        degs.append(request.GET['CD_Ju'])
                        degs.append(request.GET['CD_Ve'])
                        degs.append(request.GET['CD_Sa'])
                        degs.append(request.GET['CD_Ra'])
                        degs.append(request.GET['CD_Ke'])
                        degs.append(request.GET['CD_As'])

                        degs = [dmstodeg(i) for i in degs]

                        place_lat_lon = api.geocode(pplace)
                        lati, long = place_lat_lon[0]['geometry']['location']['lat'], place_lat_lon[0]['geometry']['location']['lng']
                        #
                        if request.GET['reloc_lat'] and request.GET['reloc_lon']:
                            lati, long = request.GET['reloc_lat'], request.GET['reloc_lon']
                            if '°' in lati:
                                if 'n' in lati.lower():
                                    lati = float(lati.split('°')[0])
                                else:
                                    lati = -float(lati.split('°')[0])
                            else:
                                lati = float(lati)
                            if '°' in long:
                                if 'e' in long.lower():
                                    long = float(long.split('°')[0])
                                else:
                                    long = -float(long.split('°')[0])
                            else:
                                long = float(long)
                        #
                        planets = ['Su', 'Mo', 'Me', 'Ma', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke', 'As']
                        signs = ['Ar', 'Ta', 'Ge', 'Ca', 'Le', 'Vg', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi']
                        #
                        # degs = bdate_time_place_to_degs(api, ddate, ttime, pplace)
                        # degs = match3(ddate, '2000.01.01', ttime, '12:00', pplace, 'Russia, Krasnodar')[4]
                        #
                        degs_signs = []
                        for i in range(len(degs)):
                            deg = degs[i]
                            planet = planets[i]
                            deg = deg + 60 if deg + 60 <= 360 else deg + 60 - 360
                            degs_signs.append([deg, planet])
                        #
                        polygons = """var cla = {};
                        var clo = {};
                        var planets = [""".format(lati, long)
                        #
                        for i in degs_signs:
                            polygons += '[{}, "{}"],'.format(str(i[0]), i[1])
                        polygons = polygons[:-1]
                        polygons += '];'
                        #
                        # degs_signs.sort(key=lambda x: x[0])
                        # sublines = """var sublines = ["""
                        # for i in degs_signs:
                        #     sublines += '[{}, "{}"],'.format(str(i[0]), i[1])
                        # sublines = sublines[:-1]
                        # sublines += '];'
                        #
                        context["polygons"] = polygons
                        #context["sublines"] = sublines
                        #

                        # Code for natal charts
                        name = request.GET['inputName1']
                        #
                        if request.GET['CD_Su'] != '':
                            degs = []
                            degs.append(request.GET['CD_Su'])
                            degs.append(request.GET['CD_Mo'])
                            degs.append(request.GET['CD_Me'])
                            degs.append(request.GET['CD_Ma'])
                            degs.append(request.GET['CD_Ju'])
                            degs.append(request.GET['CD_Ve'])
                            degs.append(request.GET['CD_Sa'])
                            degs.append(request.GET['CD_Ra'])
                            degs.append(request.GET['CD_Ke'])
                            degs.append(request.GET['CD_As'])
                            degs = [dmstodeg(i) for i in degs]
                            result = match3(ddate, ddate, ttime, ttime, pplace, pplace, degs)
                        else:
                            result = match3(ddate, ddate, ttime, ttime, pplace, pplace)
                        #
                        # items = list(results[names[1]][0].keys())
                        # #
                        # items_fix = {
                        #     'Soc': 'Sociable',
                        #     'Gro': 'Growth',
                        #     'Comm': 'Communicative',
                        #     'FO': 'Family-Oriented',
                        #     'Adve': 'Adventure',
                        #     'Dome': 'Domestic',
                        #     'Conf': 'Conflictive',
                        #     'Di': 'Distant',
                        #     'Spi': 'Spiritual/Travel',
                        #     'Fr': 'Friendly',
                        #     'Team': 'Teamwork',
                        #     'Comp': 'Complicate',
                        #     'Lo': 'Love',
                        #     'Sex': 'Sex',
                        #     'Tru': 'Trust'
                        # }
                        # scrbs = 'var x = [' + ','.join(['"' + items_fix[i] + '"' for i in items]) + '];'
                        # scrbs += 'data = ['

                        report_btns, report_txts = '', ''
                        p_asp_p, p_asp_h = '', ''

                            #
                            # for ki, kv in v[1].items():
                            #     if len(kv) > 0:
                            #         p_asp_p += '<tr>'
                            #         p_asp_p += '<td>' + ki + ': ' + escape('  '.join(list(kv))) + '</td>'
                            #         p_asp_p += '</tr>'
                            #
                            # for ki, kv in v[2].items():
                            #     if len(kv) > 0:
                            #         p_asp_h += '<tr>'
                            #         p_asp_h += '<td>' + ki + ': ' + escape('  '.join(list(kv))) + '</td>'
                            #         p_asp_h += '</tr>'

                            # Indian type of report
                        signs = ['Pi', 'Ar', 'Ta', 'Ge', 'Aq', 'Ca', 'Cp', 'Le', 'Sg', 'Sc', 'Li', 'Vg']
                            #
                        def decdeg2dms(dd):
                            mnt, sec = divmod(dd*3600,60)
                            deg, mnt = divmod(mnt,60)
                            if deg < 0:
                                deg = -deg
                            return deg, mnt

                        sign_nums = {['Ar', 'Ta', 'Ge', 'Ca', 'Le', 'Vg', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi'][i]: i+1 for i in range(12)}
                        c = []
                        # For P1 (main person)
                        t4, t5 = result[3][0], result[3][1]
                        t4vk = {v: k for k,v in t4.items()}
                        t5vk = {v: [i for i in t5 if t5[i] == v] for v in list(set(list(t5.values())))}
                        degs = result[4]
                        degs = {['Su', 'Mo', 'Me', 'Ma', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke', 'As'][i]: degs[i] for i in range(10)}

                        for i in range(12):
                            sign = signs[i]
                            house = t4[sign]
                            sign_num = sign_nums[sign]
                            s = ['', '', '', '']
                            try:
                                planets = t5vk[house]
                                for j in range(4):
                                    try:
                                        d = degs[planets[j]] - (sign_num - 1) * 30
                                        deg, min = decdeg2dms(d)
                                        s[j] = planets[j] + ' ' + str(int(deg)) + '°' + str(int(min)) + "'"
                                    except:
                                        pass
                            except:
                                pass
                            c.append("""
                                    <div class="d-flex p-1 justify-content-center mr-2" style="height: 38%">
                                        <div class="col mt-auto mb-auto" style="width: 25px">{}</div>
                                        <div class="col mt-auto mb-auto" style="width: 25px">{}</div>
                                    </div>
                                    <div class="d-flex p-1 justify-content-center mr-2" style="height: 38%">
                                        <div class="col" style="width: 25px">{}</div>
                                        <div class="col" style="width: 25px">{}</div>
                                    </div>
                                    <b class="bg-warning border border-dark rounded ml-1 pl-1 pr-1">{}</b>
                            """.format(s[0], s[1], s[2], s[3], str(house) + ' ' + sign))

                            # Layout generation
                        report_txts += """
                                <div class="row">
                                    <div class="container-fluid">
                                        <div class="row">
                                            <div class="col ml-2 pt-2" style="font-size: 9pt">
                                                <div class="row">
                                                    <div class="bg-white border border-dark border-right-0 border-bottom-0" style="width: 110px; height: 110px; border-top-left-radius: 10px;">{}</div>
                                                    <div class="bg-white border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                    <div class="bg-white border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                    <div class="bg-white border border-dark border-bottom-0" style="width: 110px; height: 110px; border-top-right-radius: 10px;">{}</div>
                                                </div>
                                                <div class="row">
                                                    <div class="bg-white border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                                    <div class="bg-white" style="width: 110px; height: 110px"></div>
                                                    <div class="bg-white" style="width: 110px; height: 110px"></div>
                                                    <div class="bg-white border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                                </div>
                                                <div class="row">
                                                    <div class="bg-white border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                                    <div class="bg-white" style="width: 110px; height: 110px"></div>
                                                    <div class="bg-white" style="width: 110px; height: 110px"></div>
                                                    <div class="bg-white border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                                </div>
                                                <div class="row">
                                                    <div class="bg-white border border-dark border-right-0" style="width: 110px; height: 110px; border-bottom-left-radius: 10px;">{}</div>
                                                    <div class="bg-white border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                    <div class="bg-white border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                    <div class="bg-white border border-dark" style="width: 110px; height: 110px; border-bottom-right-radius: 10px;">{}</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                        """.format(c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11])
                        #
                        context['label_db'] = label_db
                        context["report_txts"] = report_txts
                        context["labelName"] = labelName
                        #
                        return render(request, 'relocation_map3d.html', context=context)
                    else:
                        return render(request, 'map_add_labels.html', context=context)
        else:
            return redirect('/login')

class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('/relocation_map_input')
            else:
                return redirect('/relocation_map3d?inputSession=')
        else:
            return redirect('/login')

class DataInput3View(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'data_input3.html', context=None)
        else:
            return redirect('/login')

# AJAX based functions
def ajax_validate_person_name(request):  # finds persons with <name> like provided (for autocomplete of names)
    name = request.GET.get('name', None)
    persons = ''
    for p in Person.objects.filter(name__contains=name)[:80]:
        persons += '<option>{} | {} | {} | {} | {}</p>'.format(p.name, p.bdate, p.btime, p.bplace, p.gender)
    data = {
        'persons': persons
    }
    return JsonResponse(data)

def ajax_validate_person_name_admin(request):
    data = {
        'sessions': ''
    }
    name = request.GET.get('name', None)
    q = Person.objects.get(name=name)
    if q:
        for i in MapSession.objects.filter(user=q.user):
            d = str(i.date).split('.')[0] + str(i.date)[-5:]
            data['sessions'] += '<option value="{}    {}    {}"></option>'.format(i.name, d, i.id)
    return JsonResponse(data)

def ajax_add_person(request):  # adds a new person with data provided (if not already exists)
    name = request.GET.get('name', None)
    bdate = request.GET.get('bdate', None)
    btime = request.GET.get('btime', None)
    bplace = request.GET.get('bplace', None)
    gender = request.GET.get('gender', None)

    data = {
        'state': '1'
    }

    if Person.objects.filter(name=name).count() > 0:
        if Person.objects.filter(name=name, bdate=bdate, btime=btime, bplace=bplace, gender=gender).count() > 0:
            data['state'] = ''

    if data['state'] == '1':
        person = Person()
        person.name = name
        person.bdate = bdate
        person.btime = btime
        person.bplace = bplace
        person.gender = gender
        person.save()
    return JsonResponse(data)


# AJAX based functions

class DataInput3MatchView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            context = None
            if request.method == 'GET':
                form = Form(request.GET)
                if form.is_valid():
                    names = [request.GET.get('inputName' + str(i + 1)) for i in range(5)]
                    names = [i for i in names if i.strip() != '']
                    #
                    valid_persons_num = len(names)
                    #
                    bdates = [request.GET.get('inputDate' + str(i + 1)).split('-') for i in range(valid_persons_num)]
                    bdates = ['.'.join([i[2], i[1], i[0]]) for i in bdates]
                    #
                    btimes = [request.GET.get('inputTime' + str(i + 1)) for i in range(valid_persons_num)]
                    #
                    bplaces = [request.GET.get('autocomplete' + str(i + 1)) for i in range(valid_persons_num)]
                    #
                    results = {names[i + 1] : match3(bdates[0], bdates[i + 1], btimes[0], btimes[i + 1], bplaces[0], bplaces[i + 1]) for i in range(valid_persons_num - 1)}
                    #
                    items = list(results[names[1]][0].keys())
                    #
                    items_fix = {
                        'Soc': 'Sociable',
                        'Gro': 'Growth',
                        'Comm': 'Communicative',
                        'FO': 'Family-Oriented',
                        'Adve': 'Adventure',
                        'Dome': 'Domestic',
                        'Conf': 'Conflictive',
                        'Di': 'Distant',
                        'Spi': 'Spiritual/Travel',
                        'Fr': 'Friendly',
                        'Team': 'Teamwork',
                        'Comp': 'Complicate',
                        'Lo': 'Love',
                        'Sex': 'Sex',
                        'Tru': 'Trust'
                    }
                    scrbs = 'var x = [' + ','.join(['"' + items_fix[i] + '"' for i in items]) + '];'
                    scrbs += 'data = ['

                    report_btns, report_txts = '', ''
                    p_asp_p, p_asp_h = '', ''

                    iii = 0
                    for k,v in results.items():
                        iii += 1
                        scrbs += '{histfunc: "sum", y: [' + ','.join([str(v[0][i]) for i in items]) + '], x: x, type: "histogram", name: ' + '"' + k + '"}, '
                        report_btns += '<button name="report_p' + str(iii) + '" class="report_btn btn btn-warning m-1">Report ' + k + '</button>'

                        for ki, kv in v[1].items():
                            if len(kv) > 0:
                                p_asp_p += '<tr>'
                                p_asp_p += '<td>' + ki + ': ' + escape('  '.join(list(kv))) + '</td>'
                                p_asp_p += '</tr>'

                        for ki, kv in v[2].items():
                            if len(kv) > 0:
                                p_asp_h += '<tr>'
                                p_asp_h += '<td>' + ki + ': ' + escape('  '.join(list(kv))) + '</td>'
                                p_asp_h += '</tr>'
                        # Indian type of report
                        signs = ['Pi', 'Ar', 'Ta', 'Ge', 'Aq', 'Ca', 'Cp', 'Le', 'Sg', 'Sc', 'Li', 'Vg']
                        #
                        def decdeg2dms(dd):
                            mnt, sec = divmod(dd*3600,60)
                            deg, mnt = divmod(mnt,60)
                            if deg < 0:
                                deg = -deg
                            return deg, mnt

                        sign_nums = {['Ar', 'Ta', 'Ge', 'Ca', 'Le', 'Vg', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi'][i]: i+1 for i in range(12)}
                        c = []
                        # For P1 (main person)
                        t4, t5 = v[3][0], v[3][1]
                        t4vk = {v: k for k,v in t4.items()}
                        t5vk = {v: [i for i in t5 if t5[i] == v] for v in list(set(list(t5.values())))}
                        degs = v[4]
                        degs = {['Su', 'Mo', 'Me', 'Ma', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke', 'As'][i]: degs[i] for i in range(10)}

                        for i in range(12):
                            sign = signs[i]
                            house = t4[sign]
                            sign_num = sign_nums[sign]
                            s = ['', '', '', '']
                            try:
                                planets = t5vk[house]
                                for j in range(4):
                                    try:
                                        d = degs[planets[j]] - (sign_num - 1) * 30
                                        deg, min = decdeg2dms(d)
                                        s[j] = planets[j] + ' ' + str(int(deg)) + '°' + str(int(min)) + "'"
                                    except:
                                        pass
                            except:
                                pass
                            c.append("""
                                <div class="d-flex p-1 justify-content-center mr-2" style="height: 38%">
                                    <div class="col mt-auto mb-auto" style="width: 25px">{}</div>
                                    <div class="col mt-auto mb-auto" style="width: 25px">{}</div>
                                </div>
                                <div class="d-flex p-1 justify-content-center mr-2" style="height: 38%">
                                    <div class="col" style="width: 25px">{}</div>
                                    <div class="col" style="width: 25px">{}</div>
                                </div>
                                <b class="bg-warning border border-dark rounded ml-1 pl-1 pr-1">{}</b>
                            """.format(s[0], s[1], s[2], s[3], str(house) + ' ' + sign))

                        # For P2 (secondary person)
                        t4p2, t5p2 = v[5][0], v[5][1]
                        t4vkp2 = {v: k for k,v in t4p2.items()}
                        t5vkp2 = {v: [i for i in t5p2 if t5p2[i] == v] for v in list(set(list(t5p2.values())))}
                        degs = v[6]
                        degs = {['Su', 'Mo', 'Me', 'Ma', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke', 'As'][i]: degs[i] for i in range(10)}

                        for i in range(12):
                            sign = signs[i]
                            house = t4p2[sign]
                            sign_num = sign_nums[sign]
                            s = ['', '', '', '']
                            try:
                                planets = t5vkp2[house]
                                for j in range(4):
                                    try:
                                        d = degs[planets[j]] - (sign_num - 1) * 30
                                        deg, min = decdeg2dms(d)
                                        s[j] = planets[j] + ' ' + str(int(deg)) + '°' + str(int(min)) + "'"
                                    except:
                                        pass
                            except:
                                pass
                            c.append("""
                                <div class="d-flex p-1 justify-content-center mr-2" style="height: 38%">
                                    <div class="col mt-auto mb-auto" style="width: 25px">{}</div>
                                    <div class="col mt-auto mb-auto" style="width: 25px">{}</div>
                                </div>
                                <div class="d-flex p-1 justify-content-center mr-2" style="height: 38%">
                                    <div class="col" style="width: 25px">{}</div>
                                    <div class="col" style="width: 25px">{}</div>
                                </div>
                                <b class="bg-warning border border-dark rounded ml-1 pl-1 pr-1">{}</b>
                            """.format(s[0], s[1], s[2], s[3], str(house) + ' ' + sign))

                        # Layout generation
                        report_txts += """
                            <div id="report_p{}" class="row">
                                <div class="container-fluid">
                                    <div class="row">
                                        <div class="col ml-2 pt-2" style="font-size: 9pt">
                                            <div><h3>Report P1 ({})</h3></div>
                                            <div class="row">
                                                <div class="border border-dark border-right-0 border-bottom-0" style="width: 110px; height: 110px; border-top-left-radius: 10px;">{}</div>
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px; border-top-right-radius: 10px;">{}</div>
                                            </div>
                                            <div class="row">
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                                <div style="width: 110px; height: 110px"></div>
                                                <div style="width: 110px; height: 110px"></div>
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                            </div>
                                            <div class="row">
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                                <div style="width: 110px; height: 110px"></div>
                                                <div style="width: 110px; height: 110px"></div>
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                            </div>
                                            <div class="row">
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px; border-bottom-left-radius: 10px;">{}</div>
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                <div class="border border-dark" style="width: 110px; height: 110px; border-bottom-right-radius: 10px;">{}</div>
                                            </div>
                                        </div>

                                        <div class="col ml-2 pt-2" style="font-size: 9pt">
                                            <div><h3>Report P2 ({})</h3></div>
                                            <div class="row">
                                                <div class="border border-dark border-right-0 border-bottom-0" style="width: 110px; height: 110px; border-top-left-radius: 10px;">{}</div>
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px; border-top-right-radius: 10px;">{}</div>
                                            </div>
                                            <div class="row">
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                                <div style="width: 110px; height: 110px"></div>
                                                <div style="width: 110px; height: 110px"></div>
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                            </div>
                                            <div class="row">
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                                <div style="width: 110px; height: 110px"></div>
                                                <div style="width: 110px; height: 110px"></div>
                                                <div class="border border-dark border-bottom-0" style="width: 110px; height: 110px">{}</div>
                                            </div>
                                            <div class="row">
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px; border-bottom-left-radius: 10px;">{}</div>
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                <div class="border border-dark border-right-0" style="width: 110px; height: 110px">{}</div>
                                                <div class="border border-dark" style="width: 110px; height: 110px; border-bottom-right-radius: 10px;">{}</div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="row">
                                        <div class="col">
                                            <h3>Report {} P_asp_P</h3>
                                            <table class="table table-sm">
                                                {}
                                            </table>
                                        </div>

                                        <div class="col">
                                            <h3>Report {} P_asp_H</h3>
                                            <table class="table table-sm">
                                                {}
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        """.format(str(iii), names[0], c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], k, c[12], c[13], c[14], c[15], c[16], c[17], c[18], c[19], c[20], c[21], c[22], c[23], k, p_asp_p, k, p_asp_h)

                    scrbs = scrbs[:-1] + '];'

                    context = {
                        'script_part': scrbs,
                        'matching_from': names[0] if len(names[0].split(' ')) == 1 else names[0].split(' ')[0],
                        'matching_to': ', '.join([i if len(i.split(' ')) == 1 else i.split(' ')[0] for i in names[1:]]),
                        'report_btns': report_btns,
                        'report_txts': report_txts
                    }
            return render(request, 'match_engine3.html', context=context)
        else:
            return redirect('/login')

class DataInputDetailedMatchView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_authenticated:
            if request.method == 'GET':
                form = Form(request.GET)
                if form.is_valid():
                    # Names
                    name1 = request.GET.get('inputName1')
                    name2 = request.GET.get('inputName2')
                    if not name1:
                        name1 = 'Noname1'
                    if not name2:
                        name2 = 'Noname2'
                    # Calculations
                    bdate1 = request.GET.get('inputDate1').split('-')
                    bdate1 = bdate1[2] + '.' + bdate1[1] + '.' + bdate1[0]
                    bdate2 = request.GET.get('inputDate2').split('-')
                    bdate2 = bdate2[2] + '.' + bdate2[1] + '.' + bdate2[0]
                    #
                    btime1 = request.GET.get('inputTime1')
                    btime2 = request.GET.get('inputTime2')
                    #
                    bplace1 = request.GET.get('autocomplete1')
                    bplace2 = request.GET.get('autocomplete2')
                    #
                    data = match_all(bdate1, bdate2, btime1, btime2, bplace1, bplace2)
                    data1 = data['p1p2']
                    data2 = data['p2p1']
                    items = list(data1.keys())
                    #
                    with open('degrees.txt', 'r') as file:
                        degs = file.readlines()
                    #
                    context = {
                        'name1': name1,
                        'name2': name2,
                        'bdate1': bdate1,
                        'bdate2': bdate2,
                        'btime1': btime1,
                        'btime2': btime2,
                        'bplace1': bplace1,
                        'bplace2': bplace2,

                        'items': ",".join(items),
                        'y1': ",".join([str(data1[i]) for i in items]),
                        'y2': ",".join([str(data2[i]) for i in items]),

                        'sudeg1': degs[0],
                        'modeg1': degs[1],
                        'medeg1': degs[2],
                        'madeg1': degs[3],
                        'judeg1': degs[4],
                        'vedeg1': degs[5],
                        'sadeg1': degs[6],
                        'radeg1': degs[7],
                        'kedeg1': degs[8],
                        'asdeg1': degs[9],

                        'sudeg2': degs[11],
                        'modeg2': degs[12],
                        'medeg2': degs[13],
                        'madeg2': degs[14],
                        'judeg2': degs[15],
                        'vedeg2': degs[16],
                        'sadeg2': degs[17],
                        'radeg2': degs[18],
                        'kedeg2': degs[19],
                        'asdeg2': degs[20]
                    }
                else:
                    context = None
            return render(request, "match_engine2.html", context=context)
        else:
            return redirect('/login')

class DataInputMatchView(TemplateView):
    def get(self, request, **kwargs):
        if request.method == 'GET':
            form = Form(request.GET)
            if form.is_valid():
                # Names
                name1 = request.GET.get('inputName1')
                name2 = request.GET.get('inputName2')
                if not name1:
                    name1 = 'Noname1'
                if not name2:
                    name2 = 'Noname2'
                # Calculations
                bdate1 = request.GET.get('inputDate1').split('-')
                bdate1 = bdate1[2] + '.' + bdate1[1] + '.' + bdate1[0]
                bdate2 = request.GET.get('inputDate2').split('-')
                bdate2 = bdate2[2] + '.' + bdate2[1] + '.' + bdate2[0]
                #
                data = match_all(bdate1, bdate2)
                data1 = data['p1p2']
                data2 = data['p2p1']
                items = list(data1.keys())
                #
                context = {
                    'name1': name1,
                    'name2': name2,
                    'items': ",".join(items),
                    'y1': ",".join([str(data1[i]) for i in items]),
                    'y2': ",".join([str(data2[i]) for i in items])
                }
            else:
                context = None
        return render(request, "match_engine1.html", context=context)

class DataInputView(TemplateView):
    template_name = "data_input1.html"

class DataInputDetailedView(TemplateView):
    template_name = "data_input2.html"

class PersonsListView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            if request.method == 'GET':
                context = None
                if 'inputNameAdd' in request.GET:
                    person = Person()
                    name = request.GET['inputNameAdd']
                    bdate = request.GET['inputDateAdd']
                    btime = request.GET['inputTimeAdd']
                    bplace = request.GET['autocomplete2']
                    gender = request.GET['inputGenderAdd']
                    username = request.GET['usernameAdd']

                    person.name = name
                    person.bdate = bdate
                    person.btime = btime
                    person.bplace = bplace
                    person.gender = gender
                    person.user = username

                    person.save()
                    #render(request, "persons.html", context=context)
                # Edit person
                elif 'inputNameEdit' in request.GET:
                    name = request.GET['inputNameEdit']
                    bdate = request.GET['inputDateEdit']
                    btime = request.GET['inputTimeEdit']
                    bplace = request.GET['autocomplete1']
                    gender = request.GET['inputGenderEdit']
                    username = request.GET['usernameEdit']

                    init_name = request.GET['nameEditHidden']
                    init_bdate = request.GET['bdateEditHidden']
                    init_btime = request.GET['btimeEditHidden']
                    init_bplace = request.GET['bplaceEditHidden']
                    init_gender = request.GET['genderEditHidden']
                    init_username = request.GET['usernameHidden']

                    person = Person.objects.get(name=init_name, bdate=init_bdate, btime=init_btime, bplace=init_bplace, gender=init_gender)
                    person.name = name
                    person.bdate = bdate
                    person.btime = btime
                    person.bplace = bplace
                    person.gender = gender
                    person.user = username
                    person.save()
                    #render(request, "persons.html", context=context)
                # Delete person
                elif 'personDeleteId' in request.GET:
                    index = request.GET['personDeleteId']
                    if len(index) != 0:
                        Person.objects.get(pk=int(index)).delete()
                    #render(request, "persons.html", context=context)
                # Just show the list with persons
                entries = ""
                datalist = ""

                pnum = Person.objects.all().count()
                mli = int(pnum // 1000)
                if pnum - mli * 1000 > 0:
                    mli += 1

                try:
                    link_id = request.GET['link_id']
                    if int(link_id) < int(mli):
                        si, ei = (int(link_id)-1) * 1000, int(link_id) * 1000
                    else:
                        si, ei = (int(link_id)-1) * 1000, pnum
                except Exception as e:
                    link_id = '1'
                    si, ei = 0, 1000
                i = 1
                for person in Person.objects.all()[si:ei]:
                    index = i + si
                    name = person.name
                    bdate = person.bdate
                    btime = person.btime
                    bplace = person.bplace
                    gender = person.gender
                    username = person.user

                    entries += """
                        \n
                        <tr>
                            <td>
                                {}.
                            </td>

                            <td class="text">
                                <span>{}</span>
                            </td>

                            <td class="text">
                                <span>{}, {}</span>
                            </td>

                            <td class="text">
                                <span>{}</span>
                            </td>

                            <td class="text">
                                <span>{}</span>
                            </td>

                            <td>
                                <button class="btn btn-xs btn-info btn-block" type="button" id="plistControl" data-toggle="modal" data-target="#modalEdit" data-name="{}" data-bdate="{}" data-btime="{}" data-place="{}" data-gender="{}" data-username="{}">Edit</button>
                            </td>
                    """.format(index, name, bdate, btime, bplace, gender, name, bdate, btime, bplace, gender, username)
                    entries += """
                            <td>
                    """
                    entries += """
                                    <div hidden>{}</div>
                                    <button class="btn btn-xs btn-warning btn-block btn_delete_person" id="plistControl" type="submit">Delete</button>
                            </td>
                        </tr>
                    """.format(person.id)
                    i += 1

                    val = "{} {},{} {} | {} ({})".format(name, bdate, btime, bplace, gender, person.id)
                    datalist += '<option value="{}">'.format(val)

                links = ''
                for i in range(1, mli + 1):
                    if i == int(link_id):
                        links += '<button class="btn_link_id btn btn-primary m-1" type="submit">{}</button>'.format(str(i))
                    else:
                        links += '<button class="btn_link_id btn btn-dark m-1" type="submit">{}</button>'.format(str(i))

                context = {
                    'entries': entries,
                    'datalist': datalist,
                    'links': links,
                    'link_id': '<input type="text" class="link_id" name="link_id" value="' + str(link_id) + '" hidden>'
                }

                return render(request, "persons_list.html", context=context)
        else:
            return redirect('/login')
