import os
from dotenv import load_dotenv
import stripe

load_dotenv(override=True)  # Cargar variables de entorno desde .env
stripe.api_key = os.getenv("STRIPE_API_KEY_SANDBOX")

if not stripe.api_key or not stripe.api_key.startswith("sk_test_51M0yk0IFMgUrjyQfuXXun2UozogfpqIIZHdAFpNynltJDhG09AvSMjJVii2DcwW66rz3Vz4xGvPI3UCJk1hln41U00reaVTIPx"):
    raise ValueError(
        f"⚠️ ERROR: La clave de Stripe no se cargó correctamente. Valor obtenido: {stripe.api_key}")

print(f"✅ Clave de Stripe cargada correctamente: {stripe.api_key}")
