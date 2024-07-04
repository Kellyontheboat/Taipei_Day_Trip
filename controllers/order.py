from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from models.order import OrderResponse, OrderRequest, PaymentResponse

from datetime import datetime
import requests

router = APIRouter()

@router.post("/api/orders", response_model=OrderResponse)
def create_order(order_request: OrderRequest):
    prime = order_request.prime
    order = order_request.order

    order_number = datetime.now().strftime("%Y%m%d%H%M%S")

    # tappay_payload = {
    #     "partner_key": "partner_Dx4Ckr1tRJB315jIMc8SMnbUPCIs3DkaKLSNFDR8RzNzPPmKVYspsqo4",
    #     "prime": prime,
    #     "amount": order.price,
    #     "merchant_id": "merchantA",
    #     "details": "TapPay Test",
    #     "cardholder": {
    #         "phone_number": order.contact.phone,
    #         "name": order.contact.name,
    #         "email": order.contact.email,
    #         "zip_code": "100",
    #         "address": "Your address",
    #         "national_id": "A123456789"
    #     }
    # }
    
    tappay_payload = {
      "prime": prime,
      "partner_key": "partner_Dx4Ckr1tRJB315jIMc8SMnbUPCIs3DkaKLSNFDR8RzNzPPmKVYspsqo4",
      "merchant_id": "tppf_sha22595911sha49_GP_POS_3",
      "details":"TapPay Test",
      "amount": 100,
      "cardholder": {
          "phone_number": "+886923456789",
          "name": "王小明",
          "email": "LittleMing@Wang.com",
          "zip_code": "100",
          "address": "台北市天龍區芝麻街1號1樓",
          "national_id": "A123456789"
      },
      "remember": True
}

    headers = {
        "Content-Type": "application/json",
        "x-api-key": "partner_Dx4Ckr1tRJB315jIMc8SMnbUPCIs3DkaKLSNFDR8RzNzPPmKVYspsqo4"
    }

    tappay_response = requests.post("https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime",
                                    json=tappay_payload,
                                    headers=headers)

    if tappay_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Payment failed")

    tappay_result = tappay_response.json()
    if tappay_result["status"] != 0:
        raise HTTPException(status_code=400, detail=tappay_result["msg"])

    payment_response = PaymentResponse(status=tappay_result["status"], message="付款成功")
    order_response = OrderResponse(number=order_number, payment=payment_response)

    return order_response