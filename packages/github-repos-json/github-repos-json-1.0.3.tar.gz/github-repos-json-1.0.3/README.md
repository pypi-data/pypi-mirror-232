### Installation
```bash
$ pip install github-repos-json
```

### Usage
```bash
usage: python -m github_repos_json [login]
```
```bash
usage: python -m github_private_repos_json
```


### Examples
```bash
export GITHUB_TOKEN='secret'
```

```bash
python -m github_repos_json > repos.json
python -m github_repos_json LOGIN > repos.json
```

```bash
python -m github_private_repos_json > private_repos.json
```


