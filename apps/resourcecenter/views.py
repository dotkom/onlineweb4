#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext

# from memcache import Client ############ ?

# Index page
def index(request):
	return render_to_response('resourcecenter/index.html', context_instance=RequestContext(request))
# Subpages
def gameservers(request):
	return render_to_response('resourcecenter/gameservers.html', context_instance=RequestContext(request))



def mailinglists(request):
    return render_to_response('resourcecenter/mailinglists.html', context_instance=RequestContext(request))

#     mc = Client(["127.0.0.1:11211"], debug=0)
#     retningslinjer = u"""
# Disse retningslinjene gjelder listene på denne siden.

# Hensikten med disse epostlistene er å fremme kommunikasjon mellom foreningene og å skape en kanal for å kunne kontakte alle foreningene på en enkel måte.

# Ettersom disse epostlistene distribueres til flere hundre brukere, bør post på disse listene begrenses til informasjon som kommer fellesskapet til gode. Dette gjelder gjerne informasjon om hendelser og arrangementer, som er interessant å avertere fordi det appellerer til studentmassen og/eller avgjørelser i de respektive styrene som mottar post fra listene.

# Gode eksempler på listemateriale:
# - Invitasjoner til jubileum, ball, revy etc.
# - Nyheter som påvirker linjeforeningene.

# Epost som gjelder jobbtilbud, reklame og annen avertering skal ikke komme på disse listene. Meldinger uten noe faktisk relevant innhold for linjeforeningene direkte som kommer ut på disse listene kan medføre advarsler, utestenging eller annen inndragelse av rettigheter.
# Vi (Online) ønsker ikke å sensurere meldinger, da det kan være vanskelig å bedømme hva andre synes er relevant. Vi ber derfor folk tenke seg nøye om før man bruker listene.
#     """
#     lists = mc.get("sympa_lists")
#     return render(request, 'mailinglists/index.html', {'lists': lists, 'retningslinjer': retningslinjer}) 

