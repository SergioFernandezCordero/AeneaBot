# AeneaBot

Your personal Telegram bot with several functions.
Apart from several commands, all messages will be forwarded to an Ollama API server of your election so you can go full IA!

Built with:
- [Python-Telegram-Bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Lots of love :)

#### Commands

- /health - Run an active healthcheck. Returns a list of components check and its status
- /dice - Rolls a 6 sides dice.
- /man - Search a Linux/Unix command in the man pages. Defaults to Debian distro.(More info [aquí](http://www.polarhome.com/service/man/))
- /park - Park an object in the Parking (if database is configured SQLite database)
- /list_parking - List all object currentl in the Parking. Includes its UID and the date they were parked.
- /clear_object - Removes an object from the Parking. Must specify an object UID
- /clear_parking - Removes all objects from the Parking.

#### How to run
Use the included file config.yml.sample to create a config.yml file and fill the following variables:

  * token: Telegram bot Token
  * botname: Your Telegram bot name. Be creative!
  * authuser: Telegram username allowed to use the bot (yours)
  * ollama_url: URL of the Ollama server whith will be used to provide AI.
  * ollama_model: Name of the model configured in Ollama.
  * sqlitepath: Path for the SQLite3 persistent database. Required for Parking functionality.
  * loglevel: Log level output. See [python docs](https://docs.python.org/3/howto/logging.html#when-to-use-logging)
  
You can run in a docker container this way:
```
docker run -d --name tu-contenedor elautoestopista/aeneabot:latest -e TOKEN="XXXXX" -e BOTNAME="BotName" -e AUTHUSER="TuUser" -e LANG="es" -e LOGLEVEL="DEBUG" -e DB_PATH="/tmp"
```

Also you can run it on Kubernetes. [Here you can see an example](https://github.com/SergioFernandezCordero/ygdrassil-project/blob/master/ansible/roles/kube-apps/templates/aenea.j2) in how you can run it with the AeneaAI sidecar which provides your own AI using Ollama an the orca model.

And that's all! Your bot is up and running. You can add the modifications you want.

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

###### development-image.yml

Everytime you make a push to a branch, an image tagged with "develop" and a timestamp will be generated, so you can deploy it using minikube. Just ensure imagePullPolicy is set to Always to avoid cache.

###### stable-image.yml

When ready to generate a Relase, create a branch "releases/X.XX.XX". In this branch you will merge the branches with the features you've created.

Go to Gihub, create a Release with the release name on the branch (X.XX.XX), and tag it with the same release name. Don't forget to create a Changelog.
When the Release is published, an image will be created, tagged with the release name and "latest", so you can deploy it to Kubernetes.
