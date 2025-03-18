from django.shortcuts import render, get_object_or_404
from rest_framework.generics import CreateAPIView,ListAPIView
from api.serializers import (
    UserSerializer,
    SignInSerializer,
    FoodCategorySerializer,
    FoodSerializer,
    Seller,
    TableSerializer,
    CartSerializer,
    CheckoutSerializer,
    CartAddSerializer, 
    OrdersSerializer,
    OTPRequestSerializer
)
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import generics
from api.models import FoodCategory, Food, Table, Cart, Checkout,Orders
from rest_framework import status
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework import authentication, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
import razorpay
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from api.models import Checkout
from django.conf import settings
from django.db import transaction
from api.models import Table

# import razorpay


class SignUpView(CreateAPIView, ListAPIView):  # Added ListAPIView for GET
    serializer_class = UserSerializer
    queryset = Seller.objects.all()  # Define queryset for GET

    def get(self, request, *args, **kwargs):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SignInView(APIView):

    def post(self, request, *args, **kwargs):

        serializer = SignInSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data['user']
            
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                'access_token': access_token,
                'refresh_token': str(refresh),
                'user': user.username,
                'pin':user.pin,
                'owner':user.id,
                'is_verified':user.is_verified,
                'message': 'Login successfull'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FoodCategoryCreateView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        qs = FoodCategory.objects.filter(owner=request.user)
        serializer_instance = FoodCategorySerializer(qs, many=True)

        return Response(data=serializer_instance.data)

    def post(self, request, *args, **kwargs):

        serializer = FoodCategorySerializer(data=request.data)

        if serializer.is_valid():

            try:
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except IntegrityError:

                raise ValidationError({"message": "The category name already exists"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodCategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = FoodCategorySerializer
    queryset = FoodCategory.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        try:
            instance = self.get_object()
            serializer_instance = self.get_serializer(instance)
            return Response(serializer_instance.data, status=status.HTTP_200_OK)

        except Http404:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)


class FoodCreateListView(generics.ListCreateAPIView):

    serializer_class = FoodSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        qs = Food.objects.filter(owner=request.user)
        serializer_instance = FoodSerializer(qs, many=True)

        if serializer_instance:

            return Response(serializer_instance.data, status=status.HTTP_200_OK)
        return Response(serializer_instance.error, status=status.HTTP_400_BAD_REQUEST)


class FoodRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FoodSerializer
    queryset = Food.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


class TableCreateListView(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):
        user = request.user
        tables = Table.objects.filter(owner = user)
        return Response(TableSerializer(tables, many=True).data)

    def post(self, request, *args, **kwargs):
        user = request.user
        owner = user.id

        table_number = request.data.get('table_number')
        if not table_number:
            return Response({"error": "Table number is required."}, status=status.HTTP_400_BAD_REQUEST)

        table = Table.objects.create(owner = user, table_number=table_number)
        table.save()
        

        return Response(TableSerializer(table).data, status=status.HTTP_201_CREATED)


class TableUpdateView(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, table_id):
        user = request.user
        try:
            table = Table.objects.get(id=table_id, owner = user)
        except Table.DoesNotExist:
            return Response({"error": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

        table_number = request.data.get('table_number')
        is_occupied = request.data.get('is_occupied')

        if table_number is not None:
            table.table_number = table_number
        if is_occupied is not None:
            table.is_occupied = is_occupied

        table.save()
        return Response(TableSerializer(table).data)


class TableDeleteView(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, table_id):
        user = request.user
        try:
            table = Table.objects.get(id=table_id, owner = user)
        except Table.DoesNotExist:
            return Response({"error": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

        table.delete()
        return Response({"message": "Table deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class FoodCategoryMenuView(APIView):

    def get(self, request, *args, **kwargs):

        pin = kwargs.get("pin")
        try:
            owner = get_object_or_404(Seller, pin=pin)
        except:
            return Response(
                {"detail": "seller not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        food_category = FoodCategory.objects.filter(owner=owner)
        food_category_serializer = FoodCategorySerializer(food_category, many=True)

        # tables = Table.objects.filter(owner = owner)
        # tables_serializer_instance = TableSerializer(tables, many=True)

        return Response(
            {"seller": owner.username, "food_category": food_category_serializer.data}
        )


class FoodMenuView(APIView):

    def get(self, request, *args, **kwargs):

        pin = kwargs.get("pin")

        try:
            owner = get_object_or_404(Seller, pin=pin)
        except:
            return Response(
                {"detail": "seller not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        food_items = Food.objects.filter(owner=owner)
        food_serializer_instance = FoodSerializer(food_items, many=True)

        # food_category = FoodCategory.objects.filter(owner = owner)
        # food_category_serializer = FoodCategorySerializer(food_category, many=True)

        # tables = Table.objects.filter(owner = owner)
        # tables_serializer_instance = TableSerializer(tables, many=True)

        return Response(
            {"seller": owner.username, "food_items": food_serializer_instance.data}
        )


class TableMenuView(APIView):

    def get(self, request, *args, **kwargs):

        pin = kwargs.get("pin")

        try:
            owner = get_object_or_404(Seller, pin=pin)
        except:
            return Response(
                {"detail": "seller not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        tables = Table.objects.filter(owner=owner)
        tables_serializer_instance = TableSerializer(tables, many=True)

        return Response(
            {"seller": owner.username, "tables": tables_serializer_instance.data}
        )


class CartGetAPIView(APIView):
    # Get all cart items
    def get(self, request, table_id):
        id = Table.objects.get(id=table_id)
        carts = Cart.objects.filter(table_number=id)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartAPIView(APIView):
    # Add a new item to the cart
    def post(self, request):
        serializer = CartAddSerializer(data=request.data)
        if serializer.is_valid():
            food_id = serializer.validated_data["food"]
            table_id = serializer.validated_data["table_number"]
            quantity = serializer.validated_data["quantity"]

            # Check if the same product exists in the cart for the same table
            cart_item, created = Cart.objects.get_or_create(
                food=food_id, table_number=table_id,
                defaults={"quantity": quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                return Response(
                    {
                        "message": "Item quantity updated in cart",
                        "cart_id": cart_item.id,
                        "food_name": cart_item.food.food_name,
                        "food_image": cart_item.food.food_image.url if cart_item.food.food_image else None,
                        "food_price": cart_item.food.price,
                        "quantity": cart_item.quantity,
                        "table_number": cart_item.table_number.table_number,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "message": "Item added to cart",
                    "cart_id": cart_item.id,
                    "food_name": cart_item.food.food_name,
                    "food_image": cart_item.food.food_image.url if cart_item.food.food_image else None,
                    "food_price": cart_item.food.price,
                    "quantity": cart_item.quantity,
                    "table_number": cart_item.table_number.table_number,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    # Update a cart item
    def put(self, request, pk, *args, **kwargs):
        # Get the existing Cart object
        cart_instance = get_object_or_404(Cart, pk=pk)
        serializer = CartSerializer(cart_instance, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()
            # Refresh the instance to get updated related fields like food_name
            cart_instance.refresh_from_db()
            updated_serializer = CartSerializer(cart_instance)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a cart item
    def delete(self, request, pk):
        try:
            cart_item = Cart.objects.get(pk=pk)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        return Response(
            {"message": "Cart item deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class UpdateCartQuantityAPIView(APIView):
    def post(self, request, *args, **kwargs):

        cart_id = request.data.get("cart_id")
        action = request.data.get("action")

        try:
            cart_item = Cart.objects.get(id=cart_id)

            if action == "+":
                cart_item.quantity += 1
                cart_item.save()

            elif action == "-":
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()  # Remove item if quantity reaches 0
                    return Response(
                        {"message": "Item removed from cart"}, status=status.HTTP_200_OK
                    )

            return Response(
                {"cart_id": cart_item.id, "new_quantity": cart_item.quantity},
                status=status.HTTP_200_OK,
            )

        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckoutListCreateView(APIView):
    """
    View to list all checkouts or create a new checkout.
    """

    def get(self, request):
        checkouts = Checkout.objects.all()
        serializer = CheckoutSerializer(checkouts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new checkout instance.
        - Retrieves cart items for the table.
        - Links the cart items to the checkout.
        - Returns the checkout details.
        """
        table_number = request.data.get("table_number")  # Get table number from request

        # Get all cart items linked to this table
        cart_items = Cart.objects.filter(table_number__table_number=table_number)

        if not cart_items.exists():
            return Response(
                {"error": "No cart items found for this table."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create checkout instance and link cart items
        checkout = Checkout.objects.create()
        checkout.cart.set(cart_items)  # Add cart items to checkout

        serializer = CheckoutSerializer(checkout)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CheckoutDetailView(APIView):
    """
    View to retrieve or delete a checkout instance.
    """

    def get_object(self, pk):
        """
        Helper method to get the checkout object.
        """
        return get_object_or_404(Checkout, id=pk)

    def get(self, request, pk):
        """
        Retrieve a single checkout by ID.
        """
        checkout = self.get_object(pk)
        serializer = CheckoutSerializer(checkout)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Delete a checkout instance.
        """
        checkout = self.get_object(pk)
        try:
            with transaction.atomic():
                # Create an Order from Cart Items
                order = Orders.objects.create(
                    user=checkout.user,
                    seller=checkout.seller,
                    total_price=sum(item.food.price * item.quantity for item in checkout.cart.all()),
                    status="Paid"
                )

                # Move Cart Items to Order
                order_items = [
                    order.items.create(
                        food=cart_item.food,
                        quantity=cart_item.quantity,
                        price=cart_item.food.price
                    ) for cart_item in checkout.cart.all()
                ]

                checkout.delete()
                return Response(
                    {"message": "Checkout deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": f"Could not delete checkout: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        checkout_id = request.data.get("checkout_id")  # Get checkout ID from request
        checkout = get_object_or_404(Checkout, id=checkout_id)
        
        # Calculate total price
        total_price = sum(item.food.price * item.quantity for item in checkout.cart.all())
        amount = int(total_price * 100)  # Convert to paise (for Razorpay)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1
        })

        return Response({
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR'
        }, status=status.HTTP_200_OK)


class OrdersByPinAPIView(generics.ListAPIView):
    serializer_class = OrdersSerializer

    def get_queryset(self):
        pin = self.kwargs.get("pin")
        seller = get_object_or_404(Seller, pin=pin)
        return Orders.objects.filter(pin=seller, status="Paid")  # Show only paid orders


class VerifyPaymentView(APIView):
    """
    Verifies the payment and creates an order if payment is successful.
    """

    def post(self, request, *args, **kwargs):
        checkout_id = request.data.get("checkout_id")
        payment_id = request.data.get("payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            checkout = get_object_or_404(Checkout, id=checkout_id)

            # Verify payment signature
            params_dict = {
                'razorpay_order_id': request.data.get("order_id"),
                'razorpay_payment_id': payment_id,
                'razorpay_signature': razorpay_signature
            }

            result = client.utility.verify_payment_signature(params_dict)

            if not result:
                return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

            # Prevent duplicate order for this checkout
            if Orders.objects.filter(user=checkout.user, seller=checkout.seller, total_price__gt=0, status="Paid").exists():
                return Response({"message": "Order already processed"}, status=status.HTTP_200_OK)

            # Ensure cart is not empty before proceeding
            if not checkout.cart.exists():
                return Response({"error": "Cart is empty, cannot create an order"}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # Create an Order from Cart Items
                order = Orders.objects.create(
                    user=checkout.user,
                    seller=checkout.seller,
                    total_price=sum(item.food.price * item.quantity for item in checkout.cart.all()),
                    status="Paid"
                )

                # Move Cart Items to Order
                order_items = [
                    order.items.create(
                        food=cart_item.food,
                        quantity=cart_item.quantity,
                        price=cart_item.food.price
                    ) for cart_item in checkout.cart.all()
                ]

                # Clear the Cart after order creation
                checkout.cart.all().delete()

            return Response({
                "message": "Payment successful, order placed!",
                "order_id": order.id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class EmptyCartAPIView(APIView):
    def delete(self, request, table_id):
        try:
            table = get_object_or_404(Table, id=table_id)
            Cart.objects.filter(table_number=table).delete()
            return Response(
                {"message": "Cart emptied successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp = request.data.get("otp")

        try:
            user = Seller.objects.get(email=email, otp=otp)
            user.otp = None  # Clear OTP after verification
            user.is_verified = True
            user.save()
            return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        except Seller.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)   



class SendOTPView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            
            try:
                user = Seller.objects.get(email=email)
                user.send_otp_email()  # Call the method to generate and send OTP

                return Response({"message": "OTP sent successfully to your email."}, status=status.HTTP_200_OK)
            except Seller.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)