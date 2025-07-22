import os

from collections import namedtuple

LoginMsg = namedtuple('LoginMsg',
                      'SIGN_IN SIGN_OUT LABEL_LOGIN ERR_NOPOPUP ERR_POPUPCLOSED ERR_FATAL')

EngLoginMsg = LoginMsg("Sign In",
                       "Sign Out",
                       "Please, sign in to your account",
                       "Unable to open the authentication popup. Allow popups and refresh the page to proceed",
                       "Authentication popup was closed manually",
                       "Unable to connect to auth system using the current configuration",
                       )
RuLoginMsg = LoginMsg("Войти",
                      "Выйти",
                      "Пожалуйста, войдите в свой аккаунт",
                      "Невозможно открыть всплывающее окно аутентификации. " + \
                      "Разрешите всплывающие окна и обновите страницу, чтобы продолжить",
                      "Всплывающее окно аутентификации было закрыто вручную",
                      "Невозможно подключиться к системе аутентификации, используя текущую конфигурацию",
                      )

DefaultLoginMsg = EngLoginMsg
LOGIN_MESSAGES = {
    'en': EngLoginMsg,
    'ru': RuLoginMsg,
}
