

import base64
import json
import os
import subprocess
import sys
import shutil
import yaml
import boto3
from botocore.exceptions import ClientError, ProfileNotFound, ParamValidationError
import click


def get_secret(secret_name, region, profile):
    """
    fetch the secret out of the secrets manager

    The Function get_secret is inspired by the code snippet in the AWS Secretsmanager console, which is by my best knowledge released under the Apache License.

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

    aws_client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        response = aws_client.get_secret_value(
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
    except ParamValidationError as error:
        print(error)
        print("MFA Token could not be validated.")
        sys.exit(1)

    else:
        if 'SecretString' in response:
            secret = response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(
                response['SecretBinary'])
            return None


def create_sealed_secret_json(kubctl_cmd, certfile, namespace, base64keys):
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
        if base64keys is not None:
            base_64(json_output, base64keys)
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
    print(f"write to file {filename}")
    secret_file = open(filename, "w")

    if output == "yaml":
        secret_file.write(yaml.dump(sealed_json))
    if output == "json":
        secret_file.write(json.dumps(sealed_json, sort_keys=True,
                                     indent=4, separators=(',', ': ')))
    secret_file.close()


def keep_keys(json_secret, keynames):
    """keep only the keys that are listed in keynames and discard any other fetched from the AWS Secretsman

    Arguments:
        json_secret {[type]} -- [description]
        keynames {[type]} -- [description]
    """
    keys_to_remove = [
        x for x in json_secret.keys() if x not in keynames.split(",")]
    for i in keys_to_remove:
        json_secret.pop(i)
    if len(json_secret) == 0:
        print("no secrets left to upload. exiting.")
        sys.exit(1)


def transform_key(json_secret, transformkey):
    """[summary]

    Arguments:
        json_secret {[type]} -- [description]
        transformkey {[type]} -- [description]
    """
    if len(json_secret) != 1:
        print("you can only rename secrets with one key/value pair")
        sys.exit(1)
    else:
        transformkey_list = transformkey.split(",")
        if len(transformkey_list) != 2:
            print("please provide exactly two keynames!")
            sys.exit(1)
        else:
            if transformkey_list[0] in json_secret.keys():
                value = json_secret.pop(transformkey_list[0])
                json_secret[transformkey_list[1]] = value
            else:
                print("key is not in secret. exiting!")


def base_64(json_output, base64keys):
    """[summary]

    Arguments:
        json_output {[type]} -- [description]
        base64 {[type]} -- [description]
    """
    keys_list = base64keys.split(",")
    for i in keys_list:
        if i not in json_output["data"].keys():
            print("key is not in secret. exiting")
            sys.exit(1)
        else:
            value = json_output["data"].pop(i)
            decoded = base64.b64decode(value)
            json_output["data"][i] = decoded.decode("utf-8")


@click.command()
@click.option("-p", "--profile", envvar="AWS_PROFILE", help="set the Profile to use for the request. If AWS_PROFILE is set, the variable is read from there, but you can always override it.")
@click.option("-n", "--name", required=True, help="The name of the secret to export from the AWS Secrets Manager.")
@click.option("-kns", "--namespace", help="The namespace in which the sealed secret shall be created. If the namespace is set in the kubernetes config, this is used as default, otherwise the default namespace is used.")
@click.option("-kn", "--sealedsecretname", help="The name in which the sealed secret shall be created. If the name is not set the name is equal to the one set in the -n Option.")
@click.option("--cert", help="The Path of the Key with which to encrypt the sealed secrets. ")
@click.option("--region", default="eu-central-1", help="The AWS Region to use (optional, default eu-central-1).")
@click.option("-f", "--filename", help="the file to which to write the sealed secret, if not set, output is to stdout.")
@click.option("-o", "--output", default="yaml", type=click.Choice(['json', 'yaml'], case_sensitive=False), help="the output format. select json or yaml (optional, default yaml).")
@click.option("-k", "--keepkeys", help="if a secret has multiple key-value-pairs, keep et only the ones listed in this commaseparated list")
@click.option("-t", "--transformkey", help="transforms the key before the comma to the name behind it")
@click.option("-b", "--base64keys", help="if the data in this comma separated list of keys is already base64 decoded deploy the value directly")
@click.option("--raw", help="dont fetch a secret from AWS but actually get a json directly from a file")
def main(profile=None, name=None, namespace=None, cert=None, region=None, filename=None, output=None, sealedsecretname=None, keepkeys=None, transformkey=None, base64keys=None, raw=None):
    """Simple tool, that fetches a secret from AWS Secret Manager and pipes it into a kubernetes sealed secret."""
    shutil.get_archive_formats()
    for i in ["kubectl", "kubeseal"]:
        if shutil.which(i) is None:
            print(
                f"The necessary tool {i} cannot be found in your PATH. Please install {i} or make it available in your $PATH environment variable.")
            sys.exit(1)
    if cert:
        if not os.path.isfile(cert):
            print("PEM-file not found. exiting")
            sys.exit(1)
    name = name
    if raw is None:
        secret = get_secret(name, region, profile)
    else:
        try:
            json.loads(raw)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

        secret = raw

    if secret is None:
        print("Query of Secretsmanager returns no result. Did you use the same 2FA Code twice? Please wait until a new one is generated.")
        sys.exit(1)

    kubctl_cmd = []
    if sealedsecretname:
        kubctl_cmd.append(
            f"kubectl create secret generic {sealedsecretname} --dry-run -o json")
    else:
        kubctl_cmd.append(
            f"kubectl create secret generic {name} --dry-run -o json")
    sealed_json = ""

    try:
        json_secret = json.loads(secret)

        if keepkeys is not None:
            keep_keys(json_secret, keepkeys)

        if transformkey is not None:
            transform_key(json_secret, transformkey)

        for i in json_secret:
            kubctl_cmd.append(f"--from-literal={i}={json_secret[i]}")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    try:
        sealed_json = create_sealed_secret_json(
            kubctl_cmd, cert, namespace, base64keys)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    if filename:
        write_to_file(filename, output, sealed_json)

    else:
        write_to_stdout(output, sealed_json)


if __name__ == "__main__":
    main()
