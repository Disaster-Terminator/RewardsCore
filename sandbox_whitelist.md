# Trae 沙盒白名单命令（前缀匹配）

## 允许命令

### Git（只读 + 安全写操作）

```text
git add
git commit
git push origin
git pull --rebase
git checkout
git branch
git status
git log
git diff
git stash
git restore
git reset HEAD
git fetch
git remote -v
git config --list
git rev-parse
git ls-files
git show
git rebase --abort
git rebase --continue
```

### Python/测试

```text
python
pytest
ruff check
ruff format
mypy
```

### pip（只读）

```text
pip list
pip show
```

### conda（只读 + 环境切换）

```text
conda activate
conda deactivate
conda env list
conda info
```

### 文件操作（安全）

```text
Move-Item
Copy-Item
New-Item -ItemType Directory
Get-Content
Set-Content
Get-ChildItem
```

## 禁止命令

```text
git push --force
git push -f
git push --force-with-lease
git rebase -i
git reset --hard
git clean

pip install
pip uninstall
conda install
conda remove
conda update

Remove-Item
```
