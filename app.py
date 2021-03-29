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
            #print(response['Logs']['Arn'])
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
            return role_arn
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



class Vpc_action(Iam_action,Cloudwatch):

    def __init__(self,service_name,region_name):
        if region_name:
            self.client = boto3.client(service_name,region_name=region_name)
        else:
            self.client = boto3.client(service_name)

    def enable_vpc_flow_logs(self,vpc_id,role_name,loggroup):

        try:
            self.client.create_flow_logs(
                DeliverLogsPermissionArn=role_name,
                LogGroupName=loggroup,
                ResourceIds=vpc_id,
                ResourceType="VPC",
                TrafficType="ALL",
                LogDestinationType="cloud-watch-logs"
            )
            print("[INFO] VPC FLOW logs are enabled for {}".format(vpc_id))
        except Exception as e:
            print("[ERROR]: Error occured while enabling VPC FLOW Logs on {} ..{}".format(vpc_id,e))





if __name__ == '__main__':


    iam_obj = Vpc_action("iam",region_name=None)
    role_name = iam_obj.create_role()
    iam_obj.create_and_attach_policy()

    cloudwatch_obj = Vpc_action("logs","eu-north-1")
    cloudwatch_obj.create_loggroup()
    cloudwatch_obj.apply_retention_policy()

    vpc_obj = Vpc_action("ec2","eu-north-1")
    vpc_obj.enable_vpc_flow_logs(vpc_id=["vpc-0b4064180d24b0acb"],role_name=role_name,loggroup="flowlogs")



