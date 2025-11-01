"""
微信支付服务
"""

import os
import time
import random
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.models.payment import Order, OrderStatus, PaymentMethod


class WeChatPaymentService:
    """微信支付服务类"""
    
    def __init__(self):
        """初始化微信支付配置"""
        self.app_id = os.getenv("WECHAT_APP_ID", "")
        self.mch_id = os.getenv("WECHAT_MCH_ID", "")
        self.api_key = os.getenv("WECHAT_API_KEY", "")
        self.notify_url = os.getenv("WECHAT_NOTIFY_URL", "")
    
    async def create_payment(
        self,
        db: AsyncSession,
        order: Order
    ) -> Dict[str, Any]:
        """
        创建微信支付订单
        
        Args:
            db: 数据库会话
            order: 订单对象
        
        Returns:
            支付参数
        """
        try:
            # 构建支付参数
            params = {
                "appid": self.app_id,
                "mch_id": self.mch_id,
                "nonce_str": self._generate_nonce_str(),
                "body": f"购买课程-{order.product_name}",
                "out_trade_no": order.order_no,
                "total_fee": int(order.final_price * 100),  # 转换为分
                "spbill_create_ip": "127.0.0.1",
                "notify_url": self.notify_url,
                "trade_type": "NATIVE"  # 扫码支付
            }
            
            # 生成签名
            params["sign"] = self._generate_sign(params)
            
            # TODO: 实际调用微信支付API
            # import requests
            # response = requests.post(
            #     "https://api.mch.weixin.qq.com/pay/unifiedorder",
            #     data=self._dict_to_xml(params)
            # )
            # result = self._xml_to_dict(response.text)
            
            # 模拟返回
            result = {
                "return_code": "SUCCESS",
                "result_code": "SUCCESS",
                "prepay_id": f"wx{int(time.time())}{random.randint(1000, 9999)}",
                "code_url": f"weixin://wxpay/bizpayurl?pr={self._generate_nonce_str()[:20]}"
            }
            
            if result.get("return_code") == "SUCCESS":
                logger.info(f"微信支付订单创建成功: {order.order_no}")
                
                return {
                    "success": True,
                    "payment_method": "wechat",
                    "code_url": result.get("code_url"),
                    "prepay_id": result.get("prepay_id"),
                    "expires_in": 7200  # 2小时
                }
            else:
                logger.error(f"微信支付订单创建失败: {result}")
                return {
                    "success": False,
                    "error": result.get("return_msg", "创建支付订单失败")
                }
                
        except Exception as e:
            logger.error(f"微信支付异常: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_payment(
        self,
        db: AsyncSession,
        order_no: str,
        transaction_id: str
    ) -> Dict[str, Any]:
        """
        验证支付结果
        
        Args:
            db: 数据库会话
            order_no: 订单号
            transaction_id: 微信交易号
        
        Returns:
            验证结果
        """
        try:
            # TODO: 调用微信查询订单API
            # params = {
            #     "appid": self.app_id,
            #     "mch_id": self.mch_id,
            #     "transaction_id": transaction_id,
            #     "nonce_str": self._generate_nonce_str()
            # }
            # params["sign"] = self._generate_sign(params)
            # response = requests.post(
            #     "https://api.mch.weixin.qq.com/pay/orderquery",
            #     data=self._dict_to_xml(params)
            # )
            
            # 模拟验证成功
            result = {
                "return_code": "SUCCESS",
                "result_code": "SUCCESS",
                "trade_state": "SUCCESS",
                "transaction_id": transaction_id,
                "total_fee": 9900
            }
            
            if result.get("trade_state") == "SUCCESS":
                logger.info(f"微信支付验证成功: {order_no}")
                return {
                    "success": True,
                    "verified": True,
                    "transaction_id": transaction_id
                }
            else:
                return {
                    "success": False,
                    "verified": False,
                    "message": "支付未完成"
                }
                
        except Exception as e:
            logger.error(f"微信支付验证失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_notify(
        self,
        db: AsyncSession,
        notify_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理微信支付回调
        
        Args:
            db: 数据库会话
            notify_data: 回调数据
        
        Returns:
            处理结果
        """
        try:
            # 验证签名
            sign = notify_data.pop("sign", "")
            if not self._verify_sign(notify_data, sign):
                logger.warning("微信支付回调签名验证失败")
                return {
                    "return_code": "FAIL",
                    "return_msg": "签名验证失败"
                }
            
            # 获取订单
            order_no = notify_data.get("out_trade_no")
            from sqlalchemy import select
            result = await db.execute(
                select(Order).where(Order.order_no == order_no)
            )
            order = result.scalar_one_or_none()
            
            if not order:
                logger.error(f"订单不存在: {order_no}")
                return {
                    "return_code": "FAIL",
                    "return_msg": "订单不存在"
                }
            
            # 更新订单状态
            if notify_data.get("result_code") == "SUCCESS":
                order.status = OrderStatus.PAID
                order.payment_time = datetime.now(timezone.utc)
                order.transaction_id = notify_data.get("transaction_id")
                
                await db.commit()
                
                logger.info(f"微信支付回调处理成功: {order_no}")
                
                return {
                    "return_code": "SUCCESS",
                    "return_msg": "OK"
                }
            else:
                logger.error(f"微信支付失败: {notify_data}")
                return {
                    "return_code": "FAIL",
                    "return_msg": "支付失败"
                }
                
        except Exception as e:
            logger.error(f"微信支付回调处理异常: {e}")
            return {
                "return_code": "FAIL",
                "return_msg": str(e)
            }
    
    def _generate_nonce_str(self, length: int = 32) -> str:
        """生成随机字符串"""
        import string
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """生成签名"""
        # 排序参数
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        
        # 拼接字符串
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params if v])
        sign_str += f"&key={self.api_key}"
        
        # MD5加密并转大写
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()
    
    def _verify_sign(self, params: Dict[str, Any], sign: str) -> bool:
        """验证签名"""
        generated_sign = self._generate_sign(params)
        return generated_sign == sign
    
    def _dict_to_xml(self, data: Dict[str, Any]) -> str:
        """字典转XML"""
        xml = ["<xml>"]
        for key, value in data.items():
            xml.append(f"<{key}><![CDATA[{value}]]></{key}>")
        xml.append("</xml>")
        return "".join(xml)
    
    def _xml_to_dict(self, xml_str: str) -> Dict[str, Any]:
        """XML转字典"""
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_str)
        return {child.tag: child.text for child in root}


# 全局实例
wechat_payment = WeChatPaymentService()


# 便捷函数
async def create_wechat_payment(
    db: AsyncSession,
    order: Order
) -> Dict[str, Any]:
    """创建微信支付"""
    return await wechat_payment.create_payment(db, order)


async def verify_wechat_payment(
    db: AsyncSession,
    order_no: str,
    transaction_id: str
) -> Dict[str, Any]:
    """验证微信支付"""
    return await wechat_payment.verify_payment(db, order_no, transaction_id)
