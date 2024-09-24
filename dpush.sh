
if [ "$1" = "local" ]; then

    if [ ! "$(docker images -q docker-image:test)" ]; then
        echo "Docker image docker-image:test does not exist. Proceeding with build."
        docker build --platform linux/arm64 -t docker-image:test .
    fi
    
    docker run --platform linux/arm64 -d -v ~/.aws-lambda-rie:/aws-lambda -p 9000:8080 \
        --entrypoint /aws-lambda/aws-lambda-rie \
        --name docker-test-container \
        docker-image:test \
            /usr/local/bin/python -m awslambdaric lambda_function.handler 
    curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'      

elif [ "$1" = "push" ]; then
    if [ ! "$(docker images -q docker-image:test)" ]; then
        echo "Docker image docker-image:test does not exist. Proceeding with build."
        docker build --platform linux/arm64 -t docker-image:test .
    fi
    docker tag docker-image:test 211125788522.dkr.ecr.ap-southeast-1.amazonaws.com/speechtotext:latest
    docker push 211125788522.dkr.ecr.ap-southeast-1.amazonaws.com/speechtotext:latest

elif [ "$1" = "clean" ]; then
    # Remove existing container if it exists
    if [ "$(docker ps -aq -f name=docker-test-container)" ]; then
        docker rm -f docker-test-container
    fi
    
    # Remove existing image if it exists
    if [ "$(docker images -q 211125788522.dkr.ecr.ap-southeast-1.amazonaws.com/speechtotext:latest)" ]; then
        docker rmi 211125788522.dkr.ecr.ap-southeast-1.amazonaws.com/speechtotext:latest
    fi

    # Remove existing image if it exists
    if [ "$(docker images -q docker-image:test)" ]; then
        docker rmi docker-image:test
    fi

else
    echo "Usage: ./dpush.sh [local|push|clean]"
    echo "  local: Build the Docker image locally"
    echo "  push: Tag and push the image to ECR"
    echo "  clean: Remove the Docker image and container"
    exit 1
fi