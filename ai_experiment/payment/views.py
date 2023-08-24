from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings


import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_payment(request):
    if request.method == "POST":
        amount = int(request.POST["amount"]) 
        #Create customer
        try:
            customer = stripe.Customer.create(
                email=request.POST.get("email"),
                name=request.POST.get("full_name"),
                description="Test donation",
                source=request.POST['stripeToken']
            )

        except stripe.error.CardError as e:
            return HttpResponse("<h1>There was an error charging your card:</h1>"+str(e))     

        except stripe.error.RateLimitError as e:
             # handle this e, which could be stripe related, or more generic
            return HttpResponse("<h1>Rate error!</h1>")

        except stripe.error.InvalidRequestError as e:
            return HttpResponse("<h1>Invalid requestor!</h1>")

        except stripe.error.AuthenticationError as e:  
            return HttpResponse("<h1>Invalid API auth!</h1>")

        except stripe.error.StripeError as e:  
            return HttpResponse("<h1>Stripe error!</h1>")

        except Exception as e:  
            #  sentry_sdk.capture_exception(e) XXX
            return HttpResponse("<h1>Something went wrong!</h1>")

        #Stripe charge 
        charge = stripe.Charge.create(
            customer=customer,
            amount=int(amount)*100,
            currency='usd',
            description="Test donation"
        ) 
        transRetrive = stripe.Charge.retrieve(
            charge["id"],
            api_key=settings.STRIPE_SECRET_KEY
        )
        charge.save() # Uses the same API Key.
        return redirect("payment_success/")

    return render(request, "index.html")


def payment_success(request):
    return render(request, "success.html")   
    
