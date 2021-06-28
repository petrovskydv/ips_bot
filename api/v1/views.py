from rest_framework.views import APIView
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
    # test diff 1
    # test diff 2
    # test diff 4
    # test diff 5
    # test diff 6
    # test diff 7
    # test diff 16
    # test diff 8
    # test diff 10
    def update(self, request):
        serializer = CustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if update_customer(serializer.validated_data):
            return Response({"updated": "yes"}, status=200)
        return Response({"updated": "no"}, status=400)
