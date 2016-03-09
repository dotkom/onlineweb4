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
                {'subscriber': '', 'name': 'Alf', 'email': 'alf-styret@list.stud.ntnu.no'},
                {'subscriber': '', 'name': 'Smørekoppen', 'email': 'styret@smorekoppen.no'},
                {'subscriber': '', 'name': 'Abakus', 'email': 'abakus@abakus.no'},
                {'subscriber': '', 'name': 'Omega', 'email': 'omega@omega.ntnu.no'},
                {'subscriber': '', 'name': 'Bergstuderendes Forening', 'email': 'bsf@org.ntnu.no'},
                {'subscriber': '', 'name': 'Delta', 'email': 'delta@list.stud.ntnu.no'},
                {'subscriber': '', 'name': 'Aarhønen', 'email': 'hs@aarhonen.no'},
                {'subscriber': '', 'name': 'Hybrida', 'email': 'hybrida@org.ntnu.no'},
                {'subscriber': '', 'name': 'Janus', 'email': 'janus@org.ntnu.no'},
                {'subscriber': '', 'name': 'Online', 'email': 'online@online.ntnu.no'},
                {'subscriber': '', 'name': 'Placebo', 'email': 'placebo@list.stud.ntnu.no'},
                {'subscriber': '', 'name': 'Spanskrøret', 'email': 'styre@spanskroret.no'},
                {'subscriber': '', 'name': 'HC', 'email': 'styret@hc.ntnu.no'},
                {'subscriber': '', 'name': 'Mannhullet', 'email': 'styret@mannhullet.no'},
                {'subscriber': '', 'name': 'Volvox', 'email': 'volvox-styre@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Socius Extremus', 'email': 'socius.extremus@hotmail.no'},
                {'subscriber': '', 'name': 'Nabla', 'email': 'nabla@nabla.ntnu.no'},
                {'subscriber': '', 'name': 'Leonardo', 'email': 'leonardo-styret@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Erudio', 'email': 'erudiostyret@hotmail.com'},
                {'subscriber': 'mail', 'name': 'Paideia', 'email': 'paideia@live.no'},
                {'subscriber': 'mail', 'name': 'CAF', 'email': 'idrett@hotmail.com'},
                {'subscriber': 'mail', 'name': 'ELF', 'email': 'ntnuelf@gmail.com'},
                {'subscriber': 'mail', 'name': 'PSI', 'email': 'psi.linjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'Katharsis', 'email': 'linjeforeningenkatharsis@gmail.com'},
                {'subscriber': 'mail', 'name': 'Geolf', 'email': 'info.geolf@gmail.com'},
                {'subscriber': 'mail', 'name': 'Ludimus', 'email': 'ludimus@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'De Passe Simple', 'email': 'depassesimple@gmail.com'},
                {'subscriber': 'mail', 'name': 'Eureka', 'email': 'eurekalinjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'Sturm Und Drang', 'email': 'sturmunddrang.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Theodor', 'email': 'theodor.arkeologi@gmail.com'},
                {'subscriber': 'mail', 'name': 'Kwakiutl', 'email': 'sosant.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Primetime', 'email': 'primetime.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Akwaaba', 'email': 'akwaabapost.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Jump Cut', 'email': 'jumpcut.dragvoll@gmail.com'},
                {'subscriber': 'mail', 'name': 'Panoptikon', 'email': 'tverrfagligkult@gmail.com'},
                {'subscriber': 'mail', 'name': 'Kultura', 'email': 'kulturalinjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'Gengangere', 'email': 'gengangere@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Pareto', 'email': 'pareto.linjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'Dionysos', 'email': 'dionysoslinjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'De Folkevalgte', 'email': 'defolkevalgte@gmail.com'},
                {'subscriber': 'mail', 'name': 'Apeiron', 'email': 'apeiron.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Psykolosjen', 'email': 'psykolosjen@gmail.com'},
                {'subscriber': 'mail', 'name': 'Det Historiske Selskab', 'email': 'ntnu_dhs@hotmail.com'},
                {'subscriber': '', 'name': 'Timini', 'email': 'styret@timini.no'},
                {'subscriber': 'mail', 'name': 'LiMP', 'email': 'linjeforeningen.limp@gmail.com'},
                {'subscriber': 'mail', 'name': 'Ivrig', 'email': 'ivrig.linjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'Emil', 'email': 'styret@emilweb.no'},
                {'subscriber': 'mail', 'name': 'Solan', 'email': 'solan@entreprenorskolen.no'},
                {'subscriber': 'mail', 'name': 'Teaterlosjen', 'email': 'teaterlosjen@gmail.com'}
            ]},
            {'name': 'dragvoll', 'members': [
                {'subscriber': 'mail', 'name': 'Karrieredagen Dragvoll', 'email': 'post@karrieredagendragvoll.no'},
                {'subscriber': 'mail', 'name': 'Det Historiske Selskab', 'email': 'ntnu_dhs@hotmail.com'},
                {'subscriber': 'mail', 'name': 'CAF', 'email': 'idrett@hotmail.com'},
                {'subscriber': 'mail', 'name': 'ELF', 'email': 'ntnuelf@gmail.com'},
                {'subscriber': 'mail', 'name': 'PSI', 'email': 'psi.linjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'Katharsis', 'email': 'linjeforeningenkatharsis@gmail.com'},
                {'subscriber': 'mail', 'name': 'Geolf', 'email': 'info.geolf@gmail.com'},
                {'subscriber': 'mail', 'name': 'De Passe Simple', 'email': 'depassesimple@gmail.com'},
                {'subscriber': 'mail', 'name': 'Eureka', 'email': 'eurekalinjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'Sturm Und Drang', 'email': 'sturmunddrang.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Theodor', 'email': 'theodor.arkeologi@gmail.com'},
                {'subscriber': 'mail', 'name': 'Kwakiutl', 'email': 'sosant.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Primetime', 'email': 'primetime.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Akwaaba', 'email': 'akwaabapost.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Jump Cut', 'email': 'jumpcut.dragvoll@gmail.com'},
                {'subscriber': 'mail', 'name': 'Panoptikon', 'email': 'tverrfagligkult@gmail.com'},
                {'subscriber': 'mail', 'name': 'Kultura', 'email': 'kulturalinjeforening@gmail.com'},
                {'subscriber': '', 'name': 'Teaterlosjen', 'email': 'teaterlosjen@gmail.com'},
                {'subscriber': 'mail', 'name': 'Pareto', 'email': 'pareto.linjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'Dionysos', 'email': 'dionysoslinjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'De Folkevalgte', 'email': 'defolkevalgte@gmail.com'},
                {'subscriber': 'mail', 'name': 'Apeiron', 'email': 'apeiron.ntnu@gmail.com'},
                {'subscriber': 'mail', 'name': 'Psykolosjen', 'email': 'psykolosjen@gmail.com'},
                {'subscriber': 'mail', 'name': 'Paideia', 'email': 'paideia@live.no'},
                {'subscriber': 'mail', 'name': 'Socius Extremus', 'email': 'socius.extremus@hotmail.no'},
                {'subscriber': 'mail', 'name': 'Erudio', 'email': 'erudiostyret@hotmail.com'},
                {'subscriber': 'mail', 'name': 'Studentrådet SVT', 'email': 'svt@studentrad.no'},
                {'subscriber': 'mail', 'name': 'LiMP', 'email': 'linjeforeningen.limp@gmail.com'},
                {'subscriber': 'mail', 'name': 'Ivrig', 'email': 'ivrig.linjeforening@gmail.com'},
                {'subscriber': 'mail', 'name': 'Studentrådet HF', 'email': 'hf@studentrad.no'},
                {'subscriber': 'mail', 'name': 'Ludimus', 'email': 'ludimus@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Gengangere', 'email': 'gengangere@list.stud.ntnu.no'}
            ]},
            {'name': 'gloshaugen', 'members': [
                {'subscriber': 'mail', 'name': 'Hybrida', 'email': 'styret@hybrida.no'},
                {'subscriber': 'mail', 'name': 'Volvox', 'email': 'volvox-styre@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Delta', 'email': 'delta@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Alf', 'email': 'alf-styret@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Mannhullet', 'email': 'styret@mannhullet.no'},
                {'subscriber': 'mail', 'name': 'Spanskrøret', 'email': 'styre@spanskroret.no'},
                {'subscriber': 'mail', 'name': 'Aarhønen', 'email': 'hs@aarhonen.no'},
                {'subscriber': 'mail', 'name': 'Timini', 'email': 'styret@timini.no'},
                {'subscriber': 'mail', 'name': 'Smørekoppen', 'email': 'styret@smorekoppen.no'},
                {'subscriber': 'mail', 'name': 'Online', 'email': 'online@online.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Nabla', 'email': 'nabla@nabla.ntnu.no'},
                {'subscriber': 'mail', 'name': 'HC', 'email': 'styret@hc.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Janus', 'email': 'janus@org.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Bergstuderendes Forening', 'email': 'bsf@org.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Emil', 'email': 'styret@emilweb.no'},
                {'subscriber': 'mail', 'name': 'Leonardo', 'email': 'leonardo-styret@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Omega', 'email': 'omega@omega.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Placebo', 'email': 'placebo@list.stud.ntnu.no'},
                {'subscriber': '', 'name': 'Solan', 'email': 'solan@entreprenorskolen.no'},
                {'subscriber': 'mail', 'name': 'Abakus', 'email': 'abakus@abakus.no'}
            ]},
            {'name': 'kjellere', 'members': [
                {'subscriber': '', 'name': 'Smørekoppen', 'email': 'kjellersjef@smorekoppen.no'},
                {
                    'subscriber': '',
                    'name': 'Bergstuderendes Forening Kjellersjef',
                    'email': 'bsf-kjellersjef@org.ntnu.no'
                },
                {'subscriber': '', 'name': 'Hybrida', 'email': 'hybrida-kjeller@org.ntnu.no'},
                {'subscriber': '', 'name': 'Dragvoll Kjelleren', 'email': 'dragvollkjelleren@gmail.com'},
                {'subscriber': '', 'name': 'ICOT', 'email': 'icot09@gmail.com'},
                {'subscriber': '', 'name': 'Emil Kjellern', 'email': 'emilkjelleren@gmail.com'},
                {'subscriber': '', 'name': 'Lauget', 'email': 'lauget-barsjef@list.stud.ntnu.no'},
                {'subscriber': '', 'name': 'De Taktlause', 'email': 'taktlaus-kjeller@list.stud.ntnu.no'},
                {'subscriber': '', 'name': 'HC', 'email': 'kjellerstyret@hc.ntnu.no'},
                {'subscriber': '', 'name': 'Timini', 'email': 'kjellersjef@timini.no'},
                {'subscriber': '', 'name': 'Dykkergruppa', 'email': 'kjellersjef@dykkergruppa.no'},
                {'subscriber': '', 'name': 'Nabla', 'email': 'kjellersjef@nabla.ntnu.no'},
                {'subscriber': '', 'name': 'LaBamba', 'email': 'kjellersjef@abakus.no'},
                {'subscriber': '', 'name': 'Omega', 'email': 'kielder@omega.ntnu.no'},
                {'subscriber': '', 'name': 'Mannhullet', 'email': 'kjellersjef@mannhullet.no'},
                {'subscriber': '', 'name': 'Janus Kjellersjef', 'email': 'janus-kjellersjef@org.ntnu.no'},
                {
                    'subscriber': '',
                    'name': 'Realfagskjellern',
                    'email': 'realfagskjellern-kjellersjef@list.stud.ntnu.no'
                },
                {'subscriber': '', 'name': 'isu-orga', 'email': 'isu-orga@list.stud.ntnu.no'},
                {'subscriber': '', 'name': 'Aarhønen', 'email': 'aarhonen-krosjef@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'NTNUI', 'email': 'solveig.blandkjenn@gmail.com'},
                {'subscriber': 'mail', 'name': 'Psykolosjen', 'email': 'psykolosjen@gmail.com'}
            ]},
            {'name': 'foreninger', 'members': [
                {'subscriber': '', 'name': 'NTNUI', 'email': 'hovedstyret@ntnui.no'},
                {'subscriber': '', 'name': 'Radio Revolt', 'email': 'post@radiorevolt.no'},
                {'subscriber': '', 'name': 'Styret i Samfundet', 'email': 'styret@samfundet.no'},
                {'subscriber': '', 'name': 'Student-TV', 'email': 'styret@stv.no'},
                {'subscriber': '', 'name': 'Under Dusken', 'email': 'styret@underdusken.no'},
                {'subscriber': '', 'name': 'Velferdstinget', 'email': 'vt@velferdstinget.no'},
                {'subscriber': 'mail', 'name': 'Linjeforeninger på NTN', 'email': 'linjeforeninger@online.ntnu.no'},
                {
                    'subscriber': 'mail',
                    'name': 'Masterforeninger på Gløshaugen',
                    'email': 'masterforeninger@online.ntnu.no'
                },
                {'subscriber': 'mail', 'name': 'Studenttinget', 'email': 'sti@studenttinget.no'}
            ]},
            {'name': 'masterforeninger', 'members': [
                {'subscriber': 'mail', 'name': 'Soma', 'email': 'soma@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Projeksjon', 'email': 'kontakt@projeksjon.no'},
                {'subscriber': 'mail', 'name': 'Symbiosis', 'email': 'symbiosis.board@gmail.com'},
                {'subscriber': 'mail', 'name': 'Signifikant', 'email': 'signifikant-styret@org.ntnu.no'},
                {'subscriber': '', 'name': 'Solan', 'email': 'solan@entreprenorskolen.no'},
                {'subscriber': 'mail', 'name': 'Hippodamus', 'email': 'post@hippodamus.no'}
            ]},
            {'name': 'sr-samarbeid', 'members': [
                {'subscriber': '', 'name': 'Studentrådet IME', 'email': 'studentrad_ime-medlem@org.ntnu.no'},
                {'subscriber': '', 'name': 'Spanskrøret', 'email': 'styre@spanskroret.no'},
                {'subscriber': 'mail', 'name': 'Delta', 'email': 'delta@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Online', 'email': 'hovedstyret@online.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Abakus', 'email': 'hs@abakus.no'},
                {'subscriber': 'mail', 'name': 'Omega', 'email': 'hs@omega.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Nabla', 'email': 'nabla@nabla.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Emil', 'email': 'styret@emilweb.no'}
            ]},
            {'name': 'ivt-samarbeid', 'members': [
                {'subscriber': 'mail', 'name': 'Mannhullet', 'email': 'styret@mannhullet.no'},
                {'subscriber': 'mail', 'name': 'Aarhønen', 'email': 'hs@aarhonen.no'},
                {'subscriber': 'mail', 'name': 'Studentrådet IVT', 'email': 'ivt@studentradet.no'},
                {'subscriber': 'mail', 'name': 'Hybrida', 'email': 'hybrida@org.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Smørekoppen', 'email': 'smore-styret@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'BSF', 'email': 'bsf@org.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Teknologiporten', 'email': 'post@teknologiporten.no'},
                {'subscriber': 'mail', 'name': 'Leonardo', 'email': 'leonardo-hs@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Emil', 'email': 'styret@emilweb.no'}
            ]},
            {'name': 'linjeledere', 'members': [
                {'subscriber': 'mail', 'name': 'Timini', 'email': 'buckminister@timini.no'},
                {'subscriber': 'mail', 'name': 'Nabla', 'email': 'leder@nabla.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Placebo', 'email': 'placebo-leder@org.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Omega', 'email': 'stormeister@omega.ntnu.no'},
                {'subscriber': '', 'name': 'Smørekoppen', 'email': 'phormand@smorekoppen.no'},
                {'subscriber': 'mail', 'name': 'Hybrida', 'email': 'leder@hybrida.no'},
                {'subscriber': '', 'name': 'Janus', 'email': 'janus-president@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Leonardo', 'email': 'leonardo-leder@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Solan', 'email': 'solan-leder@entreprenorskolen.no'},
                {'subscriber': '', 'name': 'Tidligere Linjeledere', 'email': 'bakbenken@online.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Spanskrøret', 'email': 'rektor@spanskroret.no'},
                {'subscriber': 'mail', 'name': 'Mannhullet', 'email': 'formann@mannhullet.no'},
                {'subscriber': 'mail', 'name': 'Abakus', 'email': 'leder@abakus.no'},
                {'subscriber': 'mail', 'name': 'Emil', 'email': 'leder@emilweb.no'},
                {'subscriber': 'mail', 'name': 'Online', 'email': 'leder@online.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Volvox', 'email': 'volvox-leder@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Aarhønen', 'email': 'aarhonen-kanzler@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Berg', 'email': 'bsf-leder@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'Delta', 'email': 'delta.leder@gmail.com'},
                {'subscriber': 'mail', 'name': 'Alf', 'email': 'alf-leder@list.stud.ntnu.no'},
                {'subscriber': 'mail', 'name': 'HC', 'email': 'phormand@hc.ntnu.no'}
            ]}
        ]

    return render(request, 'mailinglists/index.html', {'lists': lists})
