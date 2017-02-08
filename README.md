# AeneaBot

Tu bot personal de Telegram con varias funciones.

Basado en el proyecto [AstroBeerBot](https://github.com/resetreboot/astrobeerbot) de mi amigo [ResetReboot](https://github.com/resetreboot), con el que también colaboro.

Implementado usando la magnífica librería [Python-Telegram-Bot](https://github.com/python-telegram-bot/python-telegram-bot)

####Comandos;

- /ruok - Check de estado. Devuelve "imok" si correcto
- /info - Busca en Wikipedia
- /dado - lanza un dado de 6 caras
- /tiempo - Previsión meteorológica de la localidad indicada
- /buscar - Busca información en Internet
- /man - Muestra la página "man" del comando especificado. Por defecto Debian si no se especifica otro.(Mas info [aquí](http://www.polarhome.com/service/man/))

Además tiene otras funciones relacionadas con la conversación. Búscalas en el código.
####¿Como empezar?
Genera un fichero config.py como el siguiente:
```
# Ejemplo de configuración
config = {
    "TOKEN": "Telegram bot Token",
    "BOTNAME": "El nombre de tu bot",
    "AUTHUSER": "Usuario autorizado al que el bot contestará (el tuyo)",
    "MAIL": "Tu email, ya servirá para algo",
    "LANG": "Idioma para las API",
    "MAPREQUEST": "MapRequestAPI API key",
    "USERAGENT": "UserAgent para tu bot",
}
```
Los campos empleados son:

  * TOKEN: Telegram bot Token
  * BOTNAME: El nombre de tu bot
  * AUTHUSER: Usuario autorizado al que el bot contestará (el tuyo)
  * LANG: Idioma para las API
  * MAIL: Tu email. Para algo servirá.
  * MAPREQUEST: MapRequestAPI API key
  * USERAGENT: UserAgent para tu bot
    
Despues, crea la imagen docker y lánzala mapeando la ruta del fichero config.py al contenedor:

`docker run -d --name tu-contenedor -v /ruta/a/config:/opt/aenea/config elautoestopista/aeneabot:latest`

¡Listo! Ya tienes tu bot listo. Puedes añadir las modificaciones que desees.

Builds en: https://hub.docker.com/r/elautoestopista/aeneabot/

Colaboraciones bienvenidas.