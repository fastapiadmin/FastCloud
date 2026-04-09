import json
import uuid
from datetime import datetime, timedelta
from typing import NewType

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.module_system.user.crud import UserCRUD
from app.api.v1.module_system.user.model import UserModel
from app.config.setting import settings
from app.core.exceptions import CustomException
from app.core.logger import log
from app.core.security import (
    CustomOAuth2PasswordRequestForm,
    create_access_token,
    decode_access_token,
)
from app.utils.captcha_util import CaptchaUtil
from app.utils.common_util import get_random_character
from app.utils.hash_bcrpy_util import PwdUtil
from app.utils.ip_local_util import IpLocalUtil

from .schema import (
    AuthSchema,
    CaptchaOutSchema,
    JWTOutSchema,
    JWTPayloadSchema,
    LogoutPayloadSchema,
    RefreshTokenPayloadSchema,
)

CaptchaKey = NewType("CaptchaKey", str)
CaptchaBase64 = NewType("CaptchaBase64", str)


class LoginService:
    """登录认证服务"""

    @classmethod
    async def authenticate_user_service(
        cls,
        request: Request,
        login_form: CustomOAuth2PasswordRequestForm,
        db: AsyncSession,
    ) -> JWTOutSchema:
        """
        用户认证

        参数:
        - request (Request): FastAPI请求对象
        - login_form (CustomOAuth2PasswordRequestForm): 登录表单数据
        - db (AsyncSession): 数据库会话对象

        返回:
        - JWTOutSchema: 包含访问令牌和刷新令牌的响应模型

        异常:
        - CustomException: 认证失败时抛出异常。
        """
        # 判断是否来自API文档
        referer = request.headers.get("referer", "")
        request_from_docs = referer.endswith(("docs", "redoc"))

        # 验证码校验
        if settings.CAPTCHA_ENABLE and not request_from_docs:
            if not login_form.captcha_key or not login_form.captcha:
                raise CustomException(msg="验证码不能为空")
            await CaptchaService.check_captcha_service(
                key=login_form.captcha_key,
                captcha=login_form.captcha,
            )

        # 用户认证
        auth = AuthSchema(db=db)
        user = await UserCRUD(auth).get_by_username_crud(username=login_form.username)

        if not user:
            raise CustomException(msg="用户不存在")

        if not PwdUtil.verify_password(
            plain_password=login_form.password, password_hash=user.password
        ):
            raise CustomException(msg="账号或密码错误")

        if user.status == "1":
            raise CustomException(msg="用户已被停用")

        # 更新最后登录时间
        user = await UserCRUD(auth).update_last_login_crud(id=user.id)
        if not user:
            raise CustomException(msg="用户不存在")
        if not login_form.login_type:
            raise CustomException(msg="登录类型不能为空")

        # 创建token
        token = await cls.create_token_service(
            request=request,
            user=user,
            login_type=login_form.login_type,
        )

        return token

    @classmethod
    async def create_token_service(
        cls, request: Request, user: UserModel, login_type: str
    ) -> JWTOutSchema:
        """
        创建访问令牌和刷新令牌

        参数:
        - request (Request): FastAPI请求对象
        - user (UserModel): 用户模型对象
        - login_type (str): 登录类型

        返回:
        - JWTOutSchema: 包含访问令牌和刷新令牌的响应模型

        异常:
        - CustomException: 创建令牌失败时抛出异常。
        """
        # 生成会话编号
        session_id = str(uuid.uuid4())
        request.scope["session_id"] = session_id

        request_ip = None
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # 取第一个 IP 地址，通常为客户端真实 IP
            request_ip = x_forwarded_for.split(",")[0].strip()
        else:
            # 若没有 X-Forwarded-For 头，则使用 request.client.host
            request_ip = request.client.host if request.client else "127.0.0.1"

        login_location = await IpLocalUtil.resolve_location_for_log(request_ip)
        request.scope["login_location"] = login_location

        # 确保在请求上下文中设置用户名和会话ID
        request.scope["user_username"] = user.username

        access_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        now = datetime.now()

        # 记录租户信息到日志
        log.info(f"用户ID: {user.id}, 用户名: {user.username} 正在生成JWT令牌")

        access_token = create_access_token(
            payload=JWTPayloadSchema(
                sub=user.username,
                is_refresh=False,
                exp=now + access_expires,
            )
        )
        refresh_token = create_access_token(
            payload=JWTPayloadSchema(
                sub=user.username,
                is_refresh=True,
                exp=now + refresh_expires,
            )
        )

        return JWTOutSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_expires.total_seconds()),
            token_type=settings.TOKEN_TYPE,
        )

    @classmethod
    async def refresh_token_service(
        cls,
        db: AsyncSession,
        request: Request,
        refresh_token: RefreshTokenPayloadSchema,
    ) -> JWTOutSchema:
        """
        刷新访问令牌

        参数:
        - db (AsyncSession): 数据库会话对象
        - request (Request): FastAPI请求对象
        - refresh_token (RefreshTokenPayloadSchema): 刷新令牌数据

        返回:
        - JWTOutSchema: 新的令牌对象

        异常:
        - CustomException: 刷新令牌无效时抛出异常
        """
        token_payload: JWTPayloadSchema = decode_access_token(token=refresh_token.refresh_token)
        if not token_payload.is_refresh:
            raise CustomException(msg="非法凭证，请传入刷新令牌")

        session_info = json.loads(token_payload.sub)
        session_id = session_info.get("session_id")
        user_id = session_info.get("user_id")

        if not session_id or not user_id:
            raise CustomException(msg="非法凭证,无法获取会话编号或用户ID")

        # 用户认证
        auth = AuthSchema(db=db)
        user = await UserCRUD(auth).get_by_id_crud(id=user_id)
        if not user:
            raise CustomException(msg="刷新token失败，用户不存在")

        # 记录刷新令牌时的租户信息
        log.info(f"用户ID: {user.id}, 用户名: {user.username} 正在刷新JWT令牌")

        # 设置新的 token
        access_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_expires = timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        now = datetime.now()

        session_info_json = json.dumps(session_info)

        access_token = create_access_token(
            payload=JWTPayloadSchema(
                sub=session_info_json,
                is_refresh=False,
                exp=now + access_expires,
            )
        )

        refresh_token_new = create_access_token(
            payload=JWTPayloadSchema(
                sub=session_info_json,
                is_refresh=True,
                exp=now + refresh_expires,
            )
        )

        return JWTOutSchema(
            access_token=access_token,
            refresh_token=refresh_token_new,
            token_type=settings.TOKEN_TYPE,
            expires_in=int(access_expires.total_seconds()),
        )

    @classmethod
    async def logout_service(cls, token: LogoutPayloadSchema) -> bool:
        """
        退出登录

        参数:
        - token (LogoutPayloadSchema): 退出登录令牌数据

        返回:
        - bool: 退出成功返回True

        异常:
        - CustomException: 令牌无效时抛出异常
        """
        payload: JWTPayloadSchema = decode_access_token(token=token.token)
        session_info = json.loads(payload.sub)
        session_id = session_info.get("session_id")

        if not session_id:
            raise CustomException(msg="非法凭证,无法获取会话编号")

        log.info(f"用户退出登录成功,会话编号:{session_id}")

        return True


