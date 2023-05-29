from datetime import datetime

from django.utils.timezone import make_aware
from django.shortcuts import render
from django.http.response import JsonResponse
from django.shortcuts import resolve_url as r

from ai_experiment.core.utils import tz_fix
from ai_experiment.core.facade import invalid_day_of_month
from ai_experiment.core.constants import dayOfWeekChoices, frequencyChoices
from ai_experiment.settings import BASE_URL


frequency_options = [el[0] for el in frequencyChoices.choices]
day_of_week_options = [el[0] for el in dayOfWeekChoices.choices]

