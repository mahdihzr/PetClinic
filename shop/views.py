from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import requests
from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError, HttpResponse
from django.contrib.auth.decorators import login_required
from staff.decorators import unauthenticated_user, allowed_users
from django.contrib import messages
from datetime import datetime, timedelta
import pytz
from .models import Category, Product, Image, Vote, Comment, ProductInfo, Cart, Address, Order, OrderItem, \
    StockReservation, BankPayment, BankCustomer, Transaction
import json
from django.http import JsonResponse


# Create your views here.
@login_required(login_url="/signin/")
@allowed_users(allowed_roles='shop_staff')
def shop_admin(request):
    return render(request, "shop_admin.html")


@login_required(login_url="/signin/")
@allowed_users(allowed_roles=['shop_staff'])
def shop_admin_category(request):
    if request.method == "POST":
        print(request.POST)
        if "category" in request.POST:
            new_category = request.POST["category"]
            Category.objects.create(name=new_category)

        elif "category2" in request.POST:
            new_category = request.POST["category2"]
            new_category = Category.objects.get(name=new_category)
            new_subcategory = request.POST["subcategory2"]
            Category.objects.create(name=new_subcategory, parent=new_category)

        elif "category3" in request.POST:
            new_category = request.POST["category3"]
            new_category = Category.objects.get(name=new_category)
            new_subcategory = request.POST["subcategory3"]
            new_subcategory = Category.objects.get(name=new_subcategory, parent=new_category)
            new_sub_subcategory = request.POST["sub_subcategory3"]
            Category.objects.create(name=new_sub_subcategory, parent=new_subcategory)

        elif "category4" in request.POST:
            category = request.POST['category4']
            category_obj = Category.objects.get(name=category)

            if request.POST['sub_subcategory4']:
                subcategory = request.POST['subcategory4']
                subcategory_obj = Category.objects.get(name=subcategory, parent=category_obj)
                sub_subcategory = request.POST['sub_subcategory4']
                sub_subcategory_obj = Category.objects.get(name=sub_subcategory, parent=subcategory_obj)
                sub_subcategory_obj.delete()
            elif request.POST["subcategory4"]:
                subcategory = request.POST['subcategory4']
                subcategory_obj = Category.objects.get(name=subcategory, parent=category_obj)
                subcategory_obj.delete()
            else:
                category_obj.delete()

        return redirect("/shop/admin/category/")



    elif request.method == "GET":
        try:
            categories = Category.objects.filter(parent=None)
            print(categories)

            categories_data = {}
            # make data structure like: {'Dog': {'food': ['dry', 'cann']}, 'cat': {'food': ['dry']}}
            for category in categories:
                subcategories = [sub for sub in category.subcategories.all()]
                sub_and_sub_subcategory_data = {}
                print(subcategories)

                for subcategory_data in subcategories:
                    sub_subcategory_data = [sub.name for sub in subcategory_data.subcategories.all()]
                    sub_and_sub_subcategory_data[subcategory_data.name] = sub_subcategory_data
                    categories_data[category.name] = sub_and_sub_subcategory_data

                # handeles empty subcats like 'test': {'': []}}
                else:
                    if not subcategories:
                        sub_subcategory_data = []
                        sub_and_sub_subcategory_data[""] = sub_subcategory_data
                        categories_data[category.name] = sub_and_sub_subcategory_data

            context = {"categories": categories_data, 'category_obj': categories}

            print(categories_data)
            for category in context["categories"]:
                print(category)
                for cat in context["categories"][str(category)]:
                    print('\t', cat, '\n')
            return render(request, "shop_admin_category.html", context=context)
        except:
            return render(request, "shop_admin_category.html")


