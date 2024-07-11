from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from models.order import OrderResponse, OrderRequest, PaymentResponse, OrderData, UpdateOrder, save_order_into_db, update_order_status_db, save_booking_into_order_schedule_db, delete_booking_data_db
from models.redis.r_booking import retrieve_booking_data_redis, delete_booking_data_redis

from datetime import datetime
import requests
import uuid

router = APIRouter()

@router.post("/api/orders", response_model=OrderResponse)
def create_order(order_request: OrderRequest):
    
    prime = order_request.prime
    contact = order_request.contact
    member_id = order_request.memberId

    def generate_order_number():
        unique_id = uuid.uuid4().hex[:7]  # Use the first 7 chars UUID
        now = datetime.now()
        timestamp_str = now.strftime("%y%m%d%H%M") # yr.month.day.hr.min
        
        order_number = f"{timestamp_str}{unique_id}"
        return order_number[:15]
    
    order_number = generate_order_number()
    pay_status = 'UNPAID'
    total_cost = retrieve_booking_data_redis(member_id)['total_cost']   

    order_data = OrderData(
        member_id=member_id,
        order_number=order_number,
        pay_status=pay_status,
        total_cost=total_cost,
        #rec_trade_id retrieve through tappay below
    )

    success, order_id= save_order_into_db(order_data)
    
    if not success:
            raise HTTPException(status_code=500, detail="Failed to save order")
        
    #!帶入tappay的資料
    tappay_payload = {
      "prime": prime,
      "partner_key": "partner_Dx4Ckr1tRJB315jIMc8SMnbUPCIs3DkaKLSNFDR8RzNzPPmKVYspsqo4",
      "merchant_id": "tppf_sha22595911sha49_GP_POS_3",
      "details":"TapPay Test",
      "amount": total_cost,
      "cardholder": {
          "phone_number": contact.phone,
          "name": contact.name,
          "email": contact.email,
          "zip_code": "",
          "address": "",
          "national_id": ""
      },
      "remember": True
      #"bank_transaction_id": bank_transaction_id 
}

    headers = {
        "Content-Type": "application/json",
        "x-api-key": "partner_Dx4Ckr1tRJB315jIMc8SMnbUPCIs3DkaKLSNFDR8RzNzPPmKVYspsqo4"
    }

    tappay_response = requests.post("https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime",
                                    json=tappay_payload,
                                    headers=headers)
    
    tappay_result = tappay_response.json()
    print(tappay_result)
    rec_trade_id = tappay_result.get('rec_trade_id')
    
    update_order = UpdateOrder(
        order_number=order_number,
        pay_status='UNPAID',
        rec_trade_id=rec_trade_id
    )
    
    # payment failed
    if tappay_response.status_code != 200 or tappay_result["status"] != 0:
        update_order_status_db(update_order)
        save_booking_into_order_schedule_db(member_id, order_id)
        delete_booking_data_db(member_id)
        delete_booking_data_redis(member_id, None)
        raise HTTPException(status_code=400, detail=tappay_result["msg"])
    
    # Payment succeeded
    update_order.pay_status = 'PAID'
    update_order_status_db(update_order)
    save_booking_into_order_schedule_db(member_id, order_id)
    delete_booking_data_db(member_id)
    delete_booking_data_redis(member_id, None)

    payment_response = PaymentResponse(status=tappay_result["status"], message="付款成功")
    order_response = OrderResponse(number=order_number, payment=payment_response)

    return order_response
