from django.http import Http404
from django.views.generic import DetailView, FormView, ListView
from dss.Mixin import (FormJsonResponseMixin, JsonResponseMixin,
                       MultipleJsonResponseMixin)
from dss.Serializer import serializer

from utils.tools import CheckToken, handle_post_body_to_json, parse_info
from datetime import datetime 
from .models import *


class EventView(MultipleJsonResponseMixin, ListView):
    model = Events
    paginate_by = 15
    datetime_type = 'string'
    exclude_attr = ('event_year', 'event_year_id',
                    'event_province_id', 'event_project', 'event_project_id')

    def get_queryset(self):
        kwargs = {
        }
        year = self.request.GET.get('year', None)
        type_ = self.request.GET.get('type', None)
        province = self.request.GET.get('province', None)
        etype = self.request.GET.get('etype', 0)
        search = self.request.GET.get('search', None)

        if year:
            kwargs['event_date__year'] = year
        if province:
            kwargs['event_province_id'] = province
        if type_:
            kwargs['eventtypedetail__type'] = type_
        if etype:
            kwargs['event_type'] = etype
        if search:
            kwargs['name'] = search

        queryset = super(EventView, self).get_queryset()
        queryset = queryset.filter(**kwargs)
        return queryset


class EventDetailView(JsonResponseMixin, DetailView):
    model = EventsDetail
    foreign = True
    many = True
    datetime_type = 'string'
    pk_url_kwarg = 'id'
    exclude_attr = ('id_id',)


class EventRuleslView(JsonResponseMixin, DetailView):
    model = EventRules
    foreign = True
    many = True
    datetime_type = 'string'
    pk_url_kwarg = 'id'
    exclude_attr = ('id_id',)


class EventTrafficView(JsonResponseMixin, DetailView):
    model = EventTraffic
    foreign = True
    many = True
    datetime_type = 'string'
    pk_url_kwarg = 'id'
    exclude_attr = ('id_id',)


class EventScView(JsonResponseMixin, DetailView):
    model = EventSc
    foreign = True
    many = True
    datetime_type = 'string'
    pk_url_kwarg = 'id'
    exclude_attr = ('id_id',)


class ApplyUserView(FormJsonResponseMixin, CheckToken, FormView):
    model = ApplyUser

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the form.
        """
        return parse_info({'msg': 'token'})

    @handle_post_body_to_json
    def post(self, request, body=None, *args, **kwargs):
        if not self.wrap_check_token_result():
            return self.render_to_response({'msg': self.message})

        if ApplyUser.objects.filter(apply_user=self.user).exists():
            return parse_info({'msg': '已报名'})

        for i in request.POST.keys():
            kwargs[i] = request.POST[i]
        apply_types =(kwargs['types'].split(','))

        apply_ = ApplyUser.create(
            user=self.user, apply_types=apply_types, **kwargs)
        if apply_:
            return self.render_to_response(serializer(apply_, exclude_attr=('password', 'id', 'reg_date'), datetime_format='string'))
        return self.render_to_response({'msg': '赛事或者类型id错误'})


def get_event_filter_view(request):
    res = dict()
    all_province = EventProvince.objects.all()
    all_type = EventType.objects.filter(event_type=request.GET.get('etype', 0))
    res['all_year'] = [str(i) for i in reversed(
        range(2010, datetime.now().year + 1)) if Events.objects.filter(event_date__year=i).exists()]
    res['all_province'] = serializer(all_province)
    res['all_type'] = serializer(all_type)

    return parse_info(res)


def get_event_type_view(request, event_id):
    res = dict()
    try:
        event = Events.objects.get(id=event_id)
        queryset = EventTypeDetail.objects.filter(event=event)
    except Exception as e:
        raise Http404("event_id：{} 错误".format(event_id))

    all_type = []
    for i in queryset:
        all_type.append({
            'id': i.id,
            'type_name': i.type.type,
            'type_lines': i.lines,
            'type_price': i.price
        })
    res['type'] = all_type
    res['can_apply_count'] = int(
        event.eventsdetail.apply_count) - len(event.applyuser_set.filter(is_check=1))
    res['base_price'] = event.eventsdetail.base_price
    return parse_info(res)


def get_event_apply_user_view(request, event_id):
    res = dict()
    try:
        event = Events.objects.get(id=event_id)
        queryset = event.applyuser_set.filter(is_check=0)
    except Exception as e:
        raise Http404("event_id：{} 错误".format(event_id))

    apply_list = []
    for i in queryset:
        apply_list.append({
            'user_obj': {
                'id': i.apply_user.id,
                'username': i.apply_user.userprofile.username,
                'sex': i.apply_user.userprofile.sex or '',
            },
            'apply_types': [i.apply_type.type.type for i in i.applyusertypes_set.all()],
            'apply_time': i.create_time
        })
    res['list'] = apply_list
    return parse_info(res, safe=True)
  

def get_event_score_view(request, event_id):
    res = []
    try:
        event = Events.objects.get(id=event_id)
        queryset = event.authority_set.all().order_by('single')
    except Exception as e:
        raise Http404("event_id：{} 错误".format(event_id))
        
    type = request.GET.get('type')
    kwargs = {}
    if type:
        kwargs['eventType_id'] = type

    queryset = queryset.filter(**kwargs)

    for i in queryset:
        res.append({
            'user_info': serializer(i.username, exclude_attr=('password', 'is_email_check', 'reg_date')),
            'event_info': serializer(i.events, datetime_format='string') ,
            'score': {
                'eventType': i.eventType.type,
                'single' : i.single,
                'turn': i.turn,
                'recent': i.recent,
                'award': i.award
            }
        })

    return parse_info(res, safe=False)
