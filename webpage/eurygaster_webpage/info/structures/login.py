import os

from dataclasses import dataclass
from collections import namedtuple


@dataclass
class LoginPreviewSettings:
    n_recent_icons: int = int(os.getenv("PREVIEW_N_RECENT", 10))
    icon_size: int = int(os.getenv("PREVIEW_ICON_SIZE", 100))
    icon_margin: int = int(os.getenv("PREVIEW_ICON_MARGIN", 10))
    icon_border: int = int(os.getenv("PREVIEW_ICON_BORDER", 8))
    speed_sec: int = int(os.getenv("PREVIEW_CAROUSEL_SPEED_SEC", 10))


LoginMsg = namedtuple('LoginMsg',
                      'SIGN_IN LABEL_LOGIN ERR_NOPOPUP ERR_POPUPCLOSED ERR_FATAL')

EngLoginMsg = LoginMsg("Sign in",
                       "Please, sign in to your account",
                       "Unable to open the authentication popup. Allow popups and refresh the page to proceed",
                       "Authentication popup was closed manually",
                       "Unable to connect to auth system using the current configuration",
                       )
RuLoginMsg = LoginMsg("Войти",
                      "Пожалуйста, войдите в свой аккаунт",
                      "Невозможно открыть всплывающее окно аутентификации. " + \
                      "Разрешите всплывающие окна и обновите страницу, чтобы продолжить",
                      "Всплывающее окно аутентификации было закрыто вручную",
                      "Невозможно подключиться к системе аутентификации, используя текущую конфигурацию",
                      )

CnLoginMsg = LoginMsg("登入",
                      "请登录您的帐户",
                      "无法打开身份验证弹出窗口。 允许弹出窗口并刷新页面以继续",
                      "身份验证弹出窗口已手动关闭",
                      "无法使用当前配置连接到身份验证系统",
                      )

DefaultLoginMsg = EngLoginMsg
LOGIN_MESSAGES = {
    'en': EngLoginMsg,
    'ru': RuLoginMsg,
    'cn': CnLoginMsg
}
