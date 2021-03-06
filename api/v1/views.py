from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CustomerSerializer, DateSerializer
from api.services import (
    fetch_customer_profile, change_tariff, login_to_netup, normalize_customer_data, fetch_tariffs,
    fetch_tariff_info, fetch_available_tariffs_info, logout_from_netup, connect_tariff,
    make_promised_payment, fetch_promised_payment_status, fetch_payment_history, set_suspend,
    fetch_suspension_settings, disable_suspension
)
from content.models import Customer


class LoginApi(APIView):

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        normalized_data = normalize_customer_data(serializer.validated_data)
        result = login_to_netup(normalized_data)
        if result['success']:
            return Response({"login": True}, status=200)
        return Response({"login": False}, status=400)


class LogoutApi(APIView):

    def post(self, request):
        result = logout_from_netup(request.data['tg_chat_id'])
        if result['success']:
            return Response({"logout": True}, status=200)
        return Response({"logout": False}, status=400)


class FetchCustomerInfo(APIView):

    def post(self, request):
        tg_chat_id = request.data['tg_chat_id']
        customer_info = fetch_customer_profile(tg_chat_id)
        return Response(customer_info, status=200)


class ChangeTariff(APIView):

    def post(self, request):
        tg_chat_id = request.data['tg_chat_id']
        new_tariff_id = request.data['new_tariff_id']
        old_tariff_id = request.data['old_tariff_id']
        is_changed = change_tariff(tg_chat_id, new_tariff_id, old_tariff_id)
        if is_changed:
            return Response({"changed": is_changed}, status=200)
        return Response({"changed": is_changed}, status=400)


@api_view(['POST'])
def fetch_tariffs_view(request):
    tg_chat_id = request.data['tg_chat_id']
    tariffs = fetch_tariffs(tg_chat_id)
    return Response(tariffs, status=200)


@api_view(['POST'])
def fetch_tariff(request):
    tg_chat_id = request.data['tg_chat_id']
    tariff_id = request.data['tariff_id']
    tariff_info = fetch_tariff_info(tg_chat_id, tariff_id)
    return Response(tariff_info, status=200)


@api_view(['POST'])
def fetch_available_tariffs_view(request):
    tariff_id = request.data['tariff_id']
    available_tariffs = fetch_available_tariffs_info(tariff_id)
    return Response(available_tariffs, status=200)


@api_view(['POST'])
def add_tariff(request):
    tg_chat_id = request.data['tg_chat_id']
    tariff_id = request.data['tariff_id']
    result = connect_tariff(tg_chat_id, tariff_id)
    if result:
        return Response({"added": result}, status=200)
    return Response({"added": result}, status=400)


@api_view(['POST'])
def make_promised_payment_view(request):
    tg_chat_id = request.data['tg_chat_id']
    value = request.data['value']
    result = make_promised_payment(tg_chat_id, value)
    if result:
        return Response({"payed": result}, status=200)
    return Response({"payed": result}, status=400)


@api_view(['POST'])
def check_promised_payment_view(request):
    tg_chat_id = request.data['tg_chat_id']
    result = fetch_promised_payment_status(tg_chat_id)
    return Response(result, status=200)


@api_view(['POST'])
def fetch_payment_history_view(request):
    tg_chat_id = request.data['tg_chat_id']
    result = fetch_payment_history(tg_chat_id)
    return Response(result, status=200)


class CheckDate(APIView):

    def post(self, request):
        serializer = DateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)


class SetSuspend(APIView):

    def post(self, request):
        tg_chat_id = request.data.pop('tg_chat_id')
        serializer = DateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if set_suspend(tg_chat_id, serializer.validated_data):
                return Response(
                    {
                        'success': True,
                        'start_date': serializer.validated_data['start_date'],
                        'end_date': serializer.validated_data['end_date']
                    },
                    status=200
                )
            return Response({'success': False}, status=400)


@api_view(['POST'])
def suspension_settings(request):
    tg_chat_id = request.data['tg_chat_id']
    result = fetch_suspension_settings(tg_chat_id)
    return Response(result, status=200)


@api_view(['POST'])
def suspension_disable(request):
    tg_chat_id = request.data['tg_chat_id']
    result = disable_suspension(tg_chat_id)
    return Response({'success': result}, status=200)


@api_view(['POST'])
def check_authentication(request):
    tg_chat_id = request.data['tg_chat_id']
    if Customer.objects.filter(tg_chat_id=tg_chat_id).count() == 0:
        return Response({'authenticated': False}, status=200)
    return Response({'authenticated': True}, status=200)
