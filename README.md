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
  * DB_PATH: Path for the SQLite3 persistent databse
  * LOGLEVEL: Log level output. See [python docs](https://docs.python.org/3/howto/logging.html#when-to-use-logging)

For further info see config.example file.
    
You can run in a docker container this way:
```
docker run -d --name tu-contenedor elautoestopista/aeneabot:latest -e TOKEN="XXXXX" -e BOTNAME="BotName" -e AUTHUSER="TuUser" -e LANG="es" -e LOGLEVEL="DEBUG" -e DB_PATH="/tmp"
```
And that's all! Your bot is up and running. You can add the modifications you want.

#### Development

In order to develop you can run the bot locally:

```
export TOKEN="<token_gibberish>"
export BOTNAME="MyBot"
export AUTHUSER="MyTelegramUser"
export LANG="es"
export LOGLEVEL="DEBUG"
export DB_PATH="/path/to/db"

python3 aenea/aenea.py
```

#### Manual Building

You can build your Docker images this way:

```
# Login into your registry (for example DockerHub)
docker login

# Initialize building environment
sudo apt-get install qemu-user-static
docker buildx create --name aeneabot --platform linux/amd64,linux/arm64,linux/arm/v7
docker buildx use aeneabot
docker buildx inspect --bootstrap

# Local images for testing
docker buildx build --platform linux/amd64 -t dockerhubid/aeneabot:develop --load .

# Development images on DockerHub (multiplatform)
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t dockerhubid/aeneabot:develop --push .

# Stable releases (multiplatform)
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t dockerhubid/aeneabot:latest --push .
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t dockerhubid/aeneabot:release-<version> --push .
```

#### CI/CD Building

You can find the current pipelines in .github

## development-image.yml

Everytime you make a push to a branch, an image tagged with "development" will be generated, so you can deploy using minikube. Just ensure imagePullPolicy is set to Always to avoid cache.

## stable-image.yml

When ready to generate a Relase, create a branch "releases/X.XX.XX". In this branch you will merge the branches with the features you've created.

Go to Gihub, create a Release with the release name on the branch (X.XX.XX), and tag it with the same release name. Don't forget to create a Changelog.
When the Release is published, an image will be created, tagged with the release name and "latest", so you can deploy it to Kubernetes.
