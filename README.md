# AeneaBot

Tu bot personal de Telegram con varias funciones.

Renombra config.py.example a config.py y configura a tu gusto:

  * TOKEN: Telegram bot Token
  * BOTNAME: El nombre de tu bot
  * AUTHUSER: Usuario autorizado al que el bot contestará (el tuyo)
  * LANG: Idioma para las API
  * MAIL: Tu email. Para algo servirá.
  * MAPREQUEST: MapRequestAPI API key
  * USERAGENT: UserAgent para tu bot
    
Despues, crea la imagen docker y lánzala así:
```
docker run -d --name tu-contenedor -v /ruta/a/config:/opt/aenea/config image_id
```
¡Listo! Ya tienes tu bot listo. Puedes añadir las modificaciones que desees.