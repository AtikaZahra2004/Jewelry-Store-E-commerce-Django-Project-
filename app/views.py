
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import LoginForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .forms import AccountDetailsForm

import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Order, OrderItem

import hmac
import hashlib


from django.conf import settings
import razorpay



from django.views.decorators.csrf import csrf_exempt
import json





client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def signup_view(request):
    if request.method == 'POST':
        User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password']
        )
        return redirect('/')
    return redirect('/')

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
    return redirect('/')



# payment
def payment_verify(request):
    import json
    data = json.loads(request.body)

    razorpay_payment_id = data["razorpay_payment_id"]
    razorpay_order_id = data["razorpay_order_id"]
    razorpay_signature = data["razorpay_signature"]

    generated_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    order = Order.objects.get(razorpay_order_id=razorpay_order_id)

    if generated_signature == razorpay_signature:
        order.payment_status = "Paid"
        order.save()
        return JsonResponse({"redirect_url": f"/order-success/{order.id}/"})

    return JsonResponse({"redirect_url": "/payment-failed/"})

# checkout
def checkout(request):
    cart = request.session.get("cart", {})
    subtotal = sum(item["price"] * item["quantity"] for item in cart.values())

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        order = Order.objects.create(
            full_name=request.POST.get("fname"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
            notes=request.POST.get("notes", ""),
            payment_method=payment_method,
            total_amount=subtotal
        )

        for pid, item in cart.items():
            OrderItem.objects.create(
                order=order,
                product_name=item["name"],
                price=item["price"],
                quantity=item["quantity"],
            )

        request.session["cart"] = {}

        # ✅ RAZORPAY
        if payment_method == "razorpay":
            razorpay_order = client.order.create({
                "amount": int(subtotal * 100),
                "currency": "INR",
                "payment_capture": 1
            })

            order.razorpay_order_id = razorpay_order["id"]
            order.save()

            return render(request, "razorpay_checkout.html", {
                "order": order,
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "amount": int(subtotal * 100)
            })

        # COD
        return redirect("order_success", order_id=order.id)

    return render(request, "checkout.html", {
        "cart": cart,
        "subtotal": subtotal
    })


    # return redirect("order_success", order_id=order_id)

# success
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=order)

    return render(request, "order_success.html", {
        "order": order,
        "items": items
    })


# tracking

def order_tracking(request):
    order = None
    error = None

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        email = request.POST.get("email")

        try:
            order = Order.objects.get(id=order_id, email=email)
        except Order.DoesNotExist:
            error = "Order not found. Please check Order ID or Email."

    return render(request, "order_tracking.html", {
        "order": order,
        "error": error
    })



def paypal_page(request):
    return render(request, "paypal_page.html")

# cart
def cart(request):
    cart = request.session.get('cart', {})
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())

    return render(request, "cart.html", {
        "cart": cart,
        "subtotal": subtotal
    })

def increase_cart(request, id):
    cart = request.session.get('cart', {})
    cart[str(id)]['quantity'] += 1
    request.session.modified = True
    return redirect('cart')

def decrease_cart(request, id):
    cart = request.session.get('cart', {})
    if cart[str(id)]['quantity'] > 1:
        cart[str(id)]['quantity'] -= 1
    else:
        cart.pop(str(id))
    request.session.modified = True
    return redirect('cart')

def remove_cart(request, id):
    cart = request.session.get('cart', {})
    cart.pop(str(id), None)
    request.session.modified = True
    return redirect('cart')



def add_to_cart_ajax(request, id):
    product = Product.objects.get(id=id)

    cart = request.session.get("cart", {})

    if str(id) in cart:
        cart[str(id)]["quantity"] += 1
    else:
        cart[str(id)] = {
            "name": product.name,
            "price": float(product.price),
            "image": product.front_image.url,
            "quantity": 1
        }

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({"success": True})



def mini_cart_view(request):
    cart = request.session.get("cart", {})

    html = render_to_string("mini_cart_items.html", {"cart": cart})
    subtotal = sum(item["price"] * item["quantity"] for item in cart.values())

    return JsonResponse({
        "html": html,
        "subtotal": subtotal,
    })

def increase_cart_qty(request, id):
    cart = request.session.get("cart", {})

    if str(id) in cart:
        cart[str(id)]["quantity"] += 1

    request.session["cart"] = cart
    return mini_cart_view(request)


