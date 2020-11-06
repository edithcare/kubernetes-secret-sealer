# kubernetes-secret-sealer

![Python application](https://github.com/edithcare/kubernetes-secret-sealer/workflows/Python%20application/badge.svg)

> Simple tool, that fetches a secret from AWS Secret Manager and pipes it into a kubernetes sealed secret

## prerequesites
for `kubernetes-secret-sealer` to work as intended, several prerequesites have to be fulfilled:
- `pipx` installed [github.com/pipxproject/pipx](https://github.com/pipxproject/pipx)
- `aws` cli installed and permissions to access aws secretsmanager e.g. `aws secretsmanager list-secrets` [docs.aws.amazon.com/cli/latest/userguide/cli-chap-install](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)
- `kubectl` installed and permissions to access kubernetes secrest e.g. `kubectl get secrets` [kubernetes.io/docs/tasks/tools/install-kubectl/](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- `kubeseal` client installed [github.com/bitnami-labs/sealed-secrets#homebrew](https://github.com/bitnami-labs/sealed-secrets#homebrew)
- installed sealedsecrets-controller in the k8s cluster. You probably have done it already, otherwise you would not have an interest in using this tool. ;-) Please follow instructions for installing the sealedsecret-controller [github.com/bitnami-labs/sealed-secrets#controller](https://github.com/bitnami-labs/sealed-secrets#controller)

## installation
```sh
pipx install .      # will install to `$HOME/.local/bin/kubernetes-secret-sealer`. set PATH

# legacy: pipsi is no longer maintained. See pipx for an actively maintained alternative
pipsi install .
pipsi install --python /opt/local/bin/python3.7 .     # on macos
```
- `pipsi` (legacy) [installation instructions](https://github.com/mitsuhiko/pipsi#readme)

## usage
```sh
kubernetes-secret-sealer --help     # show help message and exit

# get secret from aws-secretsmanager and generate sealed-secret.yml
kubernetes-secret-sealer \
	-p $AWS_PROFILE \
	-n $AWS_SECRETS_NAME \
	-kns $KUBERNETES_NAMESPACE \
	--cert ./path/to/sealed-secret-cert.pem \
	-o yaml \
	-f ./path/to/sealed-secret.yaml \
	-b accountJsonAsString \
	-tt Opaque
```

### handling of secrets and workflow
secrets are only stored in the AWS Secretsmanager. This tools writes no unencrypted secrets to the filesystem. So the workflow for using this tool is, to
- migrate your secrets into AWS Secretsmanager. It is advised, to use the names and semantics the Secret will use in the kubernetes services later.
- create a sealed secret yaml via:
```sh
kubernetes-secret-sealer \
	-p $AWS_PROFILE \
	-n supersecret \
	-kns $KUBERNETES_NAMESPACE \
	--cert ./dev-cluster.pem \
	-o yaml \
	-f supersecret_sealedsecret.yaml
```
- then apply the secret via `kubectl apply -f supersecret_sealedsecret.yaml`
