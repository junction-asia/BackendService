IMAGE_NAME=junction
ECR_PATH=611029865738.dkr.ecr.ap-northeast-2.amazonaws.com/$IMAGE_NAME

docker build -t $IMAGE_NAME . -f deploy.Dockerfile
docker tag $IMAGE_NAME $ECR_PATH

# ecr push
docker run --rm -it -v ~/.aws:/root/.aws -v $(pwd):/aws amazon/aws-cli ecr get-login-password --region ap-northeast-2 --profile junction | docker login --username AWS --password-stdin $ECR_PATH
docker push $ECR_PATH
