"""
requests.api
~~~~~~~~~~~~

This module implements the Requests API.

:copyright: (c) 2012 by Kenneth Reitz.
:license: Apache2, see LICENSE for more details.
"""
from __future__ import annotations

import typing

from . import sessions
from ._constant import DEFAULT_RETRIES, READ_DEFAULT_TIMEOUT, WRITE_DEFAULT_TIMEOUT
from ._typing import (
    BodyType,
    CacheLayerAltSvcType,
    CookiesType,
    HeadersType,
    HookType,
    HttpAuthenticationType,
    HttpMethodType,
    MultiPartFilesAltType,
    MultiPartFilesType,
    ProxyType,
    QueryParameterType,
    RetryType,
    TimeoutType,
    TLSClientCertType,
    TLSVerifyType,
)
from .models import Response

#: This is a non-thread safe in-memory cache for the AltSvc / h3
_SHARED_QUIC_CACHE: CacheLayerAltSvcType = {
    # ("pie.dev", 443): ("pie.dev", 443)
}


def request(
    method: HttpMethodType,
    url: str,
    *,
    params: QueryParameterType | None = None,
    data: BodyType | None = None,
    json: typing.Any | None = None,
    headers: HeadersType | None = None,
    cookies: CookiesType | None = None,
    files: MultiPartFilesType | MultiPartFilesAltType | None = None,
    auth: HttpAuthenticationType | None = None,
    timeout: TimeoutType | None = WRITE_DEFAULT_TIMEOUT,
    allow_redirects: bool = True,
    proxies: ProxyType | None = None,
    verify: TLSVerifyType = True,
    stream: bool = False,
    cert: TLSClientCertType | None = None,
    hooks: HookType | None = None,
    retries: RetryType = DEFAULT_RETRIES,
) -> Response:
    """Constructs and sends a :class:`Request <Request>`.

    :param method: method for the new :class:`Request` object: ``GET``, ``OPTIONS``, ``HEAD``, ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content_type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
        to add for the file.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :param hooks: (optional) Register functions that should be called at very specific moment in the request lifecycle.
    :param retries: (optional) If integer, determine the number of retry in case of a timeout or connection error.
            Otherwise, for fine gained retry, use directly a ``Retry`` instance from urllib3.
    :return: :class:`Response <Response>` object

    Usage::

      >>> import niquests
      >>> req = niquests.request('GET', 'https://httpbin.org/get')
      >>> req
      <Response HTTP/2 [200]>
    """

    # By using the 'with' statement we are sure the session is closed, thus we
    # avoid leaving sockets open which can trigger a ResourceWarning in some
    # cases, and look like a memory leak in others.
    with sessions.Session(
        quic_cache_layer=_SHARED_QUIC_CACHE, retries=retries
    ) as session:
        return session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            hooks=hooks,
            stream=stream,
            verify=verify,
            cert=cert,
            json=json,
        )


def get(
    url: str,
    params: QueryParameterType | None = None,
    *,
    headers: HeadersType | None = None,
    cookies: CookiesType | None = None,
    auth: HttpAuthenticationType | None = None,
    timeout: TimeoutType | None = READ_DEFAULT_TIMEOUT,
    allow_redirects: bool = True,
    proxies: ProxyType | None = None,
    verify: TLSVerifyType = True,
    stream: bool = False,
    cert: TLSClientCertType | None = None,
    hooks: HookType | None = None,
    retries: RetryType = DEFAULT_RETRIES,
) -> Response:
    r"""Sends a GET request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :param hooks: (optional) Register functions that should be called at very specific moment in the request lifecycle.
    :param retries: (optional) If integer, determine the number of retry in case of a timeout or connection error.
            Otherwise, for fine gained retry, use directly a ``Retry`` instance from urllib3.
    :return: :class:`Response <Response>` object
    """

    return request(
        "GET",
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
        hooks=hooks,
        retries=retries,
    )


def options(
    url: str,
    *,
    params: QueryParameterType | None = None,
    headers: HeadersType | None = None,
    cookies: CookiesType | None = None,
    auth: HttpAuthenticationType | None = None,
    timeout: TimeoutType | None = READ_DEFAULT_TIMEOUT,
    allow_redirects: bool = True,
    proxies: ProxyType | None = None,
    verify: TLSVerifyType = True,
    stream: bool = False,
    cert: TLSClientCertType | None = None,
    hooks: HookType | None = None,
    retries: RetryType = DEFAULT_RETRIES,
) -> Response:
    r"""Sends an OPTIONS request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :param hooks: (optional) Register functions that should be called at very specific moment in the request lifecycle.
    :param retries: (optional) If integer, determine the number of retry in case of a timeout or connection error.
            Otherwise, for fine gained retry, use directly a ``Retry`` instance from urllib3.

    :return: :class:`Response <Response>` object
    """

    return request(
        "OPTIONS",
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
        hooks=hooks,
        retries=retries,
    )


def head(
    url: str,
    *,
    params: QueryParameterType | None = None,
    headers: HeadersType | None = None,
    cookies: CookiesType | None = None,
    auth: HttpAuthenticationType | None = None,
    timeout: TimeoutType | None = READ_DEFAULT_TIMEOUT,
    allow_redirects: bool = False,
    proxies: ProxyType | None = None,
    verify: TLSVerifyType = True,
    stream: bool = False,
    cert: TLSClientCertType | None = None,
    hooks: HookType | None = None,
    retries: RetryType = DEFAULT_RETRIES,
) -> Response:
    r"""Sends a HEAD request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :param hooks: (optional) Register functions that should be called at very specific moment in the request lifecycle.
    :param retries: (optional) If integer, determine the number of retry in case of a timeout or connection error.
            Otherwise, for fine gained retry, use directly a ``Retry`` instance from urllib3.

    :return: :class:`Response <Response>` object
    """

    return request(
        "HEAD",
        url,
        allow_redirects=allow_redirects,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        timeout=timeout,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
        hooks=hooks,
        retries=retries,
    )


