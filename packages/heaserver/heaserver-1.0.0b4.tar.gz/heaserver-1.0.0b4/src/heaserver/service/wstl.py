"""
Implements the Web Service Transition Language (WeSTL) document format, which is specified at
http://rwcbook.github.io/wstl-spec/.

This format is used to drive the server-side representor pattern, described at
https://github.com/the-hypermedia-project/charter. The WeSTL format exists in two different 'states'. In
its design-time state, it contains the list of all possible state transitions for a Web service. In its runtime state,
it contains the list of the selected transitions for the current resource along with any data associated with that
resource. The design-time document can be used to define all possible transitions including possible arguments for
querying or writing data. The runtime document can be passed to a module in the heaserver.representor package that can
turn the WeSTL document into a representation format (HTML, Collection+JSON, HAL, etc.).

WeSTL documents have the following format:
{
  "wstl": {
    "actions": [...]
    "data": [...]
  }
}
The state transitions are listed in the "actions" property. Runtime WeSTL documents additionally have a "data" property
containing a list of data items. In HEA, the data items are name-value-pair JSON objects. Actions have the following
properties:
{
  "name": the unique name of the state transition. HEA uses the following naming convention:
  <package-name>-<lowercase-HEADesktopObject-class-name>-<verb-phrase-describing-the-state-transition>, for example,
  heaserver-registry-component-get-properties.
  "type": safe or unsafe, depending on whether the state transition will cause data to be written.
  "target": a space separated list of string values that tag the action for a representor to control how it is rendered.
  HEA defines the following target values that are combined to render actions differently:
    cj: for use in Collection+JSON documents. The action will not render in a Collection+JSON document without this tag
    or the cj-template tag (see below).
    item: applies to each item in the data list, for example, renders a separate link for each item.
    list: applies to the whole data list, for example, renders a single link for the entire list.
    cj-template: for rendering as a template in Collection+JSON documents. Use item or list to indicate whether the
      template should apply to the first item in the document or all items in the document (there can be only one
      template per document).
    read: together with item and cj, renders as a link for each item in a Collection+JSON document.
    href: together with item and cj, renders as bare href and rel properties for each item in a Collection+JSON document.
    add: for templates, will populate the default value of a form field with the corresponding WSTL action's value.
  "prompt": text to use in buttons or hyperlinks generated from the action.
  "href": included at runtime, the URL to go to if the link is followed.
  "rel": contains an array of link relation values, as defined in RFC5988 (https://datatracker.ietf.org/doc/html/rfc5988).
  HEA reserves the "hea-" and "hea-data-" prefixes for relation values and defines the following standard set of
  relation values:
    hea-opener: a link to the content of an openable HEADesktopObject.
    hea-opener-choices: a link to choices for opening an openable HEADesktopObject.
    hea-context-aws: a link that applies to Amazon Web Services-related contexts.
    hea-default: a default value. It is used together with hea-opener to denote the default choice among opener choices.
    If a value beginning with hea-context- is present, there may be multiple links tagged with this value, one per
      context.
    hea-icon-duplicator: Instructs the client to use a duplicator icon when displaying the link on screen. The client
      is expected to map this rel value to an appropriate icon.
    hea-icon-mover: Instructs the client to use a mover icon when displaying the link on screen. The client is expected
      to map this rel value to an appropriate icon.
    hea-properties: a link to a form to edit the properties of the desktop object.
    hea-desktop-object: a link to a form to edit the properties of an associated desktop object.
    mime types: links to the content of an openable HEADesktopObject must include supported MIME types among their
      link relation values.
    hea-actual: a link to an Item's actual value.
    hea-volume: a link to the object's volume.
    hea-account: a link to the object's account, if there is one.
    hea-person: the person associated with this object, if different from the object's owner.
    hea-context-menu-item: indicates that this link should be included as an item of the object's context menu.
    hea-trash: a link to the trash bin for this object's volume.
    hea-dynamic-standard: instructs the client to generate a form using a Collection+JSON template retrieved from the
      backend with a GET call to the URL in the link. The client then POSTs or PUTs the completed form to the same URL,
      which saves the form contents on the backend. A POST call is expected to return a 201 status code if successful,
      with an empty response body and the URL of the created object in the response's Location header. A successful PUT
      call is expected to return a 204 status code with an empty response body. The decision to make a POST or PUT call
      is made by the client based on whether the template is being used to create a new desktop object or update an
      existing object.
    hea-dynamic-clipboard: same as hea-dynamic-standard, except the client must submit the completed form in a POST
      call to the URL from which it got the form template. The POST call must return a 200 status code if successful,
      and the body must contain a heaobject.data.ClipboardData object. The client is expected to copy the data property
      to the system clipboard, using the mime_type property as needed.
    hea-system-menu-item: denotes menu items for the client application's system menu. It is currently only used by the
      HEA Server People Microservice. What happens next depends on the link's rel values:
        hea-dynamic-standard: the application must follow the link and present the desktop object or object metadata in
          the response. The HTTP response to the link's URL is assumed to return a 200 status code if successful and
          contain zero or more desktop objects in a supported format such as Collection+JSON. For data objects, the
          client application may use the objects' mime types and/or a mime type listed in the link's relation values to
          control its behavior. Mime types listed in the link's relation values would typically be the expected mime
          types of the objects in the HTTP response.
        hea-dynamic-clipboard: the application must follow the link and request a response type that includes a form
          template such as Collection+JSON. The application must then present a form based on the template. Upon form
          submission, the application must place the response body on the system clipboard if the HTTP response has a
          200 status code.
    hea-user-menu-item: denotes menu items for the client application's user menu. It is currently only used by the HEA
      Server People Microservice. What happens next depends on the link's rel values:
        hea-dynamic-standard: the application must follow the link and present the desktop object or object metadata in
          the response. The HTTP response to the link's URL is assumed to return a 200 status code if successful and
          contain zero or more desktop objects in a supported format such as Collection+JSON. For data objects, the
          client application may use the objects' mime types and/or a mime type listed in the link's relation values to
          control its behavior. Mime types listed in the link's relation values would typically be the expected mime
          types of the objects in the HTTP response.
        hea-dynamic-clipboard: the application must follow the link and request a response type that includes a form
          template such as Collection+JSON. The application must then present a form based on the template. Upon form
          submission, the application must place the response body on the system clipboard if the HTTP response has a
          200 status code.

  Relation values with the "headata-" prefix are to be used to denote link hrefs that should be used as template
  values. For eample, an action with relation values "headata-destination" will populate a template field with name
  "destination".
  Additionally, the "self" relation value is only applicable to a getter of one object and denotes a state transition
  to the same object as described in RFC 5988. The action's URL should be the object's canonical URL.
}

Actions may have a list of inputs, as described in the WeSTL specification, that can be used to generate form templates
for display in the client-side user interface. Completed forms are then sent from the client to the server in POST and
PUT requests, and they may be parsed by a representor module to create a dictionary of key-value pairs corresponding to
the completed form fields. In most cases, these key-value pairs correspond to the fields of a HEA desktop object, in
which case a HEA desktop object's from_dict() method can be used to ingest the form fields values. Representor modules
are required to parse form field values into a dictionary in which the key-value pairs appear in the same order as form
field values, and the HEA desktop object from_dict() method will read the key-value pairs and set the corresponding
fields in order of appearance. In situations where a desktop object has dependent fields (i.e., setting one field
updates another), you have three choices: 1) rely on the form field order to ensure that the corresponding HEA desktop
object fields are set in a sensible order (at the possible expense of form fields appearing out of sync in the client);
2) duplicate the dependencies' logic in your client-side form so that the form field order is irrelevant, which means
having to create a custom form rather than relying on the WeSTL inputs to generate the form dynamically; 3) for groups
of dependent form fields, include only one of them in the form. Generally, you will want to choose option 3.

This module provides a class and functions for creating WeSTL design-time and run-time documents in JSON format, and
validating those documents.

HEA follows the WeSTL spec with the following exceptions and extensions:
* Action names should use the following convention, all lowercase with dashes between words:
<project_slug>-<heaobject_classname>-<verb_describing_action>, for example, heaobject-registry-component-get-properties.
Failure to follow this convention could result in collisions between your action names and any action names added to
core HEA in the future.
* We extended the runtime document's inputs with a hea property, whose value must be an object with any of the
following properties:
    * href: the resource URL of the data, usually the request URL.
    * type: an extended set of form field types:
      object-url: the URL of an object as a string.
      datetime: an ISO date-time value.
    * section: combines related form fields to be rendered together on screen, such as in a HTML field set.
    * sectionPrompt: the display name of the section. It is required on the first form field of the section.
    * optionsFromUrl: gets a list of options from a HEA desktop object endpoint. This property's value is an object
    with the following properties:
      path: the path of the endpoint, not including the base URL of the API gateway.
      value: the property of the returned options to use as the id field of the select.
      text: the property of the returned options to use as the display name of the select.
    * display: true or false to make this form field visible or hidden.
    * object-url-target-types-include: a list of type strings that are permitted in the object-url form field. Goes
    together with "object-url" in the hea type field.

"""

