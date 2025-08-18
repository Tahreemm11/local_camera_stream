# stream/api_views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Person
from .serializers import PersonSerializer

@api_view(['GET'])
def persons_list(request):
    persons = Person.objects.all()
    s = PersonSerializer(persons, many=True)
    data = s.data
    # add percentage per expression
    for p in data:
        total = p['total_detections'] or 0
        for expr in p['expressions']:
            expr['percentage'] = round((expr['count'] / total * 100) if total > 0 else 0, 2)
    return Response(data)
