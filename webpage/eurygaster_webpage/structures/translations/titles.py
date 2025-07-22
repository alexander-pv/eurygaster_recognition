from collections import namedtuple

MdTitle = namedtuple('MdTitle',
                     'ABOUT HOW_TO GET_ACC_REC IDENTIFY')

NavTitle = namedtuple('NavTitle',
                      'ABOUT HOW_TO GET_ACC_REC IDENTIFY NAV LANG')

AccTitle = namedtuple('AccTitle',
                      'ACC GREET EMAIL USERNAME SIGN_IN HELP VER')

EngNavTitle = NavTitle(
    "About",
    "How to use",
    "Getting accurate recognition",
    "Identify Eurygaster",
    "Navigation",
    "Language"
)

RuNavTitle = NavTitle(
    "О приложении",
    "Как пользоваться",
    "Рекомендации по фотосъемке",
    "Распознать Eurygaster",
    "Навигация",
    "Язык"
)

EngMdTitle = MdTitle(
    "About",
    "How to use",
    "How to take the perfect photo for accurate identification",
    "Identify Eurygaster",
)

RuMdTitle = MdTitle(
    "О приложении",
    "Как пользоваться",
    "Рекомендации по фотосъемке для наиболее точного определения",
    "Распознать Eurygaster",
)

EngAccTitle = AccTitle(
    "Account",
    "Welcome",
    "Email",
    "User",
    "Sign In",
    "Help",
    "Version"
)

RuAccTitle = AccTitle(
    "Аккаунт",
    "Добро пожаловать",
    "Почта",
    "Пользователь",
    "Войти",
    "Помощь",
    "Версия"
)

NAV_TITLES = {
    'en': EngNavTitle,
    'ru': RuNavTitle,
}

MD_TITLES = {
    'en': EngMdTitle,
    'ru': RuMdTitle,
}

ACC_TITLES = {
    'en': EngAccTitle,
    'ru': RuAccTitle,
}
