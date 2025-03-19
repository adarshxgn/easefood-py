from django.contrib.auth import authenticate
from api.models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    otp = serializers.CharField(read_only=True)

    class Meta:
        model = Seller
        fields = ['id', 'username', 'email', 'password1', 'password2', 'seller_category', 'otp']

    def create(self, validated_data):
        password1 = validated_data.pop('password1')
        password2 = validated_data.pop('password2')

        if password1 != password2:
            raise serializers.ValidationError('Password Mismatch')

        user = Seller.objects.create_user(**validated_data, password=password1)
        user.send_otp_email()  # Send OTP email

        return user

class SignInSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data

class FoodCategorySerializer(serializers.ModelSerializer):

    class Meta:

        model = FoodCategory        
        fields= ['id','food_category_name', 'category_image', 'owner' ]
        read_only_field = ['id', 'created_date', 'is_active']
     
    def validate_name(self, value):

        if FoodCategory.objects.filter(food_category_name = value).exists():

            raise serializers.ValidationError("Category name already exists")
        
        return value


class FoodSerializer(serializers.ModelSerializer):

    class Meta:

        model = Food
        fields = "__all__"
        read_only_field = ['id', 'created_date', 'owner', 'is_active']
    
    
    def validate_name(self, value):

        if Food.objects.filter(food_name = value).exists():
            raise serializers.ValidationError("Food name already exists")    
        return value


class TableSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'is_occupied', 'owner','seller_category']


class CartAddSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ['food','quantity','table_number','description']

    # def create(self, validated_data):

        # # Extract nested data for related models
        # food_name = validated_data.pop('food')['food_name']

        # # Retrieve related objects
        # food = Food.objects.get(food_name=food_name)

        # # table_id = validated_data.pop('table_number')['table_number']

        # # table_number = Table.objects.get(table_number=table_id)
        

        # # Create the Cart instance
        # cart = Cart.objects.create(
        #     food=food,
        #     table_number=table_number,
        #     **validated_data
        # )
        # return cart

class CartSerializer(serializers.ModelSerializer):
    food = serializers.CharField(source='food.food_name')
    image = serializers.ImageField(source='food.food_image') 
    table_number = serializers.IntegerField(source="table_number.table_number", read_only=True)
    food_price = serializers.DecimalField(source='food.price',max_digits=10, decimal_places= 2)
    description = serializers.CharField(source='food.description')

    class Meta:
        model = Cart
        fields =  ['id', 'food', 'quantity', 'image', 'table_number', 'food_price','description']

    def create(self, validated_data):
        # Extract nested data for related models
        food_name = validated_data.pop('food')['food_name']

        # Retrieve related objects
        food = Food.objects.get(food_name=food_name)

        # Create the Cart instance
        cart = Cart.objects.create(
            food=food,
            **validated_data
        )
        return cart
    
    def update(self, instance, validated_data):
        # Extract nested fields
        food_data = validated_data.pop('food', None)

        # Update food if provided
        if food_data:
            food_name = food_data.get('food_name')
            instance.food = Food.objects.get(food_name=food_name)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    # def get_total_price(self, obj):
    #     # Ensure that food_price and quantity are valid before calculating
    #     if obj.food and obj.quantity:
    #         return obj.food.price * obj.quantity
    #     return 0  # Default to 0 if either value is missing
    

from rest_framework import serializers

class CheckoutSerializer(serializers.ModelSerializer):
    table_number = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    cart_details = serializers.SerializerMethodField()

    class Meta:
        model = Checkout
        fields = ['id','table_number', 'total_price', 'cart_details', 'descriptions']

    def get_table_number(self, obj):
        """
        Retrieves the table number from the first cart item.
        """ 
        cart_item = obj.cart.first()
        return cart_item.table_number.table_number if cart_item and cart_item.table_number else None

    def get_total_price(self, obj):
        """
        Returns the total price of all items in the cart.
        """
        return sum(
            (getattr(cart_item.food, 'price', 0) or 0) * (cart_item.quantity or 0)
            for cart_item in obj.cart.all()
        )

    def get_cart_details(self, obj):
        """
        Retrieves details of all cart items in the checkout.
        """
        return [
            {
                "food": item.food.food_name if item.food else None,
                "quantity": item.quantity,
                "table_number": item.table_number.table_number if item.table_number else None,
                "description": item.description,
            }
            for item in obj.cart.all()
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source="food.food_name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "food", "food_name", "quantity", "price"]


class OrdersSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    pin = serializers.CharField(source="pin.pin", read_only=True)  # Get PIN

    class Meta:
        model = Orders
        fields = ["id", "pin", "table_number", "total_price", "status", "created_at", "items"]

class OrderItemSerializer1(serializers.ModelSerializer):
    food_name = serializers.CharField(source="food.food_name", read_only=True)
    time_taken = serializers.IntegerField(source="food.time_taken", read_only=True)  # Fetch time_taken

    class Meta:
        model = OrderItem
        fields = ["id", "food_name", "quantity", "price", "time_taken"]


class OrdersSerializer1(serializers.ModelSerializer):
    items = OrderItemSerializer1(many=True, read_only=True)
    pin = serializers.CharField(source="pin.pin", read_only=True)  

    class Meta:
        model = Orders
        fields = ["id", "pin", "table_number", "total_price", "status", "created_at", "items", "descriptions"]



class OTPRequestSerializer(serializers.Serializer): 
    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if the email is associated with an existing user."""
        if not Seller.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email not registered.")
        return value
        