@login_required(login_url="/signin/")
@allowed_users(allowed_roles=['shop_staff'])
def shop_admin_create_product(request):
    if request.method == "POST":
        product_name = request.POST["product_name"]
        images = request.FILES.getlist("images")
        category = request.POST["category"]
        subcategory = request.POST["subcategory"]
        sub_subcategory = request.POST["sub_subcategory"]
        description = request.POST["description"]
        price = request.POST["price"]
        weight = request.POST["weight"]
        in_stock = request.POST["in_stock"]
        animal_kind = request.POST["animal_kind"]
        good_for = request.POST["good_for"]
        brand = request.POST["brand"]

        keys = request.POST.getlist("keys[]")
        values = request.POST.getlist("values[]")
        attributes = dict(zip(keys, values))

        # get category object
        category_obj = Category.objects.get(name=category, parent=None)
        subcategory_obj = Category.objects.get(name=subcategory, parent=category_obj)
        sub_subcategory_obj = Category.objects.get(name=sub_subcategory, parent=subcategory_obj)

        new_product = Product.objects.create(name=product_name, category=sub_subcategory_obj, description=description,
                                             price=price, weight=weight,
                                             in_stock=in_stock, animal=animal_kind, good_for=good_for, brand=brand)
        new_product.save()

        for image in images:
            new_image = Image.objects.create(image=image, product=new_product)
            new_image.save()

        for key in attributes:
            new_product_info = ProductInfo.objects.create(product=new_product, key=key, value=attributes[key])
            new_product_info.save()

        return redirect("/shop/admin/create_product/")




    elif request.method == "GET":
        try:
            categories = Category.objects.filter(parent=None)
            print(categories)

            categories_data = {}
            # make data structure like: {'Dog': {'food': ['dry', 'cann']}, 'cat': {'food': ['dry']}}
            for category in categories:
                subcategories = [sub for sub in category.subcategories.all()]
                sub_and_sub_subcategory_data = {}
                print(subcategories)

                for subcategory_data in subcategories:
                    sub_subcategory_data = [sub.name for sub in subcategory_data.subcategories.all()]
                    sub_and_sub_subcategory_data[subcategory_data.name] = sub_subcategory_data
                    categories_data[category.name] = sub_and_sub_subcategory_data

                # handeles empty subcats like 'test': {'': []}}
                else:
                    if not subcategories:
                        sub_subcategory_data = []
                        sub_and_sub_subcategory_data[""] = sub_subcategory_data
                        categories_data[category.name] = sub_and_sub_subcategory_data

            context = {"categories": categories_data, 'category_obj': categories}
            return render(request, "shop_admin_create_product.html", context=context)

        except:
            return render(request, "shop_admin_create_product.html")


@login_required(login_url="/signin/")
@allowed_users(allowed_roles=['shop_staff'])
def shop_admin_manage_product(request):
    if request.method == "POST":
        pass
    elif request.method == "GET":
        products = Product.objects.all()
        products_dict = {}

        for product in products:
            # Assuming an Image model exists with a ForeignKey to Product
            # Placeholder; replace with real logic if you have images
            try:
                image_url = product.images.first().image.url  # Example if you have an Image model
            except AttributeError:
                image_url = "https://via.placeholder.com/150"

            products_dict[product.id] = {
                "name": product.name,
                "category": product.category.get_full_path(),
                "price": str(product.price),  # Convert Decimal to string
                "weight": str(product.weight) if product.weight else None,
                "stock": str(product.in_stock),
                "animal": product.animal,
                "goodFor": product.good_for,
                "brand": product.brand,
                "description": product.description,
                "image": image_url
            }

        context = {"products": products_dict}
        print(products_dict)

        return render(request, "shop_admin_manage_product.html", context=context)