def decrease_cart_qty(request, id):
    cart = request.session.get("cart", {})

    if str(id) in cart and cart[str(id)]["quantity"] > 1:
        cart[str(id)]["quantity"] -= 1

    request.session["cart"] = cart
    return mini_cart_view(request)


def remove_cart_item(request, id):
    cart = request.session.get("cart", {})

    if str(id) in cart:
        del cart[str(id)]

    request.session["cart"] = cart
    return mini_cart_view(request)


# account
def account_details_view(request):
    user = request.user

    if not user.is_authenticated:
       return redirect('login')


    form = AccountDetailsForm(instance=user)

    if request.method == "POST":
        form = AccountDetailsForm(request.POST, instance=user)

        if form.is_valid():
            current_pwd = form.cleaned_data.get('current_password')
            new_pwd = form.cleaned_data.get('new_password')
            confirm_pwd = form.cleaned_data.get('confirm_password')

            # Password change logic
            if new_pwd:
                if not user.check_password(current_pwd):
                    form.add_error('current_password', "Incorrect current password")
                elif new_pwd != confirm_pwd:
                    form.add_error('confirm_password', "Passwords do not match")
                else:
                    user.set_password(new_pwd)
                    update_session_auth_hash(request, user)  # keep logged in

            form.save()
            return redirect('account_details')

    return render(request, 'account_details.html', {"form": form})








def logout_view(request):
    request.session.flush()  # session clear
    return redirect('home')


def dashboard_view(request):
    username = request.session.get('username')

    return render(request, 'dashboard.html', {
        'username': username,
    })


def orders_view(request):
    username = request.session.get('username')
    return render(request, 'orders.html', {'username': username})


def downloads_view(request):
    username = request.session.get('username')
    return render(request, 'downloads.html', {'username': username})


def addresses_view(request):
    username = request.session.get('username')
    return render(request, 'addresses.html', {'username': username})




def add_to_compare(request, id):
    product = Product.objects.get(id=id)

    compare = request.session.get('compare_items', [])

    compare.append({
        "name": product.name,
        "price": float(product.price),
        "image": product.front_image.url
    })

    request.session['compare_items'] = compare
    return redirect('compare')




def remove_from_compare(request, product_id):
    compare_list = request.session.get('compare_list', [])

    if product_id in compare_list:
        compare_list.remove(product_id)

    request.session['compare_list'] = compare_list
    return redirect('compare')

def compare_view(request):
    username = request.session.get('username')

    # future: session me compare products list store kar sakte hain
    compare_items = request.session.get('compare_items', [])

    return render(request, 'compare.html', {
        'username': username,
        'compare_items': compare_items
    })





def wishlist_view(request):
    username = request.session.get('username')
    
    wishlist_link = "https://yourwebsite.com/wishlist/" + (username if username else "")
    
    return render(request, 'wishlist.html', {
        'username': username,
        'wishlist_link': wishlist_link,
    })

def add_to_wishlist(request, id):
    product = Product.objects.get(id=id)

    wishlist = request.session.get('wishlist_items', [])

    wishlist.append({
        "name": product.name,
        "price": float(product.price),
        "image": product.front_image.url
    })

    request.session['wishlist_items'] = wishlist
    return redirect('wishlist')




def home(req):
    return render(req,'home.html')
def shop(request):
    products = Product.objects.all()
    return render(request, "shop.html", {'products': products})

def faq(request):
    return render (request,'faq.html')

def page404(request):
    return render (request,'page404.html')

def contact_view(request):
    success_msg = None

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # SAVE DATA IN SESSION
        request.session['contact_data'] = {
            "name": name,
            "email": email,
            "message": message
        }

        success_msg = "Your message has been sent successfully!"

    return render(request, "contact.html", {"success_msg": success_msg})


def product(req):
    return render(req,'product.html')


def blog(req):
    return render(req,'blog.html')

def page(req):
    return render(req,'page.html')


def about(req):
    return render(req,'about.html')



def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    cart = request.session.get('cart', {})
    if str(id) in cart:
        cart[str(id)]['quantity'] += 1
    else:
        cart[str(id)] = {
            'name': product.name,
            'price': float(product.price),
            'image': product.front_image.url,
            'quantity': 1
        }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')

def cart_page(request):
    cart = request.session.get('cart', {})
    return render(request, "cart.html", {'cart': cart})