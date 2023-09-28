# generate_MD_links

##
generate_MD_links is a Python script that generates a Markdown file with links to all the files in a directory.

## memo for uploading to PyPI
```powershell
python setup.py sdist bdist_wheel
python -m twine upload --repository pypi dist/*
```
### update
```powershell
rm -r dist
python setup.py sdist bdist_wheel
python -m twine upload --repository pypi dist/*
```

