import os
import typing
from datetime import datetime
from enum import IntEnum

from google.protobuf import json_format

from . import integration_pb2 as proto

ALLOW_DELIVERY_TD = os.getenv("ALLOW_DELIVERY_TD", default=True)
PROFILE_CACHE: dict[int, str] = dict()


def convert(data: dict) -> proto.TransactionDataRequest:
    if isinstance(View := data.setdefault("View", {}), dict):
        if isinstance(Promotions := View.setdefault("Promotions", {}), dict):
            if not isinstance(Promotion := Promotions.setdefault("Promotion", []), list):
                Promotions.update(Promotion=[Promotion])
        if isinstance(CustomInfo := View.setdefault("CustomInfo", {}), dict):
            if not isinstance(Info := CustomInfo.setdefault("Info", []), list):
                CustomInfo.update(Info=[Info])
        if not isinstance(ItemView := View.setdefault("ItemView", []), list):
            View.update(ItemView=[ItemView])
        if not isinstance(Offers := View.setdefault("Offers", []), list):
            View.update(Offers=[Offers])
    td = proto.TransactionDataRequest()
    json_format.ParseDict(data, td, ignore_unknown_fields=True)
    assert all(
        [
            td.View._StoreId,
            td.View._transactionKind,
        ]
    ), "structure error"
    return td


class FOEPaymentTypeEnum(IntEnum):
    EatIn = 0
    Takeout = 1
    Other = 2


class PodTypesEnum(IntEnum):
    FRONT_COUNTER = 0
    DRIVE_THRU = 1
    WALK_THRU = 2
    DELIVERY = 3
    COLD_KIOSK_DESSERT = 4
    MC_CAFE = 5
    MC_EXPRESS = 6
    COLD_KIOSK_DRINK = 7
    CSO_KIOSK = 8
    HANDHELD_ORDER_TAKERS = 9


async def format_tdata(td: proto.TransactionDataRequest) -> proto.FormattedTData:
    view = td.View

    formatted_td = proto.FormattedTData()
    formatted_td.date.FromDatetime(
        datetime.strptime(f"{view._saleDate} {view._saleTime}", "%Y%m%d %H%M%S")
    )
    formatted_td.storeId = int(view._StoreId)
    formatted_td.transactionKind = int(view._transactionKind)
    formatted_td.orderKey = view._orderKey
    if view.HasField("_EcpOrderId"):
        formatted_td.ecpOrderId = view._EcpOrderId
    if view.HasField("CustomInfo"):
        formatted_td.customInfo.CopyFrom(format_custom_info(view.CustomInfo))
    formatted_td.tenderPOS = view._tenderPOS
    formatted_td.grossAmount = float(view._grossAmount)
    formatted_td.customerId = int(view.Customer._id)
    formatted_td.loyaltyCardId = view.Customer._loyaltyCardId
    formatted_td.items.extend(get_products(view.ItemView))
    formatted_td.promotions.extend(get_promotions(view.Promotions.Promotion))
    formatted_td.offers.extend(get_offers(view.Offers))
    formatted_td.orderSrc = int(view._orderSrc)
    formatted_td.podTypeEnum = PodTypesEnum(int(view._pod)).name
    formatted_td.bdTotalTax = float(view._BDTotalTax)
    formatted_td.bdTotalAmount = float(view._BDTotalAmount)
    formatted_td.totalTax = float(view._totalTax)
    formatted_td.totalAmount = float(view._totalAmount)
    formatted_td.saleType = FOEPaymentTypeEnum(int(view._type)).name

    return formatted_td


def get_products(
    item_view: typing.Iterable[proto.ItemView],
) -> typing.Iterator[proto.FormattedTData.Item]:
    for item in item_view:
        item_data = proto.FormattedTData.Item()
        item_data.itemCode = item.itemCode
        item_data.productCode = int(item.productCode)
        item_data.quantity = int(item.quantity)
        item_data.level = int(item.level)
        item_data.productType = item.productType
        if item.HasField("PromotionApplied"):
            item_data.promotionId = int(item.PromotionApplied._promotionId)
            item_data.offerId = int(item.PromotionApplied._offerId)
            item_data.eligible = item.PromotionApplied._eligible
        item_data.unitPrice = float(item.unitPrice)
        if item.HasField("longName"):
            item_data.longName = item.longName
        if item.HasField("quantityPromo"):
            item_data.quantityPromo = int(item.quantityPromo)
        item_data.netUnitPrice = float(item.netUnitPrice)
        item_data.unitTax = float(item.unitTax)

        item_data.totalPrice = float(item.totalPrice) if item.HasField("totalPrice") else 0.00
        item_data.ADTotalPrice = float(item.ADTotalPrice) if item.HasField("ADTotalPrice") else 0.00
        item_data.totalTax = float(item.totalTax) if item.HasField("totalTax") else 0.00
        item_data.ADTotalTax = float(item.ADTotalTax) if item.HasField("ADTotalTax") else 0.00

        yield item_data


def get_offers(offers: typing.Iterable[proto.Offer]) -> typing.Iterator[proto.FormattedTData.Offer]:
    for offer in offers:
        formatted_offer = proto.FormattedTData.Offer()

        formatted_offer.offerId = offer._offerId
        formatted_offer.customerId = offer._customerId
        formatted_offer.offerType = offer._offerType
        formatted_offer.offerBarcodeType = offer._offerBarcodeType

        yield formatted_offer


def get_promotions(
    promotions: typing.Iterable[proto.Promotion],
) -> typing.Iterator[proto.FormattedTData.Promotion]:
    for promotion in promotions:
        formatted_promotion = proto.FormattedTData.Promotion()

        formatted_promotion.id = promotion._id
        formatted_promotion.offerId = promotion._offerId
        formatted_promotion.exclusive = promotion._exclusive
        formatted_promotion.counter = promotion._counter

        yield formatted_promotion


def format_custom_info(custom_info: proto.CustomInfo) -> proto.FormattedTData.CustomInfoData:
    custom_info_data = proto.FormattedTData.CustomInfoData()

    info_data = {i._name: i._value for i in custom_info.Info}
    if info_data.get("customerNickname"):
        custom_info_data.customerNickname = info_data["customerNickname"]
    if info_data.get("orignalPodName"):
        custom_info_data.orignalPodName = info_data["orignalPodName"]

    return custom_info_data
