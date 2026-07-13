Transform: AWS::Serverless-2016-10-31

Parameters:
  DatabaseUrl:
    Type: String
    NoEcho: true
  JwtSecretKey:
    Type: String
    NoEcho: true
  JwtRefreshSecretKey:
    Type: String
    NoEcho: true
  GeminiApiKey:
    Type: String
    NoEcho: true
  CloudflareR2AccountId:
    Type: String
  CloudflareR2AccessKeyId:
    Type: String
    NoEcho: true
  CloudflareR2SecretAccessKey:
    Type: String
    NoEcho: true
  CloudflareR2BucketName:
    Type: String
    Default: 'exam-ia'
  CloudflareR2PublicUrl:
    Type: String
  ResendApiKey:
    Type: String
    NoEcho: true
  EmailFrom:
    Type: String
    Default: 'ExamIA <noreply@exam-ia.net>'
  FrontendUrl:
    Type: String

Globals:
  Function:
    Timeout: 600
    MemorySize: 1024
    Runtime: python3.12
    Environment:
      Variables:
        TZ: "America/Bogota"

Resources:
  ExamIAFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: 'exam-ia-backend'
      Handler: lambda_handler.handler
      Runtime: python3.12
      Timeout: 600
      MemorySize: 1024
      Environment:
        Variables:
          DATABASE_URL: !Ref DatabaseUrl
          DEBUG: 'False'

          JWT_SECRET_KEY: !Ref JwtSecretKey
          JWT_REFRESH_SECRET_KEY: !Ref JwtRefreshSecretKey

          GEMINI_API_KEY: !Ref GeminiApiKey

          CLOUDFLARE_R2_ACCOUNT_ID: !Ref CloudflareR2AccountId
          CLOUDFLARE_R2_ACCESS_KEY_ID: !Ref CloudflareR2AccessKeyId
          CLOUDFLARE_R2_SECRET_ACCESS_KEY: !Ref CloudflareR2SecretAccessKey
          CLOUDFLARE_R2_BUCKET_NAME: !Ref CloudflareR2BucketName
          CLOUDFLARE_R2_PUBLIC_URL: !Ref CloudflareR2PublicUrl

          RESEND_API_KEY: !Ref ResendApiKey
          EMAIL_FROM: !Ref EmailFrom
          FRONTEND_URL: !Ref FrontendUrl

      Policies:
        - AWSLambdaBasicExecutionRole
        - Statement:
            - Effect: Allow
              Action: lambda:InvokeFunction
              Resource: !Sub "arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:exam-ia-backend"

      Events:
        Api:
          Type: HttpApi

Outputs:
  ExamIAApi:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${ServerlessHttpApi}.execute-api.${AWS::Region}.amazonaws.com/"
  ExamIAFunction:
    Description: "ExamIA Lambda Function ARN"
    Value: !GetAtt ExamIAFunction.Arn
