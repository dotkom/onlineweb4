# -*- coding: utf-8 -*-

from django.shortcuts import render
from memcache import Client

# dotKom: To manually see the mailinglists in memcache, do this:
#
# $ ssh you@morgan.online.ntnu.no               # connect to morgan
# $ sudo su www-data -                          # log in as web user
# $ python                                      # open the interactive python shell
# $ from memcache import client                 # error message will appear if the library is not found
# $ mc = Client(["127.0.0.1:11211"], debug=0)   # start the memcache client
# $ lists = mc.get("sympa_lists")               # get sympa lists that are stored in memcache
# $ print lists


def index(request):
    mc = Client(["127.0.0.1:11211"])  # morgan.online.ntnu.no

    lists = mc.get("sympa_lists")

    # If we couldn't find any information in memcache right now
    if lists is None:
        lists = [
            {'name': 'linjeforeninger', 'members': [
                {'subscriber': u'', 'name': u'Alf', 'email': u'alf-styret@list.stud.ntnu.no'},
                {'subscriber': u'', 'name': u'Smørekoppen', 'email': u'styret@smorekoppen.no'},
                {'subscriber': u'', 'name': u'Abakus', 'email': u'abakus@abakus.no'},
                {'subscriber': u'', 'name': u'Omega', 'email': u'omega@omega.ntnu.no'},
                {'subscriber': u'', 'name': u'Bergstuderendes Forening', 'email': u'bsf@org.ntnu.no'},
                {'subscriber': u'', 'name': u'Delta', 'email': u'delta@list.stud.ntnu.no'},
                {'subscriber': u'', 'name': u'Aarhønen', 'email': u'hs@aarhonen.no'},
                {'subscriber': u'', 'name': u'Hybrida', 'email': u'hybrida@org.ntnu.no'},
                {'subscriber': u'', 'name': u'Janus', 'email': u'janus@org.ntnu.no'},
                {'subscriber': u'', 'name': u'Online', 'email': u'online@online.ntnu.no'},
                {'subscriber': u'', 'name': u'Placebo', 'email': u'placebo@list.stud.ntnu.no'},
                {'subscriber': u'', 'name': u'Spanskrøret', 'email': u'styre@spanskroret.no'},
                {'subscriber': u'', 'name': u'HC', 'email': u'styret@hc.ntnu.no'},
                {'subscriber': u'', 'name': u'Mannhullet', 'email': u'styret@mannhullet.no'},
                {'subscriber': u'', 'name': u'Volvox', 'email': u'volvox-styre@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Socius Extremus', 'email': u'socius.extremus@hotmail.no'},
                {'subscriber': u'', 'name': u'Nabla', 'email': u'nabla@nabla.ntnu.no'},
                {'subscriber': u'', 'name': u'Leonardo', 'email': u'leonardo-styret@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Erudio', 'email': u'erudiostyret@hotmail.com'},
                {'subscriber': u'mail', 'name': u'Paideia', 'email': u'paideia@live.no'},
                {'subscriber': u'mail', 'name': u'CAF', 'email': u'idrett@hotmail.com'},
                {'subscriber': u'mail', 'name': u'ELF', 'email': u'ntnuelf@gmail.com'},
                {'subscriber': u'mail', 'name': u'PSI', 'email': u'psi.linjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'Katharsis', 'email': u'linjeforeningenkatharsis@gmail.com'},
                {'subscriber': u'mail', 'name': u'Geolf', 'email': u'info.geolf@gmail.com'},
                {'subscriber': u'mail', 'name': u'Ludimus', 'email': u'ludimus@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'De Passe Simple', 'email': u'depassesimple@gmail.com'},
                {'subscriber': u'mail', 'name': u'Eureka', 'email': u'eurekalinjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'Sturm Und Drang', 'email': u'sturmunddrang.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Theodor', 'email': u'theodor.arkeologi@gmail.com'},
                {'subscriber': u'mail', 'name': u'Kwakiutl', 'email': u'sosant.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Primetime', 'email': u'primetime.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Akwaaba', 'email': u'akwaabapost.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Jump Cut', 'email': u'jumpcut.dragvoll@gmail.com'},
                {'subscriber': u'mail', 'name': u'Panoptikon', 'email': u'tverrfagligkult@gmail.com'},
                {'subscriber': u'mail', 'name': u'Kultura', 'email': u'kulturalinjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'Gengangere', 'email': u'gengangere@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Pareto', 'email': u'pareto.linjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'Dionysos', 'email': u'dionysoslinjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'De Folkevalgte', 'email': u'defolkevalgte@gmail.com'},
                {'subscriber': u'mail', 'name': u'Apeiron', 'email': u'apeiron.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Psykolosjen', 'email': u'psykolosjen@gmail.com'},
                {'subscriber': u'mail', 'name': u'Det Historiske Selskab', 'email': u'ntnu_dhs@hotmail.com'},
                {'subscriber': u'', 'name': u'Timini', 'email': u'styret@timini.no'},
                {'subscriber': u'mail', 'name': u'LiMP', 'email': u'linjeforeningen.limp@gmail.com'},
                {'subscriber': u'mail', 'name': u'Ivrig', 'email': u'ivrig.linjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'Emil', 'email': u'styret@emilweb.no'},
                {'subscriber': u'mail', 'name': u'Solan', 'email': u'solan@entreprenorskolen.no'},
                {'subscriber': u'mail', 'name': u'Teaterlosjen', 'email': u'teaterlosjen@gmail.com'}
            ]},
            {'name': 'dragvoll', 'members': [
                {'subscriber': u'mail', 'name': u'Karrieredagen Dragvoll', 'email': u'post@karrieredagendragvoll.no'},
                {'subscriber': u'mail', 'name': u'Det Historiske Selskab', 'email': u'ntnu_dhs@hotmail.com'},
                {'subscriber': u'mail', 'name': u'CAF', 'email': u'idrett@hotmail.com'},
                {'subscriber': u'mail', 'name': u'ELF', 'email': u'ntnuelf@gmail.com'},
                {'subscriber': u'mail', 'name': u'PSI', 'email': u'psi.linjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'Katharsis', 'email': u'linjeforeningenkatharsis@gmail.com'},
                {'subscriber': u'mail', 'name': u'Geolf', 'email': u'info.geolf@gmail.com'},
                {'subscriber': u'mail', 'name': u'De Passe Simple', 'email': u'depassesimple@gmail.com'},
                {'subscriber': u'mail', 'name': u'Eureka', 'email': u'eurekalinjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'Sturm Und Drang', 'email': u'sturmunddrang.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Theodor', 'email': u'theodor.arkeologi@gmail.com'},
                {'subscriber': u'mail', 'name': u'Kwakiutl', 'email': u'sosant.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Primetime', 'email': u'primetime.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Akwaaba', 'email': u'akwaabapost.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Jump Cut', 'email': u'jumpcut.dragvoll@gmail.com'},
                {'subscriber': u'mail', 'name': u'Panoptikon', 'email': u'tverrfagligkult@gmail.com'},
                {'subscriber': u'mail', 'name': u'Kultura', 'email': u'kulturalinjeforening@gmail.com'},
                {'subscriber': u'', 'name': u'Teaterlosjen', 'email': u'teaterlosjen@gmail.com'},
                {'subscriber': u'mail', 'name': u'Pareto', 'email': u'pareto.linjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'Dionysos', 'email': u'dionysoslinjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'De Folkevalgte', 'email': u'defolkevalgte@gmail.com'},
                {'subscriber': u'mail', 'name': u'Apeiron', 'email': u'apeiron.ntnu@gmail.com'},
                {'subscriber': u'mail', 'name': u'Psykolosjen', 'email': u'psykolosjen@gmail.com'},
                {'subscriber': u'mail', 'name': u'Paideia', 'email': u'paideia@live.no'},
                {'subscriber': u'mail', 'name': u'Socius Extremus', 'email': u'socius.extremus@hotmail.no'},
                {'subscriber': u'mail', 'name': u'Erudio', 'email': u'erudiostyret@hotmail.com'},
                {'subscriber': u'mail', 'name': u'Studentrådet SVT', 'email': u'svt@studentrad.no'},
                {'subscriber': u'mail', 'name': u'LiMP', 'email': u'linjeforeningen.limp@gmail.com'},
                {'subscriber': u'mail', 'name': u'Ivrig', 'email': u'ivrig.linjeforening@gmail.com'},
                {'subscriber': u'mail', 'name': u'Studentrådet HF', 'email': u'hf@studentrad.no'},
                {'subscriber': u'mail', 'name': u'Ludimus', 'email': u'ludimus@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Gengangere', 'email': u'gengangere@list.stud.ntnu.no'}
            ]},
            {'name': 'gloshaugen', 'members': [
                {'subscriber': u'mail', 'name': u'Hybrida', 'email': u'styret@hybrida.no'},
                {'subscriber': u'mail', 'name': u'Volvox', 'email': u'volvox-styre@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Delta', 'email': u'delta@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Alf', 'email': u'alf-styret@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Mannhullet', 'email': u'styret@mannhullet.no'},
                {'subscriber': u'mail', 'name': u'Spanskrøret', 'email': u'styre@spanskroret.no'},
                {'subscriber': u'mail', 'name': u'Aarhønen', 'email': u'hs@aarhonen.no'},
                {'subscriber': u'mail', 'name': u'Timini', 'email': u'styret@timini.no'},
                {'subscriber': u'mail', 'name': u'Smørekoppen', 'email': u'styret@smorekoppen.no'},
                {'subscriber': u'mail', 'name': u'Online', 'email': u'online@online.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Nabla', 'email': u'nabla@nabla.ntnu.no'},
                {'subscriber': u'mail', 'name': u'HC', 'email': u'styret@hc.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Janus', 'email': u'janus@org.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Bergstuderendes Forening', 'email': u'bsf@org.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Emil', 'email': u'styret@emilweb.no'},
                {'subscriber': u'mail', 'name': u'Leonardo', 'email': u'leonardo-styret@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Omega', 'email': u'omega@omega.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Placebo', 'email': u'placebo@list.stud.ntnu.no'},
                {'subscriber': u'', 'name': u'Solan', 'email': u'solan@entreprenorskolen.no'},
                {'subscriber': u'mail', 'name': u'Abakus', 'email': u'abakus@abakus.no'}
            ]},
            {'name': 'kjellere', 'members': [
                {'subscriber': u'', 'name': u'Smørekoppen', 'email': u'kjellersjef@smorekoppen.no'},
                {
                    'subscriber': u'',
                    'name': u'Bergstuderendes Forening Kjellersjef',
                    'email': u'bsf-kjellersjef@org.ntnu.no'
                },
                {'subscriber': u'', 'name': u'Hybrida', 'email': u'hybrida-kjeller@org.ntnu.no'},
                {'subscriber': u'', 'name': u'Dragvoll Kjelleren', 'email': u'dragvollkjelleren@gmail.com'},
                {'subscriber': u'', 'name': u'ICOT', 'email': u'icot09@gmail.com'},
                {'subscriber': u'', 'name': u'Emil Kjellern', 'email': u'emilkjelleren@gmail.com'},
                {'subscriber': u'', 'name': u'Lauget', 'email': u'lauget-barsjef@list.stud.ntnu.no'},
                {'subscriber': u'', 'name': u'De Taktlause', 'email': u'taktlaus-kjeller@list.stud.ntnu.no'},
                {'subscriber': u'', 'name': u'HC', 'email': u'kjellerstyret@hc.ntnu.no'},
                {'subscriber': u'', 'name': u'Timini', 'email': u'kjellersjef@timini.no'},
                {'subscriber': u'', 'name': u'Dykkergruppa', 'email': u'kjellersjef@dykkergruppa.no'},
                {'subscriber': u'', 'name': u'Nabla', 'email': u'kjellersjef@nabla.ntnu.no'},
                {'subscriber': u'', 'name': u'LaBamba', 'email': u'kjellersjef@abakus.no'},
                {'subscriber': u'', 'name': u'Omega', 'email': u'kielder@omega.ntnu.no'},
                {'subscriber': u'', 'name': u'Mannhullet', 'email': u'kjellersjef@mannhullet.no'},
                {'subscriber': u'', 'name': u'Janus Kjellersjef', 'email': u'janus-kjellersjef@org.ntnu.no'},
                {
                    'subscriber': u'',
                    'name': u'Realfagskjellern',
                    'email': u'realfagskjellern-kjellersjef@list.stud.ntnu.no'
                },
                {'subscriber': u'', 'name': u'isu-orga', 'email': u'isu-orga@list.stud.ntnu.no'},
                {'subscriber': u'', 'name': u'Aarhønen', 'email': u'aarhonen-krosjef@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'NTNUI', 'email': u'solveig.blandkjenn@gmail.com'},
                {'subscriber': u'mail', 'name': u'Psykolosjen', 'email': u'psykolosjen@gmail.com'}
            ]},
            {'name': 'foreninger', 'members': [
                {'subscriber': u'', 'name': u'NTNUI', 'email': u'hovedstyret@ntnui.no'},
                {'subscriber': u'', 'name': u'Radio Revolt', 'email': u'post@radiorevolt.no'},
                {'subscriber': u'', 'name': u'Styret i Samfundet', 'email': u'styret@samfundet.no'},
                {'subscriber': u'', 'name': u'Student-TV', 'email': u'styret@stv.no'},
                {'subscriber': u'', 'name': u'Under Dusken', 'email': u'styret@underdusken.no'},
                {'subscriber': u'', 'name': u'Velferdstinget', 'email': u'vt@velferdstinget.no'},
                {'subscriber': u'mail', 'name': u'Linjeforeninger på NTNU', 'email': u'linjeforeninger@online.ntnu.no'},
                {
                    'subscriber': u'mail',
                    'name': u'Masterforeninger på Gløshaugen',
                    'email': u'masterforeninger@online.ntnu.no'
                },
                {'subscriber': u'mail', 'name': u'Studenttinget', 'email': u'sti@studenttinget.no'}
            ]},
            {'name': 'masterforeninger', 'members': [
                {'subscriber': u'mail', 'name': u'Soma', 'email': u'soma@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Projeksjon', 'email': u'kontakt@projeksjon.no'},
                {'subscriber': u'mail', 'name': u'Symbiosis', 'email': u'symbiosis.board@gmail.com'},
                {'subscriber': u'mail', 'name': u'Signifikant', 'email': u'signifikant-styret@org.ntnu.no'},
                {'subscriber': u'', 'name': u'Solan', 'email': u'solan@entreprenorskolen.no'},
                {'subscriber': u'mail', 'name': u'Hippodamus', 'email': u'post@hippodamus.no'}
            ]},
            {'name': 'sr-samarbeid', 'members': [
                {'subscriber': u'', 'name': u'Studentrådet IME', 'email': u'studentrad_ime-medlem@org.ntnu.no'},
                {'subscriber': u'', 'name': u'Spanskrøret', 'email': u'styre@spanskroret.no'},
                {'subscriber': u'mail', 'name': u'Delta', 'email': u'delta@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Online', 'email': u'hovedstyret@online.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Abakus', 'email': u'hs@abakus.no'},
                {'subscriber': u'mail', 'name': u'Omega', 'email': u'hs@omega.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Nabla', 'email': u'nabla@nabla.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Emil', 'email': u'styret@emilweb.no'}
            ]},
            {'name': 'ivt-samarbeid', 'members': [
                {'subscriber': u'mail', 'name': u'Mannhullet', 'email': u'styret@mannhullet.no'},
                {'subscriber': u'mail', 'name': u'Aarhønen', 'email': u'hs@aarhonen.no'},
                {'subscriber': u'mail', 'name': u'Studentrådet IVT', 'email': u'ivt@studentradet.no'},
                {'subscriber': u'mail', 'name': u'Hybrida', 'email': u'hybrida@org.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Smørekoppen', 'email': u'smore-styret@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'BSF', 'email': u'bsf@org.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Teknologiporten', 'email': u'post@teknologiporten.no'},
                {'subscriber': u'mail', 'name': u'Leonardo', 'email': u'leonardo-hs@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Emil', 'email': u'styret@emilweb.no'}
            ]},
            {'name': 'linjeledere', 'members': [
                {'subscriber': u'mail', 'name': u'Timini', 'email': u'buckminister@timini.no'},
                {'subscriber': u'mail', 'name': u'Nabla', 'email': u'leder@nabla.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Placebo', 'email': u'placebo-leder@org.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Omega', 'email': u'stormeister@omega.ntnu.no'},
                {'subscriber': u'', 'name': u'Smørekoppen', 'email': u'phormand@smorekoppen.no'},
                {'subscriber': u'mail', 'name': u'Hybrida', 'email': u'leder@hybrida.no'},
                {'subscriber': u'', 'name': u'Janus', 'email': u'janus-president@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Leonardo', 'email': u'leonardo-leder@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Solan', 'email': u'solan-leder@entreprenorskolen.no'},
                {'subscriber': u'', 'name': u'Tidligere Linjeledere', 'email': u'bakbenken@online.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Spanskrøret', 'email': u'rektor@spanskroret.no'},
                {'subscriber': u'mail', 'name': u'Mannhullet', 'email': u'formann@mannhullet.no'},
                {'subscriber': u'mail', 'name': u'Abakus', 'email': u'leder@abakus.no'},
                {'subscriber': u'mail', 'name': u'Emil', 'email': u'leder@emilweb.no'},
                {'subscriber': u'mail', 'name': u'Online', 'email': u'leder@online.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Volvox', 'email': u'volvox-leder@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Aarhønen', 'email': u'aarhonen-kanzler@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Berg', 'email': u'bsf-leder@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'Delta', 'email': u'delta.leder@gmail.com'},
                {'subscriber': u'mail', 'name': u'Alf', 'email': u'alf-leder@list.stud.ntnu.no'},
                {'subscriber': u'mail', 'name': u'HC', 'email': u'phormand@hc.ntnu.no'}
            ]}
        ]

    return render(request, 'mailinglists/index.html', {'lists': lists}) 
