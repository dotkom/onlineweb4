# -*- coding: utf-8 -*-
import datetime
import json

from hashlib import sha256

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone

from apps.genfors.models import AnonymousVoter, RegisteredVoter, \
    Alternative, BooleanVote, Meeting, MultipleChoice, Result


BOOLEAN_VOTE = 0
MULTIPLE_CHOICE = 1

"""
Helper functions
"""


def get_active_meeting():
    today = datetime.date.today()
    hour24 = datetime.timedelta(hours=24)
    return Meeting.objects.filter(
        start_date__lte=timezone.now(), ended=False,
        start_date__range=[today - hour24, today + hour24]
    ).order_by('-start_date').first()


def get_next_meeting():
    return Meeting.objects.filter(ended=False).order_by('-start_date').first()


def is_admin(request):
    return request.session.get('genfors_admin') is True


def anonymous_voter(anon_cookie, username):
    """Returns anon voter object if found"""
    if not anon_cookie:
        # Empty cookie
        return
    meeting = get_active_meeting()
    # Hashing with username before lookup
    h = sha256()
    h.update(anon_cookie.encode('utf-8'))
    h.update(username.encode('utf-8'))
    return AnonymousVoter.objects.filter(user_hash=h.hexdigest(), meeting=meeting).first()

"""
End helper functions
"""


# Vote results
def get_results(self, admin):
    if self.locked:
        results = get_locked_results(self, admin)
        if results:
            return results
    else:
        return handle_not_locked(self, admin)


def get_locked_results(self, admin):
    r = Result.objects.filter(question=self)
    if r:
        r = r[0]
        if admin:
            return json.loads(r.result_private)
        else:
            return json.loads(r.result_public)
    else:
        return None


def handle_not_locked(self, admin):
    results = None
    if self.question_type is BOOLEAN_VOTE:
        results = handle_boolean_voting(self)

    elif self.question_type is MULTIPLE_CHOICE:
        results = handle_multiple_choice_voting(self)

    else:
        raise NotImplementedError

    if results:
        winner = max(results.keys(), key=(lambda key: results[key]))
        winner_votes = results[winner]

        minimum = 0
        if self.locked:
            total_votes = self.total_voters
        else:
            total_votes = len(self.meeting.get_can_vote())

        # Normal
        if self.majority_type == 0:
            minimum = 1 / float(2)

        # Qualitative
        elif self.majority_type == 1:
            minimum = 2 / float(3)

        res = {'valid': False, 'data': {}}

        if total_votes != 0:
            res['valid'] = winner_votes / float(total_votes) > minimum

        # Admins should see all info regardless of only show winner
        if admin or not self.only_show_winner:
            res['data'] = results
            return res
        else:
            res['data'] = {winner: None}
            return res
    else:
        return None


def handle_boolean_voting(self):
    results = {'Ja': 0, 'Nei': 0, 'Blankt': 0}
    for a in BooleanVote.objects.filter(question=self):
        if a.answer is None:
            results['Blankt'] += 1
        elif a.answer is False:
            results['Nei'] += 1
        elif a.answer is True:
            results['Ja'] += 1
    return results


def handle_multiple_choice_voting(self):
    mc = MultipleChoice.objects.filter(question=self)
    results = {}

    for alt in Alternative.objects.filter(question=self):
        results[alt.description] = 0

    results['Blankt'] = 0
    for a in mc:
        if a.answer is not None:
            if a.answer.description not in results:
                results[a.answer.description] = 0
            results[a.answer.description] += 1
        else:
            if 'Blankt' not in results:
                results['Blankt'] = 0
            results['Blankt'] += 1
    return results


# other stuff
def handle_login(request, context):
    meeting = get_active_meeting()

    reg_voter = RegisteredVoter.objects.filter(user=request.user, meeting=meeting).first()
    if reg_voter or not meeting.registration_locked:
        return _handle_user_login(request, context['form'])


def _handle_user_login(request, form):
    meeting = get_active_meeting()

    # Creating hash
    h = sha256()
    h.update(settings.SECRET_KEY.encode('utf-8'))
    h.update(request.user.username.encode('utf-8'))
    h.update(form.cleaned_data['salt'].encode('utf-8'))
    h = h.hexdigest()

    # Create a registered voter object if it does not already exist
    reg_voter = RegisteredVoter.objects.filter(meeting=meeting, user=request.user)
    if not reg_voter:
        reg_voter = RegisteredVoter(user=request.user, meeting=meeting)
        reg_voter.save()
        # Double hashing when saving while we store the original hash as a cookie
        h2 = sha256()
        h2.update(h.encode('utf-8'))
        h2.update(request.user.username.encode('utf-8'))
        anon_voter = AnonymousVoter(user_hash=h2.hexdigest(), meeting=meeting)
        anon_voter.save()
    else:
        # Trying to get anonymous voter object too, if not found the secret code was wrong
        anon_voter = anonymous_voter(h, request.user.username)
        if not anon_voter:
            messages.error(request, 'Feil personlig kode')

    response = redirect('genfors_index')
    if anon_voter:
        # Anyonous voter hash stored in cookies for 1 day
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        response.set_cookie(key='anon_voter', value=h, expires=tomorrow)
    elif 'anon_voter' in request.COOKIES:
        # Delete old hash
        response.delete_cookie('anon_voter')
    return response


def generate_genfors_context(aq, context, anon_voter, reg_voter):
    if not aq:
        return context

    if aq.anonymous:
        context['already_voted'] = aq.already_voted(anon_voter)
    else:
        context['already_voted'] = aq.already_voted(reg_voter)

    total_votes = aq.get_votes().count()
    alternatives = aq.get_alternatives()

    context['active_question'] = {}
    context['active_question']['total_votes'] = total_votes
    context['active_question']['alternatives'] = alternatives

    context['registered_voter'] = reg_voter
    context['anonymous_voter'] = anon_voter

    res = aq.get_results()

    if total_votes != 0 and not aq.only_show_winner:
        count_votes(context, aq, res)

    return context

def count_votes(context, aq, res):
    total_votes = context['active_question']['total_votes']
    votes_for_alternative = context['active_question']['total_votes'] - res['data']['Blankt']
    alternatives = context['active_question']['alternatives']

    if aq.question_type is BOOLEAN_VOTE:
        if votes_for_alternative == 0:
            context['active_question']['yes_percent'] = res['data']['Ja'] * 100 // 1
            context['active_question']['no_percent'] = res['data']['Nei'] * 100 // 1
        else:
            context['active_question']['yes_percent'] = res['data']['Ja'] * 100 // votes_for_alternative
            context['active_question']['no_percent'] = res['data']['Nei'] * 100 // votes_for_alternative
            
        context['active_question']['blank_percent'] = res['data']['Blankt'] * 100 // total_votes

    elif aq.question_type is MULTIPLE_CHOICE and total_votes != 0:
        context['active_question']['multiple_choice'] = {}
        for a in alternatives:
            context['active_question']['multiple_choice'][a.description] = [0, 0]
        context['active_question']['multiple_choice']['Blankt'] = [0, 0]
        for k, v in res['data'].items():
            if k == 'Blankt' or total_votes == 1:
                context['active_question']['multiple_choice'][k] = [v, v * 100 // total_votes]
            else:
                context['active_question']['multiple_choice'][k] = [v, v * 100 // votes_for_alternative]
