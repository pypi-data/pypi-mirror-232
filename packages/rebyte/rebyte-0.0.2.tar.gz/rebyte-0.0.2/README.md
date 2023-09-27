# Rebyte Python Library

The Rebyte Python library provides convenient access to the Rebyte API
from applications written in the Python language. It includes a
pre-defined set of classes for API resources that initialize
themselves dynamically from API responses which makes it compatible
with a wide range of versions of the Rebyte API.

## Installation

To start, ensure you have Python 3.7.1 or newer. If you just
want to use the package, run:

```sh
pip install --upgrade rebyte
```

After you have installed the package, import it at the top of a file:

```python
import rebyte
```

To install this package from source to make modifications to it, run the following command from the root of the repository:

```sh
python setup.py install
```

## Usage

The library needs to be configured with your account's secret key which is available on the [website](https://rebyte.ai).

### Call callable

```python
from rebyte import RebyteAPIRequestor
requestor = RebyteAPIRequestor(
            key=<your api_key>,
            api_base=<rebyte endpoint, default to https://rebyte.ai>
        )
path = f'/api/sdk/p/{your project_id}/a/{your callable_id}/r'
res, _, _ = requestor.request(
    method="POST",
    stream=False, # or True
    url=path,
    params=data
)
print(res)
```

### Async API

Async support is available in the API by prepending `a` to a network-bound method:

```python
from rebyte import RebyteAPIRequestor
requestor = RebyteAPIRequestor(
            key=<your api_key>,
            api_base=<rebyte endpoint, default to https://rebyte.ai>
        )
path = f'/api/sdk/p/{your project_id}/a/{your callable_id}/r'
res, _, _ = await requestor.arequest(
    method="POST",
    stream=False, # or True
    url=path,
    params=data
)
print(res)
```
