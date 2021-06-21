from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from django.core.validators import validate_email
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework.response import Response

from api.services import create_customer, update_customer
from api.serializers import CustomerSerializer


class RegestrationApi(APIView):
    '''
    check credentials and create/update customer
    '''
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if create_customer(serializer.validated_data):
            return Response({"created": "yes"}, status=200)
        return Response({"created": "no"}, status=400)

    def update(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if update_customer(serializer.validated_data):
            return Response({"updated": "yes"}, status=200)
        return Response({"updated": "no"}, status=400)