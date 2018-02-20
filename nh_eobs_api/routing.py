# Part of Open eObs. See LICENSE file for full copyright and licensing details.
import json

import jinja2
import re
from openerp.tools import config


class Route(object):
    """Class storing all the data for a single route."""
    def __init__(self, name, url, request_type='http',
                 auth='user', methods=None, response_type='json',
                 headers=None, cors=None, url_prefix=None):
        self.name = name
        self.url = url
        self.request_type = request_type
        self.auth = auth
        self.methods = methods if methods else ['GET']
        # TODO: get this from the URL parameter?
        # (ex: adding ?_format=json to the URL)
        self.response_type = response_type
        self.headers = headers if headers else {}
        self.cors = cors  # TODO: is this really needed?
        self.url_prefix = url_prefix

        self.args = self._get_args(self.url)
        self.url_components = self._get_url_components(self.url)

    def _get_args(self, url):
        """Fetch named arguments for a URL from that URL.

        Named arguments are the ones written as: <argument_name>
        Example URL: api/v1/patients/<patient_id>/observation/<observation_id>/

        :param url: A string with a "Werkzeug style" URL
        :return: List comma separated strings or False (no arguments fetched)
        """
        args_fetched = re.findall(r'\/<[a-zA-Z]+(?:(?:_|-)[a-zA-Z]+)*>\/??',
                                  url)
        trim_regex = re.compile(r'>\/?')
        return [trim_regex.sub('', arg[2:]) for arg in args_fetched] or False

    def _split_url(self, url, split_on='/'):
        """Split a URL in pieces, according to a specific separator.

        Also, remove empty pieces, usually generated by two consecutive
        occurrences of the separator in the URL.
        This is supposed to be an utility method, only used internally by
        other higher-level methods.

        :param url: String (not necessarily a well-formed URL)
        :param split_on: String used as separator to split the URL
        :return: List of comma separated strings from split URL
        :raise ValueError: If the 'url' argument passed is not a string
        """
        if not isinstance(url, basestring):
            raise ValueError('The URL passed as argument is not a string.')
        split_url = url.split(split_on)
        url_pieces_list = [p for p in split_url if not p == '']
        return url_pieces_list

    def _get_url_components(self, url):
        """Divide a URL into pieces and store them into a list of dictionaries,
        alongside some metadata.
        Example URL: api/v1/patients/<patient_id>/observation/<observation_id>/

        :param url: String containing a "Werkzeug style" URL
        :return: List of dictionaries, each containing one URL component,
        alongside metadata describing it
        :raise ValueError: If, when parsing a piece of the URL passed as
        argument, that piece results not to be a string
        """
        decomposed_url = []
        url_pieces_list = self._split_url(url)
        for piece in url_pieces_list:
            if not isinstance(piece, basestring):
                error_string = 'Parsed {} as piece of URL, ' \
                               'but it is not a string as expected.'
                raise ValueError(error_string.format(piece))
            is_func = False
            if piece.startswith('<') and piece.endswith('>'):
                is_func = True
            # store just the actual name of the URL piece
            decomposed_url.append(
                {
                    'type': 'func' if is_func else 'string',
                    'name': piece.lstrip('<').rstrip('>')
                }
            )
        return decomposed_url


