__eurygaster_webpage__ env variables:

| ENV                        | Dockerfile ARG            | Description                                          | Default value               |
|----------------------------|---------------------------|------------------------------------------------------|:----------------------------|
| INFERENCE_SERVER_ADDRESS   | INFERENCE_SERVER_ADDRESS  | Inference server HTTP address                        | http://eurygaster-svc:3000* |
| EURYGASTER_WEBPAGE_PORT    | EURYGASTER_WEBPAGE_PORT   | webpage port                                         | 4452                        |
| EURYGASTER_WEBPAGE_IP      | EURYGASTER_WEBPAGE_IP     | webpage ip                                           | 0.0.0.0                     |
| LOGURU_INIT                | LOGURU_INIT               | loguru logger flag                                   | True                        |
| LOGURU_LEVEL               | LOGURU_LEVEL              | loguru logging level                                 | DEBUG                       |
| GLITCHTIP_DSN              | GLITCHTIP_DSN             | GlitchTip project DSN                                | -                           |
| GLITCHTIP_MAX_BREADCRUMBS  | GLITCHTIP_MAX_BREADCRUMBS | Total amount of breadcrumbs to capture               | 50                          |
| GLITCHTIP_DEBUG            | GLITCHTIP_DEBUG           | sentry_sdk debug flag                                | 1                           |
| GLITCHTIP_SR               | GLITCHTIP_SR              | The fraction of errors to send                       | 1.0                         |
| AUTH_URL                   | -                         | Auth provider URL                                    | -                           |
| AUTH_REALM                 | -                         | Auth provider realm                                  | -                           |
| AUTH_CLIENT_ID             | -                         | Auth provider client id                              | -                           |
| PREVIEW_N_RECENT           | -                         | Number of last processed images on login page        | 10                          |
| PREVIEW_ICON_SIZE          | -                         | Image icon size on login page                        | 100                         |
| PREVIEW_ICON_MARGIN        | -                         | Margin between icons on login page                   | 10                          |
| PREVIEW_ICON_BORDER        | -                         | Icon border on login page                            | 8                           |
| PREVIEW_CAROUSEL_SPEED_SEC | -                         | Icon carousel speed on login page                    | 10                          |
| ENTRIES_N_RECENT           | -                         | Number of last recognized images for tabular entries | 5                           |

*eurygaster-svc will be resolved after docker compose deploy

How to add new language:

* Create new directory `./info/markdown/<NEW_LANG>`
* Create new files named exactly as .md-files in nearby folders for other languages.
* Add hint messages in `./info/structures.py`
