# AeneaBot

Your personal Telegram bot with several functions.

Based on project [AstroBeerBot](https://github.com/resetreboot/astrobeerbot) from my friend [ResetReboot](https://github.com/resetreboot)

Built with [Python-Telegram-Bot](https://github.com/python-telegram-bot/python-telegram-bot)

#### Commands

- /ruok - Status check. Returns "imok" if ok.
- /dice - Runs a 6 sides dice.
- /man - Shows "man" page for the specified command. Defaults to Debian distro.(More info [aquí](http://www.polarhome.com/service/man/))

#### How to run
Load the following envvars as specified:

  * TOKEN: Telegram bot Token
  * BOTNAME: Your bot name
  * AUTHUSER: Username allowed to use the bot (yours) 
  * LANG: Language for the APIs

For further info see config.example file.
    
You can run in a docker container this way:
```
docker run -d --name tu-contenedor elautoestopista/aeneabot:latest -e TOKEN="XXXXX" -e BOTNAME="BotName" -e AUTHUSER="TuUser" -e LANG="es"
```
And that's all! Your bot is up and running. You can add the modifications you want.

More info at https://hub.docker.com/r/elautoestopista/aeneabot
