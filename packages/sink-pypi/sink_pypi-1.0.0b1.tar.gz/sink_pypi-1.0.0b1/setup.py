# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sink',
 'sink._utils',
 'sink.resources',
 'sink.resources.casing',
 'sink.resources.company',
 'sink.resources.decorator_tests',
 'sink.resources.deeply_nested',
 'sink.resources.deeply_nested.level_one',
 'sink.resources.deeply_nested.level_one.level_two',
 'sink.resources.invalid_schemas',
 'sink.resources.mixed_params',
 'sink.resources.model_referenced_in_parent_and_child',
 'sink.resources.names',
 'sink.resources.names.reserved_names',
 'sink.resources.pagination_tests',
 'sink.resources.parent',
 'sink.resources.recursion',
 'sink.resources.resource_refs',
 'sink.resources.resource_refs.parent',
 'sink.resources.responses',
 'sink.resources.types',
 'sink.types',
 'sink.types.casing',
 'sink.types.company',
 'sink.types.decorator_tests',
 'sink.types.deeply_nested',
 'sink.types.deeply_nested.level_one',
 'sink.types.deeply_nested.level_one.level_two',
 'sink.types.invalid_schemas',
 'sink.types.mixed_params',
 'sink.types.model_referenced_in_parent_and_child',
 'sink.types.names',
 'sink.types.names.can_cause_clashes',
 'sink.types.names.reserved_names',
 'sink.types.pagination_tests',
 'sink.types.parent',
 'sink.types.recursion',
 'sink.types.resource_refs',
 'sink.types.resource_refs.parent',
 'sink.types.responses',
 'sink.types.shared',
 'sink.types.shared_params',
 'sink.types.types']

package_data = \
{'': ['*']}

install_requires = \
['anyio>=3.5.0,<4',
 'distro>=1.7.0,<2',
 'httpx>=0.23.0,<1',
 'pydantic>=1.9.0,<3',
 'typing-extensions>=4.5,<5',
 'urllib3==1.26.15']

extras_require = \
{'logging': ['structlog>=23']}

