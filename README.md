# kubernetes-secret-sealer

![Python application](https://github.com/edithcare/kubernetes-secret-sealer/workflows/Python%20application/badge.svg)

Get a secret from aws secrets manager and generate an kubernetes sealed secret


# Installation

If you don't use `pipsi`, you're missing out.
Here are [installation instructions](https://github.com/mitsuhiko/pipsi#readme).

Simply run:

    $ pipsi install .

On mac:

    $ pipsi install --python /opt/local/bin/python3.7 .


# Preconditions

to work as intendet, several preconditions have to be fullfilled:
* you need to have a workling configuration for aws-cli. That means access to the AWS Secretsmanager has to be available in your current configuration. You can test this with the following command: ```$ aws secretsmanager list-secrets```
* you need a working kubectl connection to the k8s-cluster to which you want to deploy the sealed secrets. you can check this via the command ```$ kubectl get secrets```
* you need to install the sealed secrets controller in the k8s cluster. You probably have done it already, otherwise you would not have an interest in using this tool. ;-) Anyway, please follow this instruction for installing the sealed secret controller: https://github.com/bitnami-labs/sealed-secrets#controller

# Usage

## Use on commandline:

```
Usage: kubernetes-secret-sealer [OPTIONS]

  Simple tool, that fetches a secret from AWS Secret Manager and pipes it
  into a kubernetes sealed secret.

Options:
  -p, --profile TEXT            set the Profile to use for the request. If
                                AWS_PROFILE is set, the variable is read from
                                there, but you can always override it.

  -n, --name TEXT               The name of the secret to export from the AWS
                                Secrets Manager.  [required]

  -kns, --namespace TEXT        The namespace in which the sealed secret shall
                                be created. If the namespace is set in the
                                kubernetes config, this is used as default,
                                otherwise the default namespace is used.

  -kn, --sealedsecretname TEXT  The name in which the sealed secret shall be
                                created. If the name is not set the name is
                                equal to the one set in the -n Option.

  --cert TEXT                   The Path of the Key with which to encrypt the
                                sealed secrets.

  --region TEXT                 The AWS Region to use (optional, default eu-
                                central-1).

  -f, --filename TEXT           the file to which to write the sealed secret,
                                if not set, output is to stdout.

  -o, --output [json|yaml]      the output format. select json or yaml
                                (optional, default yaml).

  -k, --keepkeys TEXT           if a secret has multiple key-value-pairs, keep
                                only the ones listed in this commaseparated
                                list.

  -t, --transformkey TEXT       transforms the key before the comma to the
                                name behind it
                                Example:
                                -t foo,bar will change a key 'foo' to 'bar',
                                but will leave the referenced value intact.

  -b, --base64keys TEXT         if the data in this comma separated list of
                                keys is already base64 decoded deploy the
                                value directly
                                Example:
                                if a key has an already encoded value in the
                                secrets manager, it will not encode the value
                                again when create the sealed secret.

  --raw TEXT                    dont fetch a secret from AWS but actually get
                                a json directly from a commandline parameter.
                                If you have a sealed secret from another source,
                                you can directly create a sealed secret from it.

  -tt, --templatetype           add template type to the output file. Examples: kubernetes.io/dockerconfigjson or Opaque
 
  -a, --annotations JSON        add annotations to the metadate in the output file. Examples: '{"kubernetes-deploy.shopify.io/ejson-secret": "true"}'
 
  -l, --labels JSON             add labels to the metadate in the output file. Examples: '{"name": "quay-io-sdase"}'

  --help                        Show this message and exit.

```


## Handling of secrets and workflow.

Secrets are stored and only stored in the AWS Secretsmanager. This tools writes no unencrypted secrets to the filesystem. So the workflow for using this tool is, to 
- migrate your secrets into AWS Secretsmanager. It is advised, to use the names and semantics the Secret will use in the kubernetes services later.
- create a sealed secret yaml by using the tool. Example:
```kubernetes-secret-sealer -n supersecret -p dev -kns testk8snamespace --cert ./dev-cluster.pem -o yaml -f supersecret_sealedsecret.yaml```. 
- Then you just have to apply the secret via kubectl apply: ```kubectl apply -f supersecret_sealedsecret.yaml```

# Licensing:

This Code is released under the MIT-License.
