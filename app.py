import boto3
import json
import time

class Cloudwatch:
    def __init__(self,logs,region_name):
        self.client = boto3.client(logs,region_name=region_name)

    def create_loggroup(self):
        try:
            response = self.client.create_log_group(
                logGroupName="flowlogs",
                tags = {
                    'Name': 'flowlogs'
                }
            )
            print("[INFO]: Log group created successfully")
        except Exception as e:
            print(e)

    def apply_retention_policy(self):
        try:
            response = self.client.put_retention_policy(
                logGroupName='flowlogs',
                retentionInDays=60
            )
            print("[INFO]: Applied retention policy for flowlogs log group")

        except Exception as e:
            print("[ERROR]: Error occured while applying retention policy for flowlogs log group ")


class Iam_action:
    def __init__(self,iam):
        self.client = boto3.client(iam)


    def create_role(self):
        try:
            document= json.dumps({
                  "Version": "2012-10-17",
                  "Statement": [
                    {
                      "Sid": "",
                      "Effect": "Allow",
                      "Principal": {
                        "Service": "vpc-flow-logs.amazonaws.com"
                      },
                      "Action": "sts:AssumeRole"
                    }
                  ]
                })

            response = self.client.create_role(

                AssumeRolePolicyDocument= document,
                RoleName="vpcflowrole-automation",
                Description = "vpcflowrole-automation"
            )
            role_arn = response['Role']['Arn']

            print("[INFO]: IAM role has been created successfully")
        except Exception as e:
            print("[ERROR]: Error occured while creating IAM role {}".format(e))




    def create_and_attach_policy(self):
        try:
            policy_document = json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": [
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:DescribeLogGroups",
                                "logs:DescribeLogStreams",
                                "logs:PutLogEvents"
                            ],
                            "Effect": "Allow",
                            "Resource": "*"
                        }
                    ]
                })

            response_create_policy = self.client.create_policy(
                PolicyName="vpcflowpolicy-automation",
                PolicyDocument=policy_document,
                Description="vpcflowpolicy-automation"
            )

            print("[INFO]: IAM Policy has been created ")

            response_attach_policy = self.client.attach_role_policy(
                RoleName="vpcflowrole-automation",
                PolicyArn= response_create_policy['Policy']['Arn']
            )
            print("[INFO]: Attaching policy role has been completed successfully")
        except Exception as e:
            print("[ERROR]: Error occured while creating and attaching policy {}".format(e))


if __name__ == '__main__':

    iam_obj = Iam_action("iam")
    iam_obj.create_role()
    iam_obj.create_and_attach_policy()

    cloudwatch_obj = Cloudwatch("logs","eu-north-1")
    cloudwatch_obj.create_loggroup()
    cloudwatch_obj.apply_retention_policy()

