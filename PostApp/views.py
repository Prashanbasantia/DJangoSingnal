## import from Django 
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import login as log_in, logout as log_out
from django.core.exceptions import ObjectDoesNotExist



#import from restframework

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

#import from PostApp

from .models import Posts
from .serializers import UserSerializer, PostsSerializer
from .pagination import CustomPagination

# Create your views here.


class SignupView(APIView):
    '''
        User Signup Api view 
        Accept POST METHOD only
        required data ['first_name', 'last_name', 'username', 'email', 'password']

    '''
    permission_classes = (AllowAny, )
    authentication_classes = []

    def post(self, request):
        if request.user.is_authenticated:
            resp_data = {'success': False, "message": "User Already Logedin"}
            return Response(resp_data, status=400)
        
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        username = request.data.get("username", None)
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        if not all([first_name, last_name, username, email, password]):
            response = {'success': False, "message": "Required All Fields"}
            return Response(response, status=400)
        
        if User.objects.filter(username=username).exists():
            response = {
                'success': False,
                "message": f"Username {username} already exists."
            }
            return Response(response, status=400)
        if User.objects.filter(email=email).exists():
            response = {'success': False, "message": f"Email {email} already exists."}
            return Response(response, status=400)
        try:
            instance = User.objects.create_user(
                username=username, email=email,
                first_name=first_name, last_name=last_name,
                password=password, is_staff=True, 
                is_active=True, is_superuser = False
                )
            if request.session:
                request.session.clear()
            log_in(request, instance)
            data = UserSerializer(instance).data
            response = {
                'success': True,
                "message": "User Signup Successfully",
                "data": data
            }
            return Response(response, status = 200)
        except Exception as e:
            resp_data = {'success': False, "message": f"Server Error {e}"}
            return Response(resp_data, status=400)


class LoginView(APIView):
    permission_classes = (AllowAny, )
    authentication_classes = []

    def post(self, request):
        if request.user.is_authenticated:
            response = {'success': False, "message": "User Already Logedin"}
            return Response(response, status=400)
        username = request.data.get("username")
        password = request.data.get("password")
        if not username:
            response = {'success': False, "message": "Required username"}
            return Response(response, status=400)
        if not password:
            response = {'success': False, "message": "Required password"}
            return Response(response, status=400)
        try:
            user_exist = User.objects.filter(Q(username=username) | Q(email=username), Q(is_superuser = False))
            if user_exist.exists():
                user = user_exist.first()
                if user.is_active == True:
                    if not user.check_password(password):
                        response = {
                            'success': False,
                            "message": "Invalid Credentials"
                        }
                        return Response(response, status=400)
                    log_in(request, user)
                    data = UserSerializer(user).data
                    response = {
                        'success': True,
                        "message": "Login Successfully",
                        "data": data
                    }
                else:
                    response = {
                        'success': False,
                        "message": "User Account Disbaled"
                    }
            else:
                response = {
                    'success': False,
                    "message": "Email or username not found"
                }
            return Response(response, status=400)
        except Exception as e:
            response = {'success': False, "message": f"Server Error {e}"}
            return Response(response, status=400)


class LogoutView(APIView):
    permission_classes = (AllowAny, )
    authentication_classes = []

    def get(self, request):
        try:
            log_out(request)
            response = {
                'success': True,
                "message": "Logout successfully"
            }
            return Response(response, status=400)
        except Exception as e:
            response = {'success': False, "message": f"Server Error {e}"}
            return Response(response, status=400)


class UserProfileView(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        try:
            response = {
                'success': True,
                "message": "User Profile Get successfully",
                "data":self.serializer_class(request.user).data
            }
            return Response(response, status=400)
        except Exception as e:
            response = {'success': False, "message": f"Server Error {e}"}
            return Response(response, status=400)



class PostsView(APIView, CustomPagination):
    serializer_class = PostsSerializer

    def get(self, request, id=None):
        try:
            if id:
                instance = Posts.objects.get(id=id, author = request.user)
                data = self.serializer_class(instance).data
                response = {
                    "success": True,
                    "message": "Posts Get Succesfully",
                    "data": data
                }
            else:
                if query := request.GET.get("query"):
                    instance = (
                        Posts.objects.select_related("author")
                        .filter(
                            Q(title__icontains=query) | Q(body__icontains=query),
                            Q(author=request.user.id),
                        ).order_by("-created_at")
                    )
                else:
                    instance = instance = (
                        Posts.objects.select_related("author")
                        .filter(author=request.user.id)
                        .order_by("-created_at")
                    )

                if request.GET.get('page'): 
                    page = self.paginate_queryset(instance, request, view=self)
                    serializer = self.serializer_class(page, many=True)
                    result = self.get_paginated_response(serializer.data)
                    data = result.data["results"]  # pagination data
                    total = result.data["count"]  # pagination data
                else:
                    serializer = self.serializer_class(instance, many=True)
                    data = serializer.data
                    total = instance.count()
                response = {
                    "success": True,
                    "message": "Posts List Get Succesfully",
                    "data": data,
                    "total": total
                }
            return Response(response, status=200)
        except ObjectDoesNotExist:
            response = {"success": False, "message": "Post not found!"}
            return Response(response, status=400)

    def post(self, request):
        try:
            author = request.user
            data = request.data
            title = data.get("title", None)
            body = data.get("body", None)
            if not title:
                response = {
                    "success": False,
                    "message": "Required Title",
                }
                return Response(response, status=400)
            if not body:
                response = {
                    "success": False,
                    "message": "Required Body",
                }
                return Response(response, status=400)
            
            instance = Posts.objects.create(title=title,body=body,author=author)
            response = {
                "success": True,
                "message": "Post Created  Successfully",
                "data": self.serializer_class(instance).data
            }
            return Response(response, status=201)
        except Exception as e:
            response = {"success": False,"message": str(e)}
            return Response(response, status=400)

    def put(self, request, id):
        try:
            data = request.data
            user = request.user
            title = data.get("title", None)
            body = data.get("body", None)
            if not title:
                response = {
                    "success": False,
                    "message": "Required Title",
                }
                return Response(response, status=400)
            if not body:
                response = {
                    "success": False,
                    "message": "Required Body",
                }
                return Response(response, status=400)

            instance = Posts.objects.get(id=id, author = user)
            instance.title = title
            instance.body = body
            instance.save()
            response = {
                "success": True,
                "message": "Post Updated successfully",
                "data":self.serializer_class(instance).data
            }
            return Response(response, status=200)
        except ObjectDoesNotExist:
            response = {"success": False, "message": "Post not found!"}
            return Response(response, status=400)

    def delete(self, request, id):
        try:
            Posts.objects.get(id=id, author = request.user).delete()
            response = {
                "success": True,
                "message": "Post Deleted Successfully",
            }
            return Response(response, status=200)
        except ObjectDoesNotExist:
            response = {"success": False, "message": "Post not found!"}
            return Response(response, status=400)
