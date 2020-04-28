# Basic shell script file for building, tagging and publishing the Docker image

if [ "$1" = "-p" ] || [ "$1" = "--publish" ]
then
  docker build -t base-application:latest .
  docker tag base-application registry.gitlab.com/comp3931-vulture/base-application
  docker push registry.gitlab.com/comp3931-vulture/base-application
elif [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Build the base application Docker image"
  echo -e "\t-p, \t--publish \tPublish the Docker image to the GitLab Docker repository"
else
  docker build .
fi