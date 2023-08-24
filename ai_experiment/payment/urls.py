from django.urls import path

from ai_experiment.payment.views import stripe_payment, payment_success

app_name = "core"
urlpatterns = [
    path('stripe_payment', stripe_payment, name="stripe_payment"),
    path('payment_success/', payment_success, name="payment_success"),
]