def post(
    url: str,
    data: BodyType | None = None,
    json: typing.Any | None = None,
    *,
    params: QueryParameterType | None = None,
    headers: HeadersType | None = None,
    cookies: CookiesType | None = None,
    files: MultiPartFilesType | MultiPartFilesAltType | None = None,
    auth: HttpAuthenticationType | None = None,
    timeout: TimeoutType | None = WRITE_DEFAULT_TIMEOUT,
    allow_redirects: bool = True,
    proxies: ProxyType | None = None,
    verify: TLSVerifyType = True,
    stream: bool = False,
    cert: TLSClientCertType | None = None,
    hooks: HookType | None = None,
    retries: RetryType = DEFAULT_RETRIES,
) -> Response:
    r"""Sends a POST request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content_type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
        to add for the file.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :param hooks: (optional) Register functions that should be called at very specific moment in the request lifecycle.
    :param retries: (optional) If integer, determine the number of retry in case of a timeout or connection error.
            Otherwise, for fine gained retry, use directly a ``Retry`` instance from urllib3.

    :return: :class:`Response <Response>` object
    """

    return request(
        "POST",
        url,
        data=data,
        json=json,
        params=params,
        headers=headers,
        cookies=cookies,
        files=files,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
        hooks=hooks,
        retries=retries,
    )


def put(
    url: str,
    data: BodyType | None = None,
    *,
    json: typing.Any | None = None,
    params: QueryParameterType | None = None,
    headers: HeadersType | None = None,
    cookies: CookiesType | None = None,
    files: MultiPartFilesType | MultiPartFilesAltType | None = None,
    auth: HttpAuthenticationType | None = None,
    timeout: TimeoutType | None = WRITE_DEFAULT_TIMEOUT,
    allow_redirects: bool = True,
    proxies: ProxyType | None = None,
    verify: TLSVerifyType = True,
    stream: bool = False,
    cert: TLSClientCertType | None = None,
    hooks: HookType | None = None,
    retries: RetryType = DEFAULT_RETRIES,
) -> Response:
    r"""Sends a PUT request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content_type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
        to add for the file.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :param hooks: (optional) Register functions that should be called at very specific moment in the request lifecycle.
    :param retries: (optional) If integer, determine the number of retry in case of a timeout or connection error.
            Otherwise, for fine gained retry, use directly a ``Retry`` instance from urllib3.

    :return: :class:`Response <Response>` object
    """

    return request(
        "PUT",
        url,
        data=data,
        params=params,
        json=json,
        headers=headers,
        cookies=cookies,
        files=files,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
        hooks=hooks,
        retries=retries,
    )


def patch(
    url: str,
    data: BodyType | None = None,
    *,
    json: typing.Any | None = None,
    params: QueryParameterType | None = None,
    headers: HeadersType | None = None,
    cookies: CookiesType | None = None,
    files: MultiPartFilesType | MultiPartFilesAltType | None = None,
    auth: HttpAuthenticationType | None = None,
    timeout: TimeoutType | None = WRITE_DEFAULT_TIMEOUT,
    allow_redirects: bool = True,
    proxies: ProxyType | None = None,
    verify: TLSVerifyType = True,
    stream: bool = False,
    cert: TLSClientCertType | None = None,
    hooks: HookType | None = None,
    retries: RetryType = DEFAULT_RETRIES,
) -> Response:
    r"""Sends a PATCH request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param data: (optional) Dictionary, list of tuples, bytes, or file-like
        object to send in the body of the :class:`Request`.
    :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param files: (optional) Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
        ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
        or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content_type'`` is a string
        defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
        to add for the file.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :param hooks: (optional) Register functions that should be called at very specific moment in the request lifecycle.
    :param retries: (optional) If integer, determine the number of retry in case of a timeout or connection error.
            Otherwise, for fine gained retry, use directly a ``Retry`` instance from urllib3.

    :return: :class:`Response <Response>` object
    """

    return request(
        "PATCH",
        url,
        data=data,
        params=params,
        json=json,
        headers=headers,
        cookies=cookies,
        files=files,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
        hooks=hooks,
        retries=retries,
    )


def delete(
    url: str,
    *,
    params: QueryParameterType | None = None,
    headers: HeadersType | None = None,
    cookies: CookiesType | None = None,
    auth: HttpAuthenticationType | None = None,
    timeout: TimeoutType | None = WRITE_DEFAULT_TIMEOUT,
    allow_redirects: bool = True,
    proxies: ProxyType | None = None,
    verify: TLSVerifyType = True,
    stream: bool = False,
    cert: TLSClientCertType | None = None,
    hooks: HookType | None = None,
    retries: RetryType = DEFAULT_RETRIES,
) -> Response:
    r"""Sends a DELETE request.

    :param url: URL for the new :class:`Request` object.
    :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string for the :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
    :param timeout: (optional) How many seconds to wait for the server to send data
        before giving up, as a float, or a :ref:`(connect timeout, read
        timeout) <timeouts>` tuple.
    :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
    :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
    :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``.
    :param stream: (optional) if ``False``, the response content will be immediately downloaded.
    :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
    :param hooks: (optional) Register functions that should be called at very specific moment in the request lifecycle.
    :param retries: (optional) If integer, determine the number of retry in case of a timeout or connection error.
            Otherwise, for fine gained retry, use directly a ``Retry`` instance from urllib3.

    :return: :class:`Response <Response>` object
    """

    return request(
        "DELETE",
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
        hooks=hooks,
        retries=retries,
    )
