#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onlineweb4.settings")

from chunks.models import Chunk


class Chunks:
    # Bootstrap/insert fixtures for apps
    @classmethod
    def bootstrap(cls):
        c = Chunk.objects.create(
            key='offline_ingress',
            content='''
Offline er Online sitt eget tidsskrift og så dagens lys i mars 2011. Profil- og aviskomiteen står for det grafiske og redaksjonelle ansvaret, og har i tillegg eksterne skribenter i andre deler av Online.
            ''')
        c.save()

        c = Chunk.objects.create(
            key='offline_brodtekst',
            content='''
Offline gis ut to ganger i semesteret og inneholder en fin blanding av underholdende og opplysende saker myntet på informatikkstudenter.

Ønsker du å abonnere på magasinet og få tilsendt papirutgaven i posten kan du gå inn å registrere deg gjennom vårt googleskjema: [Bestillingsskjema](http://goo.gl/wksFS)

Ellers finner du alle utgavene i PDF-format nedenfor.
God lesing!
            ''')
        c.save()

