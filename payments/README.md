# Payments app – M-Pesa + Paystack

This app handles:
- **M-Pesa prompts** (Safaricom Daraja API – Lipa Na M-Pesa Online / STK Push).
- **Paystack checkout callback verification**.

Other payment methods (Airtel Money, manual M-Pesa Pay Bill, etc.) remain in the **subscriptions** app.

## Flow

1. User selects a plan and chooses **M-Pesa** as payment method, enters phone number.
2. **Subscriptions** app creates a `Payment` (pending) and calls this app’s service to initiate STK Push.
3. **Payments** app calls Daraja API (OAuth + STK Push). User receives prompt on their phone.
4. User enters M-Pesa PIN on phone. Safaricom sends result to our **callback URL**.
5. **Payments** callback view receives the result, updates `MpesaTransaction`, and activates the subscription (completes `Payment`, creates/updates `Subscription`).
6. The waiting page **polls local DB only** (`/payments/mpesa/status/<id>/`) — no Daraja query on each poll.
7. **Background reconcile** (`python manage.py reconcile_mpesa`) queries Daraja for pending transactions that missed the callback (run via cron every 2–5 minutes).

## Configuration

In `config/settings.py` (or environment variables):

| Setting | Description |
|--------|-------------|
| `MPESA_ENV` | `sandbox` or `production` |
| `MPESA_CONSUMER_KEY` | Daraja app consumer key |
| `MPESA_CONSUMER_SECRET` | Daraja app consumer secret |
| `MPESA_SHORTCODE` | Paybill or Till number |
| `MPESA_SHORTCODE_TYPE` | `till` (Buy Goods / `CustomerBuyGoodsOnline`) or `paybill` (`CustomerPayBillOnline`). Default: `till`. |
| `MPESA_PASSKEY` | Lipa Na M-Pesa passkey from Daraja |
| `MPESA_CALLBACK_BASE_URL` | Base URL for callbacks (must be HTTPS in production). Callback path: `{MPESA_CALLBACK_BASE_URL}/payments/mpesa/callback/` |

For **local testing**, use a tunnel (e.g. ngrok) and set `MPESA_CALLBACK_BASE_URL` to your public URL (e.g. `https://abc123.ngrok.io`).

### Paystack

| Setting | Description |
|--------|-------------|
| `PAYSTACK_ENV` | `sandbox` or `live` |
| `PAYSTACK_PUBLIC_KEY` | Fallback public key |
| `PAYSTACK_SECRET_KEY` | Fallback secret key |
| `PAYSTACK_TEST_PUBLIC_KEY` | Test public key (used when `PAYSTACK_ENV=sandbox`) |
| `PAYSTACK_TEST_SECRET_KEY` | Test secret key (used when `PAYSTACK_ENV=sandbox`) |
| `PAYSTACK_LIVE_PUBLIC_KEY` | Live public key (used when `PAYSTACK_ENV=live`) |
| `PAYSTACK_LIVE_SECRET_KEY` | Live secret key (used when `PAYSTACK_ENV=live`) |
| `PAYSTACK_BASE_URL` | Defaults to `https://api.paystack.co` |

## URLs

- `GET /payments/mpesa/callback/` – Health check (returns JSON `status: ok`). Use to verify the URL is public.
- `POST /payments/mpesa/callback/` – Daraja callback (CSRF exempt). Do not require auth.
- `GET /payments/paystack/callback/` – User redirect URL from Paystack after payment; verifies transaction and activates subscription.

## Models

- **MpesaTransaction** – One record per STK Push: `account_reference` (e.g. `sub_<payment_id>`), phone, amount, `checkout_request_id`, status, `mpesa_receipt_number`, callback metadata.

## Extending (e.g. tokens, tips)

To use M-Pesa prompt for token purchase or tips:

1. Create a `Payment` (or equivalent) in your app.
2. Call `MpesaService().initiate_stk_push(phone, amount, account_reference, transaction_desc)` with a unique `account_reference` (e.g. `tokens_<order_id>`).
3. Create an `MpesaTransaction` with the returned `checkout_request_id` and `merchant_request_id`.
4. In `payments/views.py`, extend `_handle_successful_payment(txn)` to handle your `account_reference` prefix (e.g. `tokens_`) and credit tokens or complete the order.