@login_required(login_url="/signin/")
@allowed_users(allowed_roles=['shop_staff'])
def shop_admin_edit_product(request, pk):
    if request.method == "POST":
        product_name = request.POST["product_name"]
        category = request.POST["category"]
        subcategory = request.POST["subcategory"]
        sub_subcategory = request.POST["sub_subcategory"]
        description = request.POST["description"]
        price = request.POST["price"]
        weight = request.POST["weight"]
        in_stock = request.POST["in_stock"]
        animal_kind = request.POST["animal_kind"]
        good_for = request.POST["good_for"]
        brand = request.POST["brand"]

        keys = request.POST.getlist("keys[]")
        values = request.POST.getlist("values[]")
        attributes = dict(zip(keys, values))

        # get category object
        category_obj = Category.objects.get(name=category, parent=None)
        subcategory_obj = Category.objects.get(name=subcategory, parent=category_obj)
        sub_subcategory_obj = Category.objects.get(name=sub_subcategory, parent=subcategory_obj)

        try:
            product_object = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return HttpResponseNotFound("Product not found")
        except ValueError:
            # Handle invalid pk format
            return HttpResponseBadRequest("Invalid product ID")
        except Exception as e:
            # Catch any other unexpected errors
            return HttpResponseServerError("An error occurred")

        product_object.name = product_name
        product_object.category = sub_subcategory_obj
        product_object.description = description
        product_object.price = price
        product_object.weight = weight
        product_object.in_stock = in_stock
        product_object.animal = animal_kind
        product_object.good_for = good_for
        product_object.brand = brand
        product_object.save()

        for key in attributes:
            if not ProductInfo.objects.filter(product=product_object, key=key, value=attributes[key]):
                new_product_info = ProductInfo.objects.create(product=product_object, key=key, value=attributes[key])
                new_product_info.save()

        return redirect("/shop/admin/manage_product/")




    elif request.method == "GET":
        try:
            product_object = Product.objects.get(id=pk)
            print(product_object)
            categories = Category.objects.filter(parent=None)
            print(categories)

            categories_data = {}
            # make data structure like: {'Dog': {'food': ['dry', 'cann']}, 'cat': {'food': ['dry']}}
            for category in categories:
                subcategories = [sub for sub in category.subcategories.all()]
                sub_and_sub_subcategory_data = {}
                print(subcategories)

                for subcategory_data in subcategories:
                    sub_subcategory_data = [sub.name for sub in subcategory_data.subcategories.all()]
                    sub_and_sub_subcategory_data[subcategory_data.name] = sub_subcategory_data
                    categories_data[category.name] = sub_and_sub_subcategory_data

                # handeles empty subcats like 'test': {'': []}}
                else:
                    if not subcategories:
                        sub_subcategory_data = []
                        sub_and_sub_subcategory_data[""] = sub_subcategory_data
                        categories_data[category.name] = sub_and_sub_subcategory_data

            context = {"categories": categories_data, 'category_obj': categories, 'product_obj': product_object}
            return render(request, "shop_admin_edit_product.html", context=context)

        except:
            return render(request, "shop_admin_edit_product.html")


def product_list(request):
    products = Product.objects.all()
    data = []

    for product in products:
        # Get the first image (if any) for the "img" field
        first_image = product.get_gallery().first()
        img_name = first_image.image.url

        # Construct the product data
        product_data = {
            "id": product.id,
            "name": product.name,
            "category": [product.category.name, product.category.parent.name, product.category.parent.parent.name],
            # Full category hierarchy
            "description": product.description,
            "price": float(product.price),  # Convert Decimal to float for JSON
            "weight": f"{product.weight}kg" if product.weight else None,
            "in_stock": product.in_stock,
            # fix this >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            "animal": product.animal,
            "good_for": product.good_for,
            "brand": product.brand,
            "img": img_name,
            "sales": product.sales,
            "score": float(product.score_counter()),  # Convert to float
            "dateAdded": product.created_at.isoformat(),  # ISO format (e.g., "2024-01-15")
        }
        data.append(product_data)
    print(data)

    context = {"data": data}

    return render(request, "shop_product_list2.html", context=context)


@login_required(login_url="/signin/")
@allowed_users(allowed_roles=['shop_staff'])
def product_detail(request, pk):
    if request.method == "POST":
        try:
            product_object = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return HttpResponseNotFound("Product not found")
        except ValueError:
            # Handle invalid pk format
            return HttpResponseBadRequest("Invalid product ID")
        except Exception as e:
            # Catch any other unexpected errors
            return HttpResponseServerError("An error occurred")

        # add to cart
        if "product_add_to_cart_count" in request.POST:
            quantity = int(request.POST['product_add_to_cart_count'])
            if quantity > product_object.in_stock:
                messages.error(request, 'not enough in stock')
                return redirect(f"/shop/product_detail/{pk}")
            if not Cart.objects.filter(user=request.user, product=product_object):
                Cart.objects.create(user=request.user, product=product_object, quantity=quantity)
            else:
                cart_object = Cart.objects.get(user=request.user, product=product_object)
                if cart_object.quantity + quantity > product_object.in_stock:
                    messages.error(request, 'already in cart')
                    return redirect(f"/shop/product_detail/{pk}")

                cart_object.quantity = cart_object.quantity + quantity
                cart_object.save()
        # add or edit product rating
        if "rating" in request.POST:
            score = int(request.POST["rating"])
            if Vote.objects.filter(product=product_object, user=request.user):
                vote_object = Vote.objects.get(product=product_object, user=request.user)
                vote_object.vote = score
                vote_object.save()
            else:
                new_vote = Vote.objects.create(product=product_object, user=request.user, vote=score)
                new_vote.save()

        # add comment
        elif "comment" in request.POST:

            comment = request.POST["comment"]
            user_object = request.user
            new_comment = Comment.objects.create(user=user_object, product=product_object, comment=comment)
            new_comment.save()

        return redirect(f"/shop/product_detail/{pk}")

    elif request.method == "GET":
        try:
            product_object = Product.objects.get(id=pk)
            context = {"product_object": product_object}
            return render(request, "shop_product_detail.html", context=context)
        except Product.DoesNotExist:
            return HttpResponseNotFound("Product not found")
        except ValueError:
            # Handle invalid pk format
            return HttpResponseBadRequest("Invalid product ID")
        except Exception as e:
            # Catch any other unexpected errors
            return HttpResponseServerError("An error occurred")


