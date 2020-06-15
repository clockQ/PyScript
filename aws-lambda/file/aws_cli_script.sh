# 创建执行角色
aws iam create-role --role-name python-lambda-example-role --assume-role-policy-document file://file/trust-policy.json


# 发布层
## 压缩层
pipenv run package python-lambda-example-layer.zip

## 上传层
aws s3 cp python-lambda-example-layer.zip s3://ph-lambda-layer/

## s3 发布层
aws lambda publish-layer-version --layer-name python-lambda-example-layer \
--description "Include requests" --license-info "MIT" \
--compatible-runtimes python3.8 \
--content S3Bucket=ph-lambda-layer,S3Key=python-lambda-example-layer.zip

## 本地发布层
aws lambda publish-layer-version --layer-name python-lambda-example-layer \
--description "Include requests" --license-info "MIT" \
--compatible-runtimes python3.8 \
--zip-file fileb://python-lambda-example-layer.zip


# 发布代码
## 打包源代码
zip -r aws-lambda.zip hello_world

## 首次创建函数
aws lambda create-function --function-name python-lambda-example \
--zip-file fileb://aws-lambda.zip --handler hello_world.app.lambda_handler --runtime python3.8 \
--role $(aws iam list-roles --query "Roles[?RoleName == 'python-lambda-example-role'].Arn" | grep arn | awk '{print $1}' | sed 's/\"//g')

## 更新现有函数
aws lambda update-function-code --function-name python-lambda-example \
--zip-file fileb://aws-lambda.zip

## 对函数加层
aws lambda update-function-configuration --function-name python-lambda-example \
--layers $(aws lambda list-layers --query "Layers[?LayerName == 'python-lambda-example-layer'].LatestMatchingVersion.LayerVersionArn" | grep arn | awk '{print $1}' | sed 's/\"//g')


# API GATEWAY
## 导入 REST API
aws apigateway import-rest-api --cli-binary-format raw-in-base64-out --parameters endpointConfigurationTypes=REGIONAL --body 'file://phlambda-jsonapi-v0-oas30.yaml'


aws apigateway put-integration \
        --region cn-northwest-1 \
        --rest-api-id 5ummfh1v81 \
        --resource-id dnffd1 \
        --http-method GET \
        --type AWS_PROXY \
        --integration-http-method POST \
        --uri arn:aws-cn:apigateway:cn-northwest-1:lambda:path/2015-03-31/functions/arn:aws-cn:lambda:cn-northwest-1:444603803904:function:python-lambda-example/invocations \
        --credentials arn:aws-cn:iam::444603803904:role/python-lambda-example



