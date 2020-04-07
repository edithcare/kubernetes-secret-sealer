# kubernetes-secret-sealer

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
  -p, --profile TEXT        set the Profile to use for the request. If
                            AWS_PROFILE is set, the variable is read from
                            there, but you can always override it.

  -n, --name TEXT           The name of the secret to export from the AWS
                            Secrets Manager.  [required]

  -kns, --namespace TEXT    The namespace in which the sealed secret shall be
                            created. If the namespace is set in the kubernetes
                            config, this is used as default, otherwise the
                            default namespace is used.

  --cert TEXT               The Path of the Key with which to encrypt the
                            sealed secrets.

  --region TEXT             The AWS Region to use (optional, default eu-
                            central-1).

  -f, --filename TEXT       the file to which to write the sealed secret, if
                            not set, output is to stdout.

  -o, --output [json|yaml]  the output format. select json or yaml (optional,
                            default yaml).

  --help                    Show this message and exit.
```


## Handling of secrets and workflow.

Secrets are stored and only stored in the AWS Secretsmanager. This tools writes no unencrypted secrets to the filesystem. So the workflow for using this tool is, to 
- migrate your secrets into AWS Secretsmanager. Use the names the Secret will use in the kubernetes services later. This is vital, because the tool gives you no posibility to change name of sealed secrets later on.
- create a sealed secret yaml by using the tool. Example:
```kubernetes-secret-sealer -n supersecret -p dev -kns testk8snamespace --cert ./dev-cluster.pem -o yaml -f supersecret_sealedsecret.yaml```. 
- Then you just have to apply the secret via kubectl apply: ```kubectl apply -f supersecret_sealedsecret.yaml```

# Licensing:

This Code is under the MIT-License. The Function get_secret is inspired by the code snippet in the AWS Secretsmanager console, and is by my best knowledge released under the Apache License.

Copyright (c) 2020 Michael Gröning

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# TODO:
- [x] check `FileNotFoundError: [Errno 2] No such file or directory: 'kubeseal': 'kubeseal'` => Docu & Check for kubeseal
 
- [x] check MFA error
```sh
MFA: ....

Unexpected error: <class 'TypeError'>
Traceback (most recent call last):
  File "/Users/david/.local/bin/kubernetes-secret-sealer", line 8, in <module>
    sys.exit(main())
  File "/Users/david/.local/venvs/kubernetes-secret-sealer/lib/python3.7/site-packages/click/core.py", line 829, in __call__
    return self.main(*args, **kwargs)
  File "/Users/david/.local/venvs/kubernetes-secret-sealer/lib/python3.7/site-packages/click/core.py", line 782, in main
    rv = self.invoke(ctx)
  File "/Users/david/.local/venvs/kubernetes-secret-sealer/lib/python3.7/site-packages/click/core.py", line 1066, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/Users/david/.local/venvs/kubernetes-secret-sealer/lib/python3.7/site-packages/click/core.py", line 610, in invoke
    return callback(*args, **kwargs)
  File "/Users/david/.local/venvs/kubernetes-secret-sealer/lib/python3.7/site-packages/sealer/cli.py", line 141, in main
    json_secret = json.loads(secret)
  File "/opt/local/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/json/__init__.py", line 341, in loads
    raise TypeError(f'the JSON object must be str, bytes or bytearray, '
TypeError: the JSON object must be str, bytes or bytearray, not NoneType

```
 
- [x] Option for PEM file
- [x] Namespace Option default per ENV
- [ ] Check existing passwords and export to separate namespace k8s
- [ ] Create git repo for new DEV cluster according Syncier ArgoCD conventions
- [ ] MIT Lizens => OpenSource
- [ ] Test
- [ ] CI/CD GitHub Actions / Ggf. CircleCI + [Packages] => kostenfrei für OpenSource?
 
