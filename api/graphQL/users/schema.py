import graphene
from graphene_django import DjangoObjectType
from graphql_auth import mutations
from users.models import User, Address, Favorite, CartItem
from products.models import Product

# Define GraphQL Types

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"

class AddressType(DjangoObjectType):
    class Meta:
        model = Address
        fields = "__all__"

class FavoriteType(DjangoObjectType):
    class Meta:
        model = Favorite
        fields = '__all__'

class CartItemType(DjangoObjectType):
    class Meta:
        model = CartItem
        fields = "__all__"

# Define Mutations

class UpsertAddress(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        user_id = graphene.ID(required=True)
        address_line1 = graphene.String(required=True)
        address_line2 = graphene.String()
        city = graphene.String(required=True)
        state = graphene.String(required=True)
        postal_code = graphene.String(required=True)
        country = graphene.String(required=True)

    address = graphene.Field(AddressType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, user_id, address_line1, city, state, postal_code, country, address_line2=None, id=None):
        errors = []
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            errors.append("User does not exist.")
            return UpsertAddress(success=False, errors=errors)

        if id:
            try:
                address = Address.objects.get(pk=id)
                if address.user != user:
                    raise Exception("You do not have permission to update this address.")
            except Address.DoesNotExist:
                errors.append("Address does not exist.")
                return UpsertAddress(success=False, errors=errors)
            except Exception as e:
                errors.append(str(e))
                return UpsertAddress(success=False, errors=errors)

            address.address_line1 = address_line1
            address.address_line2 = address_line2
            address.city = city
            address.state = state
            address.postal_code = postal_code
            address.country = country
            message = "Address updated successfully."
        else:
            address = Address(
                user=user,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country
            )
            message = "Address created successfully."

        try:
            address.full_clean()
            address.save()
        except Exception as e:
            errors.extend(e.messages)
            return UpsertAddress(success=False, errors=errors)

        return UpsertAddress(address=address, success=True, message=message, errors=None)

class DeleteAddress(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id, user_id):
        errors = []
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            errors.append("User does not exist.")
            return DeleteAddress(success=False, errors=errors)

        try:
            address = Address.objects.get(pk=id)
            if address.user != user:
                errors.append("You do not have permission to delete this address.")
                return DeleteAddress(success=False, errors=errors)
            address.delete()
            return DeleteAddress(success=True, message="Address deleted successfully.", errors=None)
        except Address.DoesNotExist:
            errors.append("Address does not exist.")
            return DeleteAddress(success=False, errors=errors)

class UpsertCartItem(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        user_id = graphene.ID(required=True)
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    cart_item = graphene.Field(CartItemType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, user_id, product_id, quantity, id=None):
        errors = []
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            errors.append("User does not exist.")
            return UpsertCartItem(success=False, errors=errors)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            errors.append("Product does not exist.")
            return UpsertCartItem(success=False, errors=errors)

        if id:
            try:
                cart_item = CartItem.objects.get(pk=id)
                if cart_item.user != user:
                    raise Exception("You do not have permission to update this cart item.")
            except CartItem.DoesNotExist:
                errors.append("Cart item does not exist.")
                return UpsertCartItem(success=False, errors=errors)
            except Exception as e:
                errors.append(str(e))
                return UpsertCartItem(success=False, errors=errors)

            cart_item.product = product
            cart_item.quantity = quantity
            message = "Cart item updated successfully."
        else:
            cart_item = CartItem(user=user, product=product, quantity=quantity)
            message = "Cart item created successfully."

        try:
            cart_item.full_clean()
            cart_item.save()
        except Exception as e:
            errors.extend(e.messages)
            return UpsertCartItem(success=False, errors=errors)

        return UpsertCartItem(cart_item=cart_item, success=True, message=message, errors=None)

class DeleteCartItem(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id, user_id):
        errors = []
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            errors.append("User does not exist.")
            return DeleteCartItem(success=False, errors=errors)

        try:
            cart_item = CartItem.objects.get(pk=id)
            if cart_item.user != user:
                errors.append("You do not have permission to delete this cart item.")
                return DeleteCartItem(success=False, errors=errors)
            cart_item.delete()
            return DeleteCartItem(success=True, message="Cart item deleted successfully.", errors=None)
        except CartItem.DoesNotExist:
            errors.append("Cart item does not exist.")
            return DeleteCartItem(success=False, errors=errors)

class UpsertFavorite(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        user_id = graphene.ID(required=True)
        product_id = graphene.ID(required=True)

    favorite = graphene.Field(FavoriteType)
    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, user_id, product_id, id=None):
        errors = []
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            errors.append("User does not exist.")
            return UpsertFavorite(success=False, errors=errors)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            errors.append("Product does not exist.")
            return UpsertFavorite(success=False, errors=errors)

        if id:
            try:
                favorite = Favorite.objects.get(pk=id)
                if favorite.user != user:
                    raise Exception("You do not have permission to update this favorite.")
            except Favorite.DoesNotExist:
                errors.append("Favorite does not exist.")
                return UpsertFavorite(success=False, errors=errors)
            except Exception as e:
                errors.append(str(e))
                return UpsertFavorite(success=False, errors=errors)

            favorite.product = product
            message = "Favorite updated successfully."
        else:
            favorite = Favorite(user=user, product=product)
            message = "Favorite created successfully."

        try:
            favorite.full_clean()
            favorite.save()
        except Exception as e:
            errors.extend(e.messages)
            return UpsertFavorite(success=False, errors=errors)

        return UpsertFavorite(favorite=favorite, success=True, message=message, errors=None)

class DeleteFavorite(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id, user_id):
        errors = []
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            errors.append("User does not exist.")
            return DeleteFavorite(success=False, errors=errors)

        try:
            favorite = Favorite.objects.get(pk=id)
            if favorite.user != user:
                errors.append("You do not have permission to delete this favorite.")
                return DeleteFavorite(success=False, errors=errors)
            favorite.delete()
            return DeleteFavorite(success=True, message="Favorite deleted successfully.", errors=None)
        except Favorite.DoesNotExist:
            errors.append("Favorite does not exist.")
            return DeleteFavorite(success=False, errors=errors)

# Define Queries

class UserQueryResult(graphene.ObjectType):
    user = graphene.Field(UserType)
    status = graphene.Boolean()
    message = graphene.String()

class UserListQueryResult(graphene.ObjectType):
    users = graphene.List(UserType)
    status = graphene.Boolean()
    message = graphene.String()

class UserQuery(graphene.ObjectType):
    all_user = graphene.Field(UserListQueryResult)
    get_user_by_email = graphene.Field(UserListQueryResult, email=graphene.String())
    user_by_id = graphene.Field(UserQueryResult, id=graphene.ID())

    def resolve_all_user(root, info):
        users = User.objects.all()
        return UserListQueryResult(users=users, status=True, message="All users fetched successfully.")

    def resolve_get_user_by_email(root, info, email):
        users = User.objects.filter(email=email)
        if users:
            return UserListQueryResult(users=users, status=True, message="Users with the specified email fetched successfully.")
        return UserListQueryResult(users=[], status=False, message="No users found with the specified email.")

    def resolve_user_by_id(root, info, id):
        try:
            user = User.objects.get(id=id)
            return UserQueryResult(user=user, status=True, message="User found successfully.")
        except User.DoesNotExist:
            return UserQueryResult(user=None, status=False, message="User not found.")

class AddressQuery(graphene.ObjectType):
    get_all_addresses = graphene.List(AddressType)
    get_addresses_by_user_id = graphene.List(AddressType, user_id=graphene.ID(required=True))
    get_address_by_id = graphene.Field(AddressType, id=graphene.ID(required=True))

    def resolve_get_all_addresses(self, info):
        return Address.objects.all()

    def resolve_get_addresses_by_user_id(self, info, user_id):
        try:
            return Address.objects.filter(user__id=user_id)
        except Address.DoesNotExist:
            return None

    def resolve_get_address_by_id(self, info, id):
        try:
            return Address.objects.get(pk=id)
        except Address.DoesNotExist:
            return None

class CartItemQuery(graphene.ObjectType):
    get_all_cart_items = graphene.List(CartItemType)
    get_cart_items_by_user_id = graphene.List(CartItemType, user_id=graphene.ID(required=True))
    get_cart_item_by_id = graphene.Field(CartItemType, id=graphene.ID(required=True))

    def resolve_get_all_cart_items(self, info):
        return CartItem.objects.all()

    def resolve_get_cart_items_by_user_id(self, info, user_id):
        try:
            return CartItem.objects.filter(user__id=user_id)
        except CartItem.DoesNotExist:
            return None

    def resolve_get_cart_item_by_id(self, info, id):
        try:
            return CartItem.objects.get(pk=id)
        except CartItem.DoesNotExist:
            return None

class FavoriteQuery(graphene.ObjectType):
    get_all_favorites = graphene.List(FavoriteType)
    get_favorites_by_user_id = graphene.List(FavoriteType, user_id=graphene.ID(required=True))
    get_favorite_by_id = graphene.Field(FavoriteType, id=graphene.ID(required=True))

    def resolve_get_all_favorites(self, info):
        return Favorite.objects.all()

    def resolve_get_favorites_by_user_id(self, info, user_id):
        try:
            return Favorite.objects.filter(user__id=user_id)
        except Favorite.DoesNotExist:
            return None

    def resolve_get_favorite_by_id(self, info, id):
        try:
            return Favorite.objects.get(pk=id)
        except Favorite.DoesNotExist:
            return None

# Combine Queries and Mutations into a Schema

class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()

class UserMutations(AuthMutation, graphene.ObjectType):
    upsert_address = UpsertAddress.Field()
    delete_address = DeleteAddress.Field()
    upsert_cart_item = UpsertCartItem.Field()
    delete_cart_item = DeleteCartItem.Field()
    upsert_favorite = UpsertFavorite.Field()
    delete_favorite = DeleteFavorite.Field()

class UserQueries(UserQuery, AddressQuery, CartItemQuery, FavoriteQuery, graphene.ObjectType):
    pass


