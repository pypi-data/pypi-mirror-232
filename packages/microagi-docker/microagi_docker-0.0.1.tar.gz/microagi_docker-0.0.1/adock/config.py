
# Potentially Destructive Docker Commands with explanations

DESTRUCTIVE_COMMANDS = {
    "docker rmi": "Removes one or more Docker images.",
    "docker rm": "Removes one or more stopped containers.",
    "docker volume rm": "Removes one or more volumes. Volumes are used to persist data between container restarts.",
    "docker network rm": "Removes one or more networks.",
    "docker system prune": "Removes unused data (containers, volumes, networks, and images).",
    "docker-compose down": "Stops and removes all containers defined in the docker-compose.yml.",
    "docker image prune": "Removes unused images.",
    "docker image rm": "Removes one or more images.",
    "docker container prune": "Removes all stopped containers.",
    "docker kill": "Kills one or more running containers.",
    "docker volume prune": "Removes all local volumes not used by at least one container.",
    "docker network prune": "Removes all unused networks.",
    "docker system prune": "Removes unused data, including stopped containers, all unused volumes, and more.",
    "docker-compose rm": "Removes stopped service containers.",
    "docker-compose down --volumes": "Stops and removes all containers and volumes.",
    "docker-compose down -v": "Stops and removes all containers and volumes.",
}