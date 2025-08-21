import json, asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .vector_store import search_emotions
from .webrtc import handle_offer, close_session
from django.http import JsonResponse
from .models import Person

def persons_list(request):
    persons = Person.objects.all().values("id", "face_id")
    return JsonResponse(list(persons), safe=False)
# --- WebRTC signaling ---
@csrf_exempt
@permission_classes([AllowAny])   # keep open in dev; add JWT later
@api_view(['POST'])
def webrtc_offer(request):
    data = json.loads(request.body.decode('utf-8'))
    session_id, local_desc = asyncio.run(handle_offer(data["sdp"], data["type"]))
    return JsonResponse({"sdp": local_desc.sdp, "type": local_desc.type, "session_id": session_id})

@api_view(['POST'])
def webrtc_stop(request):
    data = json.loads(request.body.decode('utf-8'))
    ok = asyncio.run(close_session(data["session_id"]))
    return JsonResponse({"stopped": ok})

# --- Vector DB search (JWT protected) ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def emotion_search_view(request):
    data = json.loads(request.body.decode('utf-8'))
    vec = [float(x) for x in data["vector"]]
    k = int(data.get("k", 5))
    pid = data.get("person_id")
    res = search_emotions(vec, k=k, person_id=pid)
    return JsonResponse(res)
