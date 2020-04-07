# kubernetes-secret-sealer

Get a secret from aws secrets manager and generate an kubernetes sealed secret


# Installation

If you don't use `pipsi`, you're missing out.
Here are [installation instructions](https://github.com/mitsuhiko/pipsi#readme).

Simply run:

    $ pipsi install .

On mac:

    $ pipsi install --python /opt/local/bin/python3.7 .

# Usage

To use it:

    $ kubernetes-secret-sealer --help


TODO:
- [ ] check `FileNotFoundError: [Errno 2] No such file or directory: 'kubeseal': 'kubeseal'` => Docu & Check for kubeseal
 
- [ ] check MFA error
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
 
- [ ] Option for PEM file
- [ ] Namespace Option default per ENV
- [ ] Check existing passwords and export to separate namespace k8s
- [ ] Create git repo for new DEV cluster according Syncier ArgoCD conventions
- [ ] MIT Lizens => OpenSource
- [ ] Test
- [ ] CI/CD GitHub Actions / Ggf. CircleCI + [Packages] => kostenfrei für OpenSource?
 
