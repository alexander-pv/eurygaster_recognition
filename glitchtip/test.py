import sentry_sdk

sentry_sdk.init("DSN")
division_by_zero = 1 / 0
