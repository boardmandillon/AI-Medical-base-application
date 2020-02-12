# Basic shell script file for building, tagging and publishing the Docker image

docker build -t base-application:latest .
docker tag base-application registry.gitlab.com/comp3931-vulture/base-application
docker push registry.gitlab.com/comp3931-vulture/base-application