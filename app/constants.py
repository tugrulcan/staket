from enum import Enum


# https://fastapi-utils.davidmontague.xyz/user-guide/basics/enums/
# https://support.bigcommerce.com/s/article/Order-Statuses
class OrderStatus(str, Enum):
    PENDING = "pending"
    AWAITING_PAYMENT = "awaiting_payment"
    AWAITING_FULFILLMENT = "awaiting_fulfillment"
    AWAITING_SHIPMENT = "awaiting_shipment"
    AWAITING_PICKUP = "awaiting_pickup"
    PARTIALLY_SHIPPED = "partially_shipped"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"
    DECLINED = "declined"
    REFUNDED = "refunded"
    MANUAL_VERIFICATION_REQUIRED = "manual_verification_required"
