##coding:utf-8
#from rest_framework import generics, viewsets, mixins, status
#from rest_framework.response import Response
#from rest_framework.views import APIView
#from apps.apis.serializers import *
#
#
#class LoginViewSet(APIView):
#    queryset = User.objects.all()
#    serializer_class = LoginSerializer
#
#    def post(self, request):
#        try:
#            username = request.data.get('username')
#            password = request.data.get('password')
#            user = User.objects.get(username__iexact=username)
#            if user.check_password(password):
#                print user
#                serializer = LoginSerializer({'id': user.id, 'username': user.username})
#                return Response(serializer.data)
#            return Response(status=status.HTTP_401_UNAUTHORIZED)
#        except User.DoesNotExist:
#            return Response(status=status.HTTP_401_UNAUTHORIZED)
