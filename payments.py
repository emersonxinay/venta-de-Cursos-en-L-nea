import paypalrestsdk
import stripe

stripe.api_key = "TU_SECRET_KEY"


def procesar_pago_stripe(monto, token):
    try:
        charge = stripe.Charge.create(
            amount=int(monto * 100),
            currency="usd",
            source=token,
            description="Compra de curso"
        )
        return charge
    except stripe.error.StripeError as e:
        return None


paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "TU_CLIENT_ID",
    "client_secret": "TU_SECRET"
})


def procesar_pago_paypal(monto, return_url, cancel_url):
    pago = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {"return_url": return_url, "cancel_url": cancel_url},
        "transactions": [{"amount": {"total": str(monto), "currency": "USD"}}]
    })

    if pago.create():
        return pago
    else:
        return None


@app.route('/reportes')
@login_required
def reportes():
    if current_user.rol != 'admin':
        return redirect(url_for('dashboard'))
    ventas = Venta.query.all()
    usuarios = Usuario.query.all()
    return render_template('reportes.html', ventas=ventas, usuarios=usuarios)