class RouteManager(object):
    """Class storing and managing Route objects."""
    def __init__(self, server_protocol='https',
                 server_address='localhost', server_port=None, url_prefix='/'):
        self.SERVER_PROTOCOL = server_protocol
        self.SERVER_ADDRESS = server_address
        if not server_port:
            self.SERVER_PORT = '{}'.format(config['xmlrpc_port'])
        self.URL_PREFIX = url_prefix
        self.BASE_URL = '{0}://{1}:{2}'.format(self.SERVER_PROTOCOL,
                                               self.SERVER_ADDRESS,
                                               self.SERVER_PORT)
        self.BASE_URL_WITH_PREFIX = self.BASE_URL + self.URL_PREFIX

        self.ROUTES = {}

    def add_route(self, route):
        """Add a new route to the dictionary ROUTES.

        :param route: A Route object
        :raise KeyError: If 'name' of the Route object to be added is the
        same of another Route object already in the dictionary
        """
        if route.name in self.ROUTES:
            raise KeyError(str(route.name))
        else:
            self.ROUTES[route.name] = route

    def remove_route(self, route_name):  # TODO: is this really needed?
        """Remove an existing route from the dictionary ROUTES.

        :param route_name: A string matching the 'name' key of the route
        to be removed
        """
        pass

    def get_route(self, route_name):
        """Return an existing route from the dictionary ROUTES.

        :param route_name: A string matching the 'name' key of the route
        to be returned
        :return: A Route object or None (if a Route object with that name
        is not found)
        """
        # TODO: Need to sort out args
        return self.ROUTES.get(route_name, None)

    # TODO: name this "explode_route"?
    def expose_route(self, route_name, url_prefix=None):
        """Expose all the properties of an existing route,
        formatted as a dictionary.

        :param route_name: A string matching the 'name' key of the
        route to be returned
        :param url_prefix: A string add as a prefix when returning the
        'url' property of the Route object
        :return: A dictionary with all the properties inside the Route
        object looked for
        :raise: KeyError (if no Route object matching the 'route_name'
        parameter is found)
        """
        route = self.ROUTES[route_name]
        route_prefix = url_prefix or route.url_prefix or self.URL_PREFIX
        if route:
            route_string = route.url
            if route_prefix:
                route_string = str(route_prefix) + route.url
            route_dict = {
                'route': route_string,
                'auth': route.auth,
                'methods': route.methods,
                'headers': route.headers,
                'cors': route.cors
            }
            return route_dict

    # TODO: ALTERNATIVE VERSION ! Is this useful ???
    def expose_route2(self, route_name, url_prefix=None,
                      additional_parameters=None):
        """Expose all the properties of an existing route,
        formatted as a dictionary.

        :param route_name: A string matching the 'name' key of
        the route to be returned
        :param url_prefix: A string add as a prefix when returning the
        'url' property of the Route object
        :param additional_parameters: A dictionary with additional
        key-value arguments to be exposed
        :return: A dictionary with all the properties inside the Route
        object looked for
        :raise: KeyError (if no Route object matching the 'route_name'
        parameter is found)
        """
        route = self.ROUTES[route_name]
        route_prefix = url_prefix or route.url_prefix or self.URL_PREFIX
        if route:
            route_string = route.url
            if route_prefix:
                route_string = str(route_prefix) + route.url
            route_dict = {  # TODO: exclude 'falsy' parameters ?
                'route': route_string,
                'auth': route.auth,
                'methods': route.methods,
                'headers': route.headers,
                'cors': route.cors
            }
            if additional_parameters and isinstance(additional_parameters,
                                                    dict):
                route_dict.update(additional_parameters)
            return route_dict

    def get_javascript_routes(self, template_name, template_path,
                              route_list=None, additional_context=None):
        """Render a template file using Jinja.

        :param template_name: The name of the template file
        :param template_path: The absolute path of the template file
        (omitting the name of the template file)
        :param route_list: A list of Route objects, used to render the
        template (OPTIONAL)
        :param additional_context: A dictionary that will extend the
        context used to render the template (OPTIONAL)
        :return: The template file rendered as a string (with a default
        template variable called "routes" that stores a list of Route objects)
        """
        # TODO: use only ONE argument for the template's filepath (?)
        loader = jinja2.FileSystemLoader(template_path)
        env = jinja2.Environment(loader=loader)

        template = env.get_template(template_name)

        # list all the Route objects or only some of them
        routes = route_list or self.ROUTES.values()
        default_context = {'routes': routes}

        if additional_context is None:
            return template.render(default_context)
        else:
            default_context.update(additional_context)
            return template.render(default_context)


class ResponseJSON(object):
    """Class managing a JSON-encoded response (for an API request)."""
    STATUS_SUCCESS = 'success'
    STATUS_FAIL = 'fail'
    STATUS_ERROR = 'error'
    # default Content-Type header for this class' responses
    HEADER_CONTENT_TYPE = {'Content-Type': 'application/json'}

    @staticmethod
    def get_json_data(status=STATUS_ERROR, title=False, description=False,
                      data=False):
        """Build a dictionary containing all the arguments' data, and
        encode it as JSON.

        :param status: A string with the status of the response
        (please, use the STATUS_* constants defined in this class!)
        :param title: A string with summary information about the response
        (in case of error: the name of the Exception)
        :param description: A string with complete information about the
        response (in case of error: the complete error message)
        :param data: A dictionary with the actual payload of the JSON response
        :return: A JSON-encoded dictionary containing all the data from
        the arguments passed to this function
        """
        json_response = {
            'status': status,
            'title': title,
            'description': description,
            'data': data
        }
        return json.dumps(json_response)
