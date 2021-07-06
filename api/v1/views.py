from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from api.services import (create_customer, update_customer, fetch_customer_profile, change_tariff, login_to_netup,
                          normalize_customer_data, fetch_tariffs)
from api.serializers import CustomerSerializer, TariffSerializer


class RegistrationApi(APIView):
    '''
    dead branch at this moment
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


class LoginApi(APIView):

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = normalize_customer_data(serializer.validated_data)
        result = login_to_netup(validated_data)
        customer_info = 'gogogogo'
        # customer_info = fetch_customer_profile(validated_data, result['is_new_customer'])
        if result['success']:
            return Response({"login": "yes", 'customer_info': customer_info}, status=200)
        return Response({"login": "no"}, status=400)


class ChangeTariff(APIView):

    def post(self, request):
        serializer = TariffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if change_tariff(serializer.validated_data):
            return Response({"changed": "yes"}, status=200)
        return Response({"changed": "no"}, status=400)


@api_view(['GET'])
def fetch_tariffs_view(request):
    tariffs = fetch_tariffs()
    return Response(tariffs, status=200)
