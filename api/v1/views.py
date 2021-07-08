from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from api.services import (create_customer, update_customer, fetch_customer_profile, change_tariff, login_to_netup,
                          normalize_customer_data, fetch_tariffs)
from api.serializers import CustomerSerializer


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
        normalized_data = normalize_customer_data(serializer.validated_data)
        result = login_to_netup(normalized_data)
        if result['success']:
            return Response({"login": True}, status=200)
        return Response({"login": False}, status=400)


class FetchCustomerInfo(APIView):

    def post(self, request):
        tg_chat_id = request.data['tg_chat_id']
        customer_info = fetch_customer_profile(tg_chat_id)
        return Response(customer_info, status=200)


class ChangeTariff(APIView):

    def post(self, request):
        tg_chat_id = request.data['tg_chat_id']
        new_tariff_id = request.data['new_tariff_id']
        is_changed = change_tariff(tg_chat_id, new_tariff_id)
        if is_changed:
            return Response({"changed": is_changed}, status=200)
        return Response({"changed": is_changed}, status=400)


@api_view(['POST'])
def fetch_tariffs_view(request):
    tg_chat_id = request.data['tg_chat_id']
    tariffs = fetch_tariffs(tg_chat_id)
    return Response(tariffs, status=200)