def cart(request):
    user_object = request.user
    cart_items = Cart.objects.filter(user=user_object)

    if request.method == "POST":
        for item in cart_items:
            if request.POST[f'p{item.product.id}']:
                if int(request.POST[f'p{item.product.id}']) == 0:
                    item.delete()
                    continue
                item.quantity = request.POST[f'p{item.product.id}']
                item.save()
            else:
                item.delete()
        return redirect("/shop/order_summary")
    elif request.method == "GET":
        context = {"cart_items": cart_items}
        return render(request, "shop_cart.html", context=context)


def order(request):
    user_object = request.user
    cart_items = Cart.objects.filter(user=user_object)

    if request.method == "POST":
        # check in_stock and quantity
        for item in cart_items:
            if item.quantity > item.product.in_stock:
                messages.error(request, message="Not enough item in stock")
                return redirect("/shop/cart")

        address = request.POST["address"]
        customer_full_name = request.POST["full_name"]
        if Address.objects.filter(user=user_object, address=address):
            address_object = Address.objects.get(user=user_object, address=address)

        else:
            address_object = Address.objects.create(user=user_object, address=address)
            address_object.save()

        order_object = Order.objects.create(user=user_object,
                                            address=address_object,
                                            customer_name=customer_full_name)
        order_object.save()
        for item in cart_items:
            order_item_object = OrderItem.objects.create(order=order_object,
                                                         product=item.product,
                                                         quantity=item.quantity,
                                                         price=item.product.price)
            order_item_object.save()
            expire_time = datetime.utcnow() + timedelta(minutes=15)
            stock_reservation_object = StockReservation.objects.create(user=user_object,
                                                                       product=item.product,
                                                                       quantity=item.quantity,
                                                                       expires_at=expire_time)
            stock_reservation_object.save()
            item.product.in_stock -= item.quantity
            item.product.save()
            cart_object = Cart.objects.get(id=item.id)
            cart_object.delete()

        order_object.calculate_total()
        call_back_url = "http://127.0.0.1:8000/shop/payment_result"
        response = requests.post('http://127.0.0.1:8000/shop/bank_token_generator',
                                 data={'customer_uuid': '85cfe236-1f3c-4500-8e97-90333c271b45',
                                       'order_id': order_object.id, 'amount': order_object.total_price,
                                       "call_back_url": call_back_url})

        response_data = response.json()
        response_trans_id = response_data.get("trans_id")
        new_transaction = Transaction.objects.create(user=user_object, trans_id=response_trans_id,
                                                     amount=order_object.total_price,
                                                     order=order_object)
        new_transaction.save()

        return redirect(f"/shop/bank_page/{response_trans_id}")




    elif request.method == "GET":
        total_price = 0
        for item in cart_items:
            total_price += item.get_total_price()

        context = {"cart_items": cart_items, "total_price": total_price}
        return render(request, "shop_order_summary.html", context=context)


