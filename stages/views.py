from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Stage
from .serializers import StageSerializer

# ViewSet pour les stages
class StageViewSet(viewsets.ModelViewSet):
    """
    Fournit tous les endpoints CRUD pour les stages.
    - GET /api/stages/ : liste
    - GET /api/stages/<id>/ : détails
    - POST /api/stages/ : création
    - PUT/PATCH /api/stages/<id>/ : modification
    - DELETE /api/stages/<id>/ : suppression
    """
    queryset = Stage.objects.all().order_by('-created_at')
    serializer_class = StageSerializer
    permission_classes =  [IsAuthenticated] # Lecture publique, modification sécurisée

    # Permet la recherche par titre, company ou category
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'company', 'category__name']