setup_kwargs = {
    'name': 'sink-pypi',
    'version': '1.0.0b1',
    'description': 'Client library for the sink API',
    'long_description': '# Sink Custom Python Title 3 API Library\n\n[![PyPI version](https://img.shields.io/pypi/v/sink-pypi.svg)](https://pypi.org/project/sink-pypi/)\n\nThe Sink Custom Python Title 3 library provides convenient access to the Sink REST API from any Python 3.7+\napplication. It includes type definitions for all request params and response fields,\nand offers both synchronous and asynchronous clients powered by [httpx](https://github.com/encode/httpx).\n\n## Documentation\n\nThe API documentation can be found [here](https://stainlessapi.com).\n\n## Installation\n\n```sh\npip install sink-pypi\n```\n\n## Usage\n\nThe full API of this library can be found in [api.md](https://www.github.com/stainless-sdks/sink-python-public/blob/master/api.md).\n\n```python\nfrom sink import Sink\n\nclient = Sink(\n    # defaults to os.environ.get("SINK_CUSTOM_API_KEY_ENV")\n    user_token="my user token",\n    # defaults to "production".\n    environment="sandbox",\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\ncard = client.cards.create(\n    type="SINGLE_USE",\n    not_="TEST",\n)\nprint(card.token)\n```\n\nWhile you can provide a `user_token` keyword argument, we recommend using [python-dotenv](https://pypi.org/project/python-dotenv/)\nand adding `SINK_CUSTOM_API_KEY_ENV="my user token"` to your `.env` file so that your user token is not stored in source control.\n\n## Async Usage\n\nSimply import `AsyncSink` instead of `Sink` and use `await` with each API call:\n\n```python\nfrom sink import AsyncSink\n\nclient = AsyncSink(\n    # defaults to os.environ.get("SINK_CUSTOM_API_KEY_ENV")\n    user_token="my user token",\n    # defaults to "production".\n    environment="sandbox",\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\n\nasync def main():\n    card = await client.cards.create(\n        type="SINGLE_USE",\n        not_="TEST",\n    )\n    print(card.token)\n\n\nasyncio.run(main())\n```\n\nFunctionality between the synchronous and asynchronous clients is otherwise identical.\n\n## Using Types\n\nNested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev), which provide helper methods for things like serializing back into json ([v1](https://docs.pydantic.dev/1.10/usage/models/), [v2](https://docs.pydantic.dev/latest/usage/serialization/)). To get a dictionary, you can call `dict(model)`.\n\nThis helps provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `"basic"`.\n\n## Pagination\n\nList methods in the Sink API are paginated.\n\nThis library provides auto-paginating iterators with each list response, so you do not have to request successive pages manually:\n\n```python\nimport sink\n\nclient = Sink(\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\nall_offsets = []\n# Automatically fetches more pages as needed.\nfor offset in client.pagination_tests.offset.list():\n    # Do something with offset here\n    all_offsets.append(offset)\nprint(all_offsets)\n```\n\nOr, asynchronously:\n\n```python\nimport asyncio\nimport sink\n\nclient = AsyncSink(\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\n\nasync def main() -> None:\n    all_offsets = []\n    # Iterate through items across all pages, issuing requests as needed.\n    async for offset in client.pagination_tests.offset.list():\n        all_offsets.append(offset)\n    print(all_offsets)\n\n\nasyncio.run(main())\n```\n\nAlternatively, you can use the `.has_next_page()`, `.next_page_info()`, or `.get_next_page()` methods for more granular control working with pages:\n\n```python\nfirst_page = await client.pagination_tests.offset.list()\nif first_page.has_next_page():\n    print(f"will fetch next page using these details: {first_page.next_page_info()}")\n    next_page = await first_page.get_next_page()\n    print(f"number of items we just fetched: {len(next_page.data)}")\n\n# Remove `await` for non-async usage.\n```\n\nOr just work directly with the returned data:\n\n```python\nfirst_page = await client.pagination_tests.offset.list()\n\nprint(\n    f"the current start offset for this page: {first_page.offset}"\n)  # => "the current start offset for this page: 1"\nfor offset in first_page.data:\n    print(offset.bar)\n\n# Remove `await` for non-async usage.\n```\n\n## Nested params\n\nNested parameters are dictionaries, typed using `TypedDict`, for example:\n\n```python\nfrom sink import Sink\n\nclient = Sink(\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\nclient.cards.create(\n    foo={\n        "bar": True,\n    },\n)\n```\n\n## File Uploads\n\nRequest parameters that correspond to file uploads can be passed as `bytes` or a tuple of `(filename, contents, media type)`.\n\n```python\nfrom pathlib import Path\nfrom sink import Sink\n\nclient = Sink(\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\ncontents = Path("foo/bar.txt").read_bytes()\nclient.files.create_multipart(\n    file=contents,\n)\n```\n\nThe async client uses the exact same interface. This example uses `aiofiles` to asynchronously read the file contents but you can use whatever method you would like.\n\n```python\nimport aiofiles\nfrom sink import Sink\n\nclient = Sink(\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\nasync with aiofiles.open("foo/bar.txt", mode="rb") as f:\n    contents = await f.read()\n\nawait client.files.create_multipart(\n    file=contents,\n)\n```\n\n## Handling errors\n\nWhen the library is unable to connect to the API (e.g., due to network connection problems or a timeout), a subclass of `sink.APIConnectionError` is raised.\n\nWhen the API returns a non-success status code (i.e., 4xx or 5xx\nresponse), a subclass of `sink.APIStatusError` will be raised, containing `status_code` and `response` properties.\n\nAll errors inherit from `sink.APIError`.\n\n```python\nimport sink\nfrom sink import Sink\n\nclient = Sink(\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\ntry:\n    client.cards.create(\n        type="an_incorrect_type",\n    )\nexcept sink.APIConnectionError as e:\n    print("The server could not be reached")\n    print(e.__cause__)  # an underlying Exception, likely raised within httpx.\nexcept sink.RateLimitError as e:\n    print("A 429 status code was received; we should back off a bit.")\nexcept sink.APIStatusError as e:\n    print("Another non-200-range status code was received")\n    print(e.status_code)\n    print(e.response)\n```\n\nError codes are as followed:\n\n| Status Code | Error Type                 |\n| ----------- | -------------------------- |\n| 400         | `BadRequestError`          |\n| 401         | `AuthenticationError`      |\n| 403         | `PermissionDeniedError`    |\n| 404         | `NotFoundError`            |\n| 422         | `UnprocessableEntityError` |\n| 429         | `RateLimitError`           |\n| >=500       | `InternalServerError`      |\n| N/A         | `APIConnectionError`       |\n\n### Retries\n\nCertain errors will be automatically retried 2 times by default, with a short exponential backoff.\nConnection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict,\n429 Rate Limit, and >=500 Internal errors will all be retried by default.\n\nYou can use the `max_retries` option to configure or disable this:\n\n```python\nfrom sink import Sink\n\n# Configure the default for all requests:\nclient = Sink(\n    # default is 2\n    max_retries=0,\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\n# Or, configure per-request:\nclient.with_options(max_retries=5).cards.list(\n    page_size=10,\n)\n```\n\n### Timeouts\n\nRequests time out after 1 minute by default. You can configure this with a `timeout` option,\nwhich accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/#fine-tuning-the-configuration):\n\n```python\nfrom sink import Sink\n\n# Configure the default for all requests:\nclient = Sink(\n    # default is 60s\n    timeout=20.0,\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\n# More granular control:\nclient = Sink(\n    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n\n# Override per-request:\nclient.with_options(timeout=5 * 1000).cards.list(\n    page_size=10,\n)\n```\n\nOn timeout, an `APITimeoutError` is thrown.\n\nNote that requests which time out will be [retried twice by default](#retries).\n\n## Default Headers\n\nWe automatically send the following headers with all requests.\n\n| Header             | Value |\n| ------------------ | ----- |\n| `My-Api-Version`   | `11`  |\n| `X-Enable-Metrics` | `1`   |\n\nIf you need to, you can override these headers by setting default headers per-request or on the client object.\n\n```python\nfrom sink import Sink\n\nclient = Sink(\n    default_headers={"My-Api-Version": "My-Custom-Value"},\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n```\n\n## Advanced\n\n### How to tell whether `None` means `null` or missing\n\nIn an API response, a field may be explicitly null, or missing entirely; in either case, its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:\n\n```py\nif response.my_field is None:\n  if \'my_field\' not in response.model_fields_set:\n    print(\'Got json like {}, without a "my_field" key present at all.\')\n  else:\n    print(\'Got json like {"my_field": null}.\')\n```\n\n### Configuring custom URLs, proxies, and transports\n\nYou can configure the following keyword arguments when instantiating the client:\n\n```python\nimport httpx\nfrom sink import Sink\n\nclient = Sink(\n    # Use a custom base URL\n    base_url="http://my.test.server.example.com:8083",\n    proxies="http://my.test.proxy.example.com",\n    transport=httpx.HTTPTransport(local_address="0.0.0.0"),\n    username="Robert",\n    required_arg_no_env="<example>",\n)\n```\n\nSee the httpx documentation for information about the [`proxies`](https://www.python-httpx.org/advanced/#http-proxying) and [`transport`](https://www.python-httpx.org/advanced/#custom-transports) keyword arguments.\n\n### Managing HTTP resources\n\nBy default we will close the underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__) is called but you can also manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.\n\n## Versioning\n\nThis package generally attempts to follow [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:\n\n1. Changes that only affect static types, without breaking runtime behavior.\n2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals)_.\n3. Changes that we do not expect to impact the vast majority of users in practice.\n\nWe take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.\n\nWe are keen for your feedback; please open an [issue](https://www.github.com/stainless-sdks/sink-python-public/issues) with questions, bugs, or suggestions.\n\n## Requirements\n\nPython 3.7 or higher.\n',
    'author': 'Sink',
    'author_email': 'dev@stainlessapi.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/stainless-sdks/sink-python-public',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