@csrf_exempt
def bank_token_generator(request):
    print(f"Request method: {request.method}")  # Add this line
    if request.method == "POST":
        customer_uuid = request.POST.get("customer_uuid")
        order_id = int(request.POST.get("order_id"))
        amount = float(request.POST.get("amount"))
        call_back_url = request.POST.get("call_back_url")

        if BankCustomer.objects.filter(customer_uuid=customer_uuid):
            new_payment = BankPayment.objects.create(order_id=order_id, amount=amount, call_back_url=call_back_url)
            new_payment.save()
            data = {
                "code": new_payment.status,
                "trans_id": new_payment.trans_id
            }
            return JsonResponse(data)
        else:
            return HttpResponse("You are not authorized to use this page")


def bank_page(request, pk):
    if request.method == "POST":
        status = request.POST["status"]
        print(pk == '62260760-b8bd-4f3f-9f1f-4a75c9051628')
        customer_payment = BankPayment.objects.get(trans_id=pk)
        customer_payment.status = status
        customer_payment.save()
        order_id = customer_payment.order_id
        amount =customer_payment.amount
        call_back_url = customer_payment.call_back_url
        return redirect(f"{call_back_url}?trans_id={pk}&order_id={order_id}&amount={amount}")
    elif request.method == "GET":

        return render(request, "shop_bank_page.html")


def payment_result(request):
    user_object = request.user
    trans_id = request.GET.get("trans_id")
    order_id = request.GET.get("order_id")
    amount = request.GET.get("amount")
    order_obj = Order.objects.get(id=order_id)

    response = requests.post('http://127.0.0.1:8000/shop/bank_confirmation',
                             data={'customer_uuid': '85cfe236-1f3c-4500-8e97-90333c271b45',
                                   'trans_id': trans_id, 'amount': amount, "order_id": order_id})

    response_data = response.json()
    response_trans_id = response_data.get("trans_id")
    payment_status = int(response_data.get("payment_status"))
    transaction_object = Transaction.objects.get(order=order_obj)
    transaction_object.status = payment_status
    transaction_object.save()
    if payment_status == 0:
        order_obj.status = "pending"
        order_obj.save()
        for item in order_obj.items.all():
            stock_reservation_object = StockReservation.objects.filter(product=item.product, quantity=item.quantity).first()
            stock_reservation_object.delete()
    else:
        order_obj.status = "cancelled"
        order_obj.save()
        for item in order_obj.items.all():
            stock_reservation_object = StockReservation.objects.filter(product=item.product, quantity=item.quantity).first()
            product_object = stock_reservation_object.product
            product_object.in_stock += item.quantity
            product_object.save()
            stock_reservation_object.delete()










    context = {"payment_status": payment_status}
    return render(request, "shop_payment_result.html", context=context)


@csrf_exempt
def bank_confirmation(request):
    if request.method == "POST":
        customer_uuid = request.POST.get("customer_uuid")
        trans_id = request.POST.get("trans_id")
        amount = float(request.POST.get("amount"))
        order_id = request.POST.get("order_id")

        if BankCustomer.objects.filter(customer_uuid=customer_uuid):
            try:
                payment_object = BankPayment.objects.get(trans_id=trans_id, amount=amount, order_id=order_id)
                payment_status = payment_object.status
                data = {"payment_status": payment_status, "trans_id": trans_id}
                return JsonResponse(data)
            except:
                data = {"payment_status": -1, "trans_id": trans_id}
                return JsonResponse(data)

    data = {"payment_status": -1, "trans_id": trans_id}

    return JsonResponse(data)


@login_required(login_url="/signin/")
@allowed_users(allowed_roles=['shop_staff'])
def get_products(request):
    products = Product.objects.all()
    products_dict = {}

    for product in products:
        # Assuming an Image model exists with a ForeignKey to Product
        # Placeholder; replace with real logic if you have images
        try:
            image_url = product.images.first().image.url  # Example if you have an Image model
        except AttributeError:
            image_url = "https://via.placeholder.com/150"

        products_dict[product.id] = {
            "name": product.name,
            "category": product.category.get_full_path(),
            "price": str(product.price),  # Convert Decimal to string
            "weight": str(product.weight) if product.weight else None,
            "stock": str(product.in_stock),
            "animal": product.animal,
            "goodFor": product.good_for,
            "brand": product.brand,
            "description": product.description,
            "image": image_url
        }

    return JsonResponse(products_dict)
