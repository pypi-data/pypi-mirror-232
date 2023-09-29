from keycloak_django.security import ValidatePermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from ..utils.app_endpoints import get_endpoints


class GetEndpoints(APIView):
    # permission_classes = [IsAuthenticated, ValidatePermissions]
    permission_classes = []
    http_method_names = ['get']
    # validate_permissions = {'get': 'get_enpoints_allow_read'}

    def get(self, request, format=None):
        exclude = request.query_params('exclude')
        exclude = exclude.split(',') if exclude else []
        data = get_endpoints(exclude=exclude)
        return Response(data, status=status.HTTP_200_OK)