class CaptchaService:
    """验证码服务"""
    # 内存存储验证码，格式: {captcha_key: (captcha_value, expire_time)}
    _captcha_store: dict[str, tuple[str, float]] = {}

    @classmethod
    async def get_captcha_service(cls) -> dict[str, CaptchaKey | CaptchaBase64]:
        """
        获取验证码

        参数:
        - None

        返回:
        - dict[str, CaptchaKey | CaptchaBase64]: 包含验证码key和base64图片的字典

        异常:
        - CustomException: 验证码服务未启用时抛出异常
        """
        if not settings.CAPTCHA_ENABLE:
            raise CustomException(msg="未开启验证码服务")

        # 生成验证码图片和值
        captcha_base64, captcha_value = CaptchaUtil.captcha_arithmetic()
        captcha_key = get_random_character()

        # 计算过期时间（默认5分钟）
        expire_time = datetime.now().timestamp() + 300

        # 存储验证码到内存
        cls._captcha_store[captcha_key] = (str(captcha_value), expire_time)

        log.info(f"生成验证码成功,验证码:{captcha_value}")

        # 返回验证码信息
        return CaptchaOutSchema(
            enable=settings.CAPTCHA_ENABLE,
            key=CaptchaKey(captcha_key),
            img_base=CaptchaBase64(f"data:image/png;base64,{captcha_base64}"),
        ).model_dump()

    @classmethod
    async def check_captcha_service(cls, key: str, captcha: str) -> bool:
        """
        校验验证码

        参数:
        - key (str): 验证码key
        - captcha (str): 用户输入的验证码

        返回:
        - bool: 验证通过返回True

        异常:
        - CustomException: 验证码无效或错误时抛出异常
        """
        if not captcha:
            raise CustomException(msg="验证码不能为空")

        # 清理过期验证码
        current_time = datetime.now().timestamp()
        expired_keys = [k for k, (_, exp) in cls._captcha_store.items() if exp < current_time]
        for k in expired_keys:
            del cls._captcha_store[k]

        # 获取存储的验证码
        captcha_info = cls._captcha_store.get(key)
        if not captcha_info:
            log.error("验证码已过期或不存在")
            raise CustomException(msg="验证码已过期")

        captcha_value, expire_time = captcha_info

        # 验证码不区分大小写比对
        if captcha.lower() != captcha_value.lower():
            log.error(f"验证码错误,用户输入:{captcha},正确值:{captcha_value}")
            raise CustomException(msg="验证码错误")

        # 验证成功后删除验证码
        del cls._captcha_store[key]

        return True
