# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/

import click
import boto3
import base64
from botocore.exceptions import ClientError
import json
import os
import subprocess
import yaml
import sys


def get_secret(secret_name, region):
    """
    fetch the secret out of the secrets manager

    Arguments:
        secret_name {String} -- The Name of the secret to fatch
        region {String} -- the aws-region of the secrets manager

    Returns:
        String -- the string containing the secret
    """
    secret_name = secret_name
    region_name = region

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            print("Access on secret not allowed. did you set your AWS_PROFILE?")
            sys.exit()
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
            return None



def create_sealed_secret_json(kubctl_cmd):
    """pipe the secret first through kubectl then through kubeseal

    Arguments:
        kubctl_cmd {[String]} -- An Array of strings which builds the kubectl command to create a secret

    Returns:
        json -- the json object containing the sealed secret
    """
    process = subprocess.run(
        " ".join(kubctl_cmd).split(" "), capture_output=True)
    if process.returncode is 0:
        kubectl_output = process.stdout
        json_output = json.loads(kubectl_output)
        seal_process = subprocess.run(["kubeseal"], input=json.dumps(
            json_output), capture_output=True, text=True)
        seal_output = seal_process.stdout
        sealed_json = json.loads(seal_output)
    else:
        print(process.stderr)
    return sealed_json


def write_to_stdout(output, sealed_json):
    """write the 

    Arguments:
        output {String} -- the output format 
        sealed_json {json} -- the json containing the sealed secret
    """
    if output == "yaml":
        print(yaml.dump(sealed_json))
    if output == "json":
        print(json.dumps(sealed_json, sort_keys=True,
                         indent=4, separators=(',', ': ')))


def write_to_file(filename, output, sealed_json):
    """writes the sealed secret to a file

    Arguments:
        filename {String} -- the filename of the sealed secret
        output {String} -- the output format
        sealed_json {json} -- the json containing the sealed secret
    """
    print("write to file "+filename)
    f = open(filename, "w")
    if output == "yaml":
        f.write(yaml.dump(sealed_json))
    if output == "json":
        f.write(json.dumps(sealed_json, sort_keys=True,
                           indent=4, separators=(',', ': ')))
    f.close()


@click.command()
@click.option("-p", "--profile", help="set the AWS_PROFILE environment variable.")
@click.option("-n", "--name", required=True, help="The name of the secret to export from the AWS Secrets Manager.")
@click.option("--region", default="eu-central-1", help="The AWS Region to use (optional).")
@click.option("-c", "--command", is_flag=True, help="only print kubectl command for creating secret.")
@click.option("-f", "--filename",  help="the file to which to write the sealed secret, if not set, output is to stdout.")
@click.option("-o", "--output", default="yaml", type=click.Choice(['json', 'yaml'], case_sensitive=False), help="the output format. select json or yaml.")
def main(profile, region, command, name, filename, output):
    """Simple tool, that fetches a secret from AWS Secret Manager and pipes it into a kubernetes sealed secret."""
    if profile:
        os.environ['AWS_PROFILE'] = profile
    name = name
    secret = get_secret(name, region)
    kubctl_cmd = []
    kubctl_cmd.append(
        f"kubectl create secret generic {name} --dry-run -o json")
    sealed_json = ""
    try:
        json_secret = json.loads(secret)
        for i in json_secret:
            kubctl_cmd.append(f"--from-literal={i}={json_secret[i]}")
        if command:
            print(" ".join(kubctl_cmd))
            return
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    try:
        sealed_json = create_sealed_secret_json(kubctl_cmd)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    if filename:
        write_to_file(filename, output, sealed_json)

    else:
        write_to_stdout(output, sealed_json)


if __name__ == "__main__":
    main()