import copy
import functools
import logging
import pkgutil
import json
import jsonmerge  # type: ignore
from collections import abc
from aiohttp.web import Request, Response
from typing import Optional, Callable, Dict, Any, Coroutine, List, Union
from . import appproperty, requestproperty, jsonschemavalidator, jsonschema
from yarl import URL
from .util import check_duplicates, DuplicateError

DEFAULT_DESIGN_TIME_WSTL = {
    '$schema': 'http://json-schema.org/draft-07/schema#',
    'wstl': {
        "actions": []
    }
}


class RuntimeWeSTLDocumentBuilder:
    """
    A run-time WeSTL document builder. Call instance of this class to produce a run-time WeSTL document.
    """

    def __init__(self, design_time_wstl: Optional[Dict[str, Any]] = None,
                 href: Optional[Union[str, URL]] = None) -> None:
        """
        Constructs a run-time WeSTL document with a design-time WeSTL document.

        :param design_time_wstl: a dict representing a design-time WeSTL document. If omitted, the
        DEFAULT_DESIGN_TIME_WSTL design-time WeSTL document will be used. Assumes that the design-time WeSTL document
        is valid.
        :param href: The URL associated with the resource (optional).
        """
        _logger = logging.getLogger(__name__)
        self.__orig_design_time_wstl = copy.deepcopy(design_time_wstl if design_time_wstl else DEFAULT_DESIGN_TIME_WSTL)
        self.__design_time_wstl = copy.deepcopy(self.__orig_design_time_wstl)
        _logger.debug('Design-time WeSTL document is %s', self.__design_time_wstl)
        self.__run_time_wstl = copy.deepcopy(self.__design_time_wstl)
        self.__run_time_wstl['wstl']['actions'] = []
        self.__actions = {action_['name']: action_ for action_ in self.__design_time_wstl['wstl'].get('actions', [])}
        self.__run_time_actions: Dict[str, Any] = {}
        if href is not None:
            self.__run_time_wstl['wstl'].setdefault('hea', {})['href'] = str(href)

    def clear(self):
        _logger = logging.getLogger(__name__)
        self.__design_time_wstl = copy.deepcopy(self.__orig_design_time_wstl)
        self.__run_time_wstl = copy.deepcopy(self.__design_time_wstl)
        self.__run_time_wstl['wstl']['actions'] = []
        self.__actions = {action_['name']: action_ for action_ in self.__design_time_wstl['wstl'].get('actions', [])}
        self.__run_time_actions: Dict[str, Any] = {}
        _logger.debug('Cleared run-time WeSTL document builder')

    def find_action(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Low level finder of actions in the design-time WeSTL document.

        :param name: the name of the action of interest.
        :return: A copy of the first action found with the given name, or None
        if not found.
        """
        a = self.__actions.get(name)
        if a:
            return copy.deepcopy(a)
        else:
            return None

    def has_run_time_action(self, name: str):
        return name in self.__run_time_actions

    def add_run_time_action(self, name: str,
                            path: str | None = None,
                            rel: Union[str, List[str]] | None = None,
                            root: str | None = None,
                            itemif: str | None = None) -> None:
        """
        Append an action from the design-time WeSTL document to the run-time
        WeSTL document.

        An action has a name that is used to match it to a state transition in
        the design-time WeSTL document. The properties of the state transition
        are pulled into the action. It also has rel values as described in IETF
        RFC5988 (https://datatracker.ietf.org/doc/html/rfc5988), and an itemif
        expression that conditionally appends the action depending on the data
        in the WeSTL document. Finally, it has an href that is created by
        concatenating the root and path parameters. Before the root and the path
        are concatenated, a trailing slash is added to the root if not already
        present. If a root is provided, the path must be relative (not contain a
        leading slash).


        :param name: the action's name. Required. Action names should use the
        following convention, all lowercase with dashes between words:
        <project_slug>-<heaobject_classname>-<verb_describing_action>, for
        example, heaobject-registry-component-get-properties. Failure to follow
        this convention could result in collisions between your action names
        and any action names added to core HEA in the future.
        :param path: the path of the action, plus any fragment and query string.
        :param rel: a list of HTML rel attribute values, or the list as a
        space-delimited string.
        :param root: the root of the action URL (everything except the path
        above).
        :param itemif: an expression string for determining whether to apply
        an action to an item in the wstl document (optional).
        """
        _logger = logging.getLogger(__name__)
        rel_: Optional[List[str]] = None
        if rel is not None and not isinstance(rel, list):
            rel_ = str(rel).split()
        else:
            rel_ = rel
        if name in self.__run_time_actions:
            raise ValueError(f'Duplicate run-time action {name}')
        tran = self.__make(name, path=path, rel=rel_, root=root, itemif=itemif)
        _logger.debug('Adding base action %s', tran)
        self.__run_time_wstl['wstl']['actions'].append(tran)
        self.__run_time_actions[name] = tran

    def has_design_time_action(self, name: str):
        return name in self.__actions

    def add_design_time_action(self, action_: Dict[str, Any]) -> None:
        """
        Append an action to the design-time WeSTL document.

        :param action_: a WeSTL action object dict. Required.
        """
        if not action_:
            raise ValueError('action_ cannot be None')
        try:
            jsonschemavalidator.WSTL_ACTION_SCHEMA_VALIDATOR.validate(action_)
            actions = self.__design_time_wstl['wstl']['actions']
            if action_['name'] not in self.__actions:
                action__ = copy.deepcopy(action_)
                actions.append(action__)
                self.__actions[action_['name']] = action__
            else:
                raise ValueError(f'Existing action with name {action_["name"]} found in the design-time document')
        except jsonschemavalidator.ValidationError as e:
            raise ValueError from e

    @property
    def href(self) -> Optional[str]:
        wstl = self.__run_time_wstl['wstl']
        return wstl['hea'].get('href') if 'hea' in wstl else None

    @href.setter
    def href(self, href: Optional[str]) -> None:
        """
        The href of the data in the run-time WeSTL document.
        """
        self.__run_time_wstl['wstl'].setdefault('hea', {})['href'] = str(href)

    @href.deleter
    def href(self) -> None:
        wstl = self.__run_time_wstl['wstl']
        if 'hea' in wstl:
            wstl['hea'].pop('href', None)

    @property
    def data(self) -> list:
        return self.__run_time_wstl['wstl'].get('data', None)

    @data.setter
    def data(self, data) -> None:
        """
        The data object of the run-time WeSTL document. The data is expected to be a mapping or sequence of mappings.
        """
        if isinstance(data, abc.Mapping):
            self.__run_time_wstl['wstl']['data'] = [data]
        elif not all(isinstance(elt, abc.Mapping) for elt in data):
            raise TypeError(f'List data must be a list of mappings but instead was {data}')
        elif data:
            self.__run_time_wstl['wstl']['data'] = data
        else:
            self.__run_time_wstl['wstl'].pop('data', None)

    @data.deleter
    def data(self) -> None:
        self.__run_time_wstl['wstl'].pop('data', None)

    def find_by_target(self, val: str):
        return [tran for tran in self.__run_time_wstl['wstl']['actions'] if 'target' in tran and val in tran['target']]

    @property
    def design_time_document(self) -> Dict[str, Any]:
        """
        Returns a copy of the design-time WeSTL document.

        :return: a dict representing the design-time WeSTL document.
        """
        return copy.deepcopy(self.__design_time_wstl)

    def __call__(self) -> Dict[str, Any]:
        """
        Returns a copy of the run-time WeSTL document.

        :return: a dict representing the run-time WeSTL document.
        """
        return copy.deepcopy(self.__run_time_wstl)

    def __make(self, name: str, path: str | None = None, rel: List[str] | None = None,
               root: str | None = None, itemif: str | None = None) -> Dict[str, Any]:
        """
        Create a run-time state transition combining the named design-time state
        transition and the provided action properties. In addition to the named
        state transition's properties as found in the design-time WeSTL
        document, the returned dict contains the provided itemif property
        value, and it contains an href property created by concatenating the
        root URL and the path for client applications to execute the state
        transition. Before the root and the path are concatenated, a trailing
        slash is added to the root if not already present. If a root is
        provided, the path must be relative (not contain a leading slash).

        :param name: the state transition name. Required.
        :param path: the path and fragment parts of the action URL.
        :param rel: a space-separated list of relation values to include in the
        run-time state transition.
        :param root: the base URL to which the path is concatenated, creating
        a URL for client applications to execute the state transition.
        :param itemif: an expression string for determining whether to apply
        an action to an item in the wstl document (optional).
        :return: the created state transition.
        :raises ValueError: if no name was provided.
        """
        if not name:
            raise ValueError('name cannot be None')
        else:
            root_ = '' if root is None else root
            path_ = '' if path is None else path
            rel_ = rel if rel is not None else []
            tran = self.find_action(name)
            if tran is not None:
                rtn = tran
                rtn['href'] = root_ + ('' if root_.endswith('/') or not path_ else '/') + path_
                if inputs := rtn.get('inputs', None):
                    for input in inputs:
                        if optionsFromUrl := get_extended_property_value('optionsFromUrl', input):
                            optionsFromUrlPath = optionsFromUrl.get('path', '')
                            optionsFromUrl['href'] = root_ + ('' if root_.endswith('/') or not optionsFromUrlPath else '/') + optionsFromUrlPath
                rtn['rel'] = rel_
                if itemif and 'item' not in rtn['target']:
                    raise ValueError(f'Action {name} has an item_if attribute but lacks an item target')
                if itemif:
                    rtn.setdefault('hea', {})['itemIf'] = itemif
            else:
                raise ValueError(f'No action with name {name}')
        return rtn


def action(name: str,
           path: str | None = None,
           rel: Union[str, List[str]] | None = None,
           root: str | None = None,
           itemif: str | None = None) -> \
    Callable[[Callable[[Request], Coroutine[Any, Any, Response]]],
             Callable[[Request], Coroutine[Any, Any, Response]]]:
    """
    Decorator factory for appending a WeSTL action to a run-time WeSTL document
    in a HTTP request.

    An action has a name that is used to match it to a state transition in the
    design-time WeSTL document. The properties of the state transition are
    pulled into the action. It also has rel values as described in IETF RFC
    5988 (https://datatracker.ietf.org/doc/html/rfc5988), and an itemif
    expression that conditionally appends the action depending on the data in
    the WeSTL document. Finally, it has an href that is created by
    concatenating the root and path parameters. Before the root and the path
    are concatenated, a trailing slash is added to the root if not already
    present. If a root is provided, the path must be relative (not contain a
    leading slash).

    :param name: the action's name. Required. Action names should use the
    following convention, all lowercase with dashes between words:
    <project_slug>-<heaobject_classname>-<verb_describing_action>, for example,
    heaobject-registry-component-get-properties. Failure to follow this
    convention could result in collisions between your action names and any
    action names added to core HEA in the future.
    :param path: the action's path. Required. The path may contain variables in
    curly braces, using the syntax of the URI Template standard, RFC 6570,
    documented at https://datatracker.ietf.org/doc/html/rfc6570. Variables are
    matched to attributes of the HEA object being processed. They are replaced
    with their values by Representor objects while outputting links. Nested
    JSON objects may be referred to using a period syntax just like in python.
    :param root: the base URL to be prepended to the path. If None, the value
    of request.app[appproperty.HEA_COMPONENT] will be used.
    :param rel: a list of HTML rel attribute values, or the list as a
    space-delimited string.
    :param itemif: an expression string for determining whether to apply an
    action to an item in the wstl document (optional).
    :return: the decorated callable.
    """

    def wrap(f: Callable[[Request], Coroutine[Any, Any, Response]]) -> Callable[
        [Request], Coroutine[Any, Any, Response]]:
        @functools.wraps(f)
        def wrapped_f(request: Request) -> Coroutine[Any, Any, Response]:
            wstl_ = request[requestproperty.HEA_WSTL_BUILDER]
            wstl_.add_run_time_action(name, path=path, rel=rel, root=root if root is not None else request.app[appproperty.HEA_COMPONENT], itemif=itemif)
            return f(request)

        return wrapped_f

    return wrap


def add_run_time_action(request: Request, name: str, path: str | None = None,
           rel: Union[str, List[str]] | None = None, root: str | None = None,
           itemif: str | None = None):
    """
    Append an action from the design-time WeSTL document to the run-time WeSTL document.

    :param request: the HTTP request (required).
    :param name: the action's name. Required. Action names should use the following convention, all lowercase with
    dashes between words: <project_slug>-<heaobject_classname>-<verb_describing_action>, for example,
    heaobject-registry-component-get-properties. Failure to follow this convention could result in collisions
    between dyour action names and any action names added to core HEA in the future.
    :param path: the path of the action, plus any fragment and query string.
    :param rel: a list of HTML rel attribute values, or the list as a space-delimited string.
    :param root: the root of the action URL (everything except the path above).
    :param itemif: an expression string for determining whether to apply
    an action to an item in the wstl document (optional).
    """
    wstl_ = request[requestproperty.HEA_WSTL_BUILDER]
    wstl_.add_run_time_action(name, path=path, rel=rel,
                              root=root if root is not None else request.app[appproperty.HEA_COMPONENT],
                              itemif=itemif)


def builder_factory(package: Optional[str] = None, resource='wstl/all.json', href: Optional[Union[str, URL]] = None,
                    loads=json.loads) -> Callable[[], RuntimeWeSTLDocumentBuilder]:
    """
    Returns a zero-argument callable that will load a design-time WeSTL document and get a RuntimeWeSTLDocumentBuilder
    instance. It caches the design-time WeSTL document.

    :param package: the name of the package that the provided resource is in, in standard module format (foo.bar).
    Must be an absolute package name. If resource is set to None, then this argument will be ignored and may be omitted.
    :param resource: a relative path to a design-time WeSTL document. Expects / as the path separator. The parent
    directory (..) is not allowed, nor is a rooted name (starting with /). The default value is 'wstl/all.json'. If
    set to None, the DEFAULT_DESIGN_TIME_WSTL design-time WeSTL document will be used.
    :param href: The URL associated with the resource
    :param loads: any callable that accepts str and returns dict with parsed JSON (json.loads() by default).
    :return: a zero-argument callable for creating a WSTLDocument object. The same document instance will be
    returned every time.
    :raises FileNotFoundException: no such resource exists.
    :raises ValueError: if a non-existent package is specified, or the provided package name does not support the
    get_data API.
    """

    if resource is not None and package is not None:
        data_ = pkgutil.get_data(package, resource)
        if not data_:
            raise ValueError('No package named ' + package +
                             ', or the package uses a loader that does not support get_data')
        data = loads(data_)
        validate(data)
    else:
        data = DEFAULT_DESIGN_TIME_WSTL

    def builder_factory_() -> RuntimeWeSTLDocumentBuilder:
        """
        Reads a JSON document in design-time Web Service Transition Language (WeSTL) format from a file within a package.
        The specification of the WeSTL format is available from https://rwcbook.github.io/wstl-spec/.

        :return: a RuntimeWeSTLDocumentBuilder instance for creating a run-time WeSTL document.
        """
        return RuntimeWeSTLDocumentBuilder(data, href)

    return builder_factory_


def builder(package: Optional[str] = None, resource='wstl/all.json', href: Optional[Union[str, URL]] = None,
            loads=json.loads) -> RuntimeWeSTLDocumentBuilder:
    """
    Returns a RuntimeWeSTLDocumentBuilder instance.

    :param package: the name of a package, in standard module format (foo.bar).
    :param resource: a relative path to a design-time WeSTL ocument. Expects / as the path separator. The parent
    directory (..) is not allowed, nor is a rooted name (starting with /). The default value is 'wstl/all.json'. If
    set to None, the DEFAULT_DESIGN_TIME_WSTL design-time WeSTL document will be used.
    :param href: the URL associated with the resource.
    :param loads: any callable that accepts str and returns dict with parsed JSON (json.loads() by default).
    :return: a zero-argument callable for creating a WSTLDocument object. The same document instance will be
    returned every time.
    :raises FileNotFoundException: no such resource exists.
    :raises ValueError: if a non-existent package is specified, or the provided package name does not support the
    get_data API.
    """
    return builder_factory(package, resource=resource, href=href, loads=loads)()


_merger = jsonmerge.Merger(jsonschema.WSTL_SCHEMA)


def merge(base: Dict[str, Any], head: Dict[str, Any]):
    return _merger.merge(base, head)


def get_extended_property_value(key: str, item: dict[str, Any]) -> Optional[Any]:
    return item.get(key, item['hea'].get(key, None) if 'hea' in item else None)


def has_extended_property_value(key: str, item: dict[str, Any]) -> bool:
    return get_extended_property_value(key, item) is not None


def get_section(value: dict[str, Any]) -> Optional[str]:
    return get_extended_property_value('section', value)


def has_section(value: dict[str, Any]) -> bool:
    return get_section(value) is not None


def validate(wstl_doc):
    """
    Validates a WeSTL document.

    :param wstl_doc: a WeSTL document as a dictionary.
    :raises ValueError: if the provided document fails validation.
    """
    try:
        jsonschemavalidator.WSTL_SCHEMA_VALIDATOR.validate(wstl_doc)
        check_duplicates(obj['name'] for obj in wstl_doc['wstl'].get('actions', []))
    except DuplicateError as e:
        raise ValueError(f'Invalid WeSTL document: duplicate name {e.duplicate_item}') from e
    except jsonschemavalidator.ValidationError as e:
        raise ValueError(f'Invalid WeSTL document: {e}') from e
