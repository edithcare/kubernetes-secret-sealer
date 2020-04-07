

import base64
import json
import os
import subprocess
import sys
import yaml
import boto3
from botocore.exceptions import ClientError, ProfileNotFound
import click
import shutil

def get_secret(secret_name, region, profile):
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
    profile_name = profile
    # Create a Secrets Manager client
    try:
        session = boto3.session.Session(profile_name=profile_name)
    except ProfileNotFound as error:
        print(error)
        sys.exit(1)

    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'DecryptionFailureException':
            raise error
        elif error.response['Error']['Code'] == 'InternalServiceErrorException':
            raise error
        elif error.response['Error']['Code'] == 'InvalidParameterException':
            raise error
        elif error.response['Error']['Code'] == 'InvalidRequestException':
            raise error
        elif error.response['Error']['Code'] == 'ResourceNotFoundException':
            raise error
        elif error.response['Error']['Code'] == 'AccessDeniedException':
            print("Access on secret not allowed. Set your AWS_PROFILE?")
            sys.exit(1)
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of
        # these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
            return None


def create_sealed_secret_json(kubctl_cmd, certfile, namespace):
    """pipe the secret first through kubectl then through kubeseal

    Arguments:
        kubctl_cmd {[String]} -- An Array of strings which builds the kubectl
                                 command to create a secret
        certfile {String} -- a path to a cert with which to encrypt the file
        namespace {String} -- the namespace in which to encrypt the secret

    Returns:
        json -- the json object containing the sealed secret
    """

    kubeseal_command = ["kubeseal"]
    if certfile:
        kubeseal_command.append(f"--cert {certfile}")
    if namespace:
        kubeseal_command.append(f"--namespace {namespace}")
    process = subprocess.run(
        " ".join(kubctl_cmd).split(" "), capture_output=True)

    if process.returncode == 0:
        kubectl_output = process.stdout
        json_output = json.loads(kubectl_output)
        seal_process = subprocess.run(" ".join(kubeseal_command).split(
            " "), input=json.dumps(json_output), capture_output=True, text=True)
        if seal_process.returncode == 0:
            seal_output = seal_process.stdout
            sealed_json = json.loads(seal_output)
        else:
            print(seal_process.stderr)
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
    secret_file = open(filename, "w")

    if output == "yaml":
        secret_file.write(yaml.dump(sealed_json))
    if output == "json":
        secret_file.write(json.dumps(sealed_json, sort_keys=True,
                                     indent=4, separators=(',', ': ')))
    secret_file.close()


@click.command()
@click.option("-p", "--profile", envvar="AWS_PROFILE", help="set the environment variable.(optional)")
@click.option("-n", "--name", required=True, help="The name of the secret to export from the AWS Secrets Manager.")
@click.option("-kns", "--namespace", help="The namespace in which the sealed secret shall be created.")
@click.option("--cert", help="The Path of the Key with which to encrypt the sealed secrets. ")
@click.option("--region", default="eu-central-1", help="The AWS Region to use (optional, default eu-central-1).")
@click.option("-f", "--filename", help="the file to which to write the sealed secret, if not set, output is to stdout.")
@click.option("-o", "--output", default="yaml", type=click.Choice(['json', 'yaml'], case_sensitive=False), help="the output format. select json or yaml (optional, default yaml).")
def main(profile=None, name=None, namespace=None, cert=None, region=None, filename=None, output=None):
    """Simple tool, that fetches a secret from AWS Secret Manager and pipes it into a kubernetes sealed secret."""
    shutil.get_archive_formats()
    for i in ["kubectl", "kubeseal"]:
        if shutil.which(i) is None:
            print (f"The necessary tool {i} cannot be found in your PATH. Please install {i} or make it available in your $PATH environment variable.")
            sys.exit(1)
    if cert:
        if not os.path.isfile(cert):
            print("PEM-file not found. exiting")
            sys.exit(1)
    name = name
    secret = get_secret(name, region, profile)
    kubctl_cmd = []
    kubctl_cmd.append(
        f"kubectl create secret generic {name} --dry-run -o json")
    sealed_json = ""

    try:
        json_secret = json.loads(secret)
        for i in json_secret:
            kubctl_cmd.append(f"--from-literal={i}={json_secret[i]}")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    try:
        sealed_json = create_sealed_secret_json(
            kubctl_cmd, cert, namespace)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    if filename:
        write_to_file(filename, output, sealed_json)

    else:
        write_to_stdout(output, sealed_json)


if __name__ == "__main__":
    main()
