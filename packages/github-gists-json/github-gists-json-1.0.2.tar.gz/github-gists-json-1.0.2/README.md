### Installation
```bash
$ pip install github-gists-json
```

### Usage
```bash
usage: python -m github_gists_json [login]
```
```bash
usage: python -m github_private_gists_json
```


### Examples
```bash
export GITHUB_TOKEN='secret'
```

```bash
python -m github_gists_json > gists.json
python -m github_gists_json LOGIN > gists.json
```

```bash
python -m github_private_gists_json > private_gists.json
```


