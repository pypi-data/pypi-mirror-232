# HongXiongMao Refuel

Toolbox for importing data from various financial sources; 
for a personal project so if you are here by accident I highly advise you look elsewhere.


## Bloomberg API
In order to make calls to Bloomberg we must have the `blpapi` installed. 
We then extend the excellent `xbbg` package. 
One complication is the installation of `blpapi` which is a bit of a pain in the backside.

According to the [Bloomberg website](https://www.bloomberg.com/professional/support/api-library/) 
one can install using pip with:
```
python -m pip install --index-url=https://bcms.bloomberg.com/pip/simple blpapi
```

For Poetry there are [2 steps required](https://github.com/python-poetry/poetry/issues/7587):
Setting up Bloomberg as a source & then installing;
This is FYI because the pyproject.toml file should take care of this.
```
poetry source add --priority bloomberg https://bcms.bloomberg.com/pip/simple
poetry add --source bloomberg blpapi
```

## Publishing to PyPi
I'm no pro at deploying packages to PyPi, so have been following  
[this tutorial](https://www.digitalocean.com/community/tutorials/how-to-publish-python-packages-to-pypi-using-poetry-on-ubuntu-22-04)

Key points:
* (PyPi account is required)[https://pypi.org/manage/account/#account-emails]
* (Configure Poetry)[https://python-poetry.org/docs/repositories/#configuring-credentials]
* poetry build
* poetry publish

```
# configure API key
poetry config pypi-token.pypi <pypi-reallyREALLYllongKEY...>

# The build bit
(base) (hxm-refuel-py3.10) PS C:\Users\XXX\Documents\GitHub\hxm-refuel> poetry build

Building hxm-refuel (0.1.0)
  - Building sdist
  - Built hxm_refuel-0.1.0.tar.gz
  - Building wheel
  - Built hxm_refuel-0.1.0-py3-none-any.whl

# publishing bit
(base) (hxm-refuel-py3.10) PS C:\Users\T333208\Documents\GitHub\hxm-refuel> poetry publish

Publishing hxm-refuel (0.1.0) to PyPI
 - Uploading hxm_refuel-0.1.0-py3-none-any.whl 0%
 - Uploading hxm_refuel-0.1.0-py3-none-any.whl 85%
 - Uploading hxm_refuel-0.1.0-py3-none-any.whl 100%
 - Uploading hxm_refuel-0.1.0.tar.gz 0%
 - Uploading hxm_refuel-0.1.0.tar.gz 100%
```
