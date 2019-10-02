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
Carga las siguientes variables de entorno con los valores que se indican abajo:

  * TOKEN: Telegram bot Token
  * BOTNAME: El nombre de tu bot
  * AUTHUSER: Usuario autorizado al que el bot contestará (el tuyo)
  * LANG: Idioma para las API
  * MAPREQUEST: MapRequestAPI API key. Opcional, pero si no lo seteas la funcionalidad de geoposicionamiento no estará disponible.

Puedes fijarte en el fichero de config.example
    
Después lanza el contenedor.

`
source config
docker run -d --name tu-contenedor elautoestopista/aeneabot:latest
`
Alternativamente, puedes pasarle las variables de entorno directamente en el comando:

`
docker run -d --name tu-contenedor elautoestopista/aeneabot:latest -e TOKEN="XXXXX" -e BOTNAME="BotName" -e AUTHUSER="TuUser" -e LANG="es"
` 

¡Listo! Ya tienes tu bot listo. Puedes añadir las modificaciones que desees.

Más info en https://hub.docker.com/r/elautoestopista/aeneabot

Colaboraciones bienvenidas.
