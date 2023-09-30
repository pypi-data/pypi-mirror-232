# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from ...._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ...._utils import maybe_transform
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._base_client import make_request_options
from ....types.names.reserved_names import Export, method_export_params

__all__ = ["Methods", "AsyncMethods"]


class Methods(SyncAPIResource):
    def export(
        self,
        class_: str,
        *,
        let: str | NotGiven = NOT_GIVEN,
        const: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Export:
        """
        Test reserved word in method name

        Args:
          let: test reserved word in query parameter

          const: test reserved word in body property

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            f"/names/reserved_names/methods/export/{class_}",
            body=maybe_transform({"const": const}, method_export_params.MethodExportParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"let": let}, method_export_params.MethodExportParams),
            ),
            cast_to=Export,
        )


class AsyncMethods(AsyncAPIResource):
    async def export(
        self,
        class_: str,
        *,
        let: str | NotGiven = NOT_GIVEN,
        const: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> Export:
        """
        Test reserved word in method name

        Args:
          let: test reserved word in query parameter

          const: test reserved word in body property

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            f"/names/reserved_names/methods/export/{class_}",
            body=maybe_transform({"const": const}, method_export_params.MethodExportParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
                query=maybe_transform({"let": let}, method_export_params.MethodExportParams),
            ),
            cast_to=Export,
        )
