from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.views import View
from django.shortcuts import render
from .models import Post, Product, Category, Comment
from django.db import transaction, connection
from rest_framework import generics, viewsets
from .serializers import ProductSerializer, PostSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsOwnerOrReadOnly, IsAdmin, IsManager, IsEmployee
# Create your views here.


def fetch_data(model):
    return list(model.objects.all().values())

def get_posts(request):
    return JsonResponse({"posts": fetch_data(Post)})

def get_users(request):
    return JsonResponse({"users": fetch_data(User)})


class PostListView(View):
    def get(self, request):
        posts = Post.objects.prefetch_related('comments').all()
        return render(request, 'core/post_list.html', {'posts': posts})
    
    
class HomeView(View):
    def get(self, request):
        return HttpResponse("Hello, Django BootCamp!")
    
class apiView(View):
    def get(self, request):
        data = {
        "message": "Welcome to Django BootCamp API!",
        "status": "success"
        }
        return JsonResponse(data)
    

        
@transaction.atomic
def create_post_with_comments(post_data, comments_data):
    post = Post.objects.create(**post_data)
    for comment_data in comments_data:
        Comment.objects.create(post=post, **comment_data)

@transaction.atomic
def create_product_with_category(product_data, category_ids):
    product = Product.objects.create(**product_data)
    product.categories.set(category_ids)
    
def get_ranked_products():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, 
                RANK() OVER (ORDER BY price) AS price_rank 
            FROM product
        """)
        results = cursor.fetchall()
        
        
class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
        
class ProductRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    
class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
class PostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "You have access to this view!"})
    
class ProtectedJWTView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({"message": "This is a protected JWT view!"})
    

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    
class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        return Response({"message": "Only admins can see this!"})
    
class ManagerView(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    
    def get(self, request):
        return Response({"message": "welcome manager"})

class EmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    
    def get(self, request):
        return Response({"message": "welcome employee"})