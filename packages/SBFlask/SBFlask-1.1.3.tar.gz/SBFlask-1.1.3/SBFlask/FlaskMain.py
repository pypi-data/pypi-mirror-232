import logging

from flask import Flask, redirect, url_for, request
from flask_cors import CORS, cross_origin
import json
from SBKodiak.KodiakControl import KodiakControlClass, KodiakWrapper
from SBKodiak.KodiakMDNsLocate import find_kodiak_ip_addresses
from tests.frigged_server_responses import *

app = Flask(__name__)
cors = CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

stop_kodiak = True

# Kodiak Controller object
KodiakController = KodiakControlClass()

# Fake the responses
frigg_responses = True

# @app.route(f"/kodiak/login", methods=['POST'])
# def kodiak_endpoint_login():
#     global stop_kodiak
#     """
#     Login endpoint.
#     This needs to create a session and login to the specified kodiak.
#
#     It should query the database to check if the kodiak was logged into previously and attempt to use the
#     session key renewal.
#
#     Once the login has been confirmed, the data should be written back into the database.
#
#     :return: JSON - With an appropriate success / error message.
#     """
#     global KodiakController
#
#     if request.method == 'POST':
#         # Get the json data sent from JS
#         data = request.get_json()
#         response = {}
#
#         # check all the necessary information is here to login to the kodiak system
#         if all(keys in data.keys() for keys in ['ipaddress', 'username', 'password', 'key']):
#
#             # Create the KodiakWrapper to store these data values in
#             kw = KodiakWrapper(kodiak_ip_address=data['ipaddress'], username=data['username'],
#                                password=data['password'], private_key=data['key'])
#
#             # Login to the kodiak and save the data to the database
#             if not KodiakController.login(kw):
#                 response["login error!"] = "Problem loging into the Kodiak, are these details correct?"
#
#             if stop_kodiak:
#                 KodiakController.stop(kw)
#
#         else:
#             response["Key error!"] = "Missing one of the following keys : 'ipaddress', 'username', 'password', 'key'"
#
#         return json.dumps(response, indent=4)


@app.route(f"/kodiak/port/discover", methods=['POST'])
def kodiak_endpoint_discover():
    """
    Discover endpoint.

    The function will first try to get the login credentials.

    This endpoint will start the discovery of the Kodiak Module against the SB ports
    After posting to the endpoint, the client should then send a 'get' request to the /kodiak/port to discover the port.

    :return: JSON - With an appropriate success / error message.
    """
    global KodiakController
    global frigg_responses

    response = {}

    if frigg_responses:
        response['Success'] = 'Started auto discovery'
        return json.dumps(response, indent=4)

    if request.method == 'POST':
        data = request.get_json()
        if all(keys in data.keys() for keys in ['ipaddress']):

            # Get the items from the database
            query_response = KodiakController.db.get_kodiak_db(data['ipaddress'])

            # if the response is missing then add an appropriate error message
            if not query_response:
                response['Error'] = "Could not locate this IP address, is this definitely connected?"

            else:
                # Create a wrapper and attempt to start the auto locate
                kw = KodiakWrapper(query_response[0], query_response[1], query_response[2], query_response[3])
                started = KodiakController.start_auto_locate_port(kw)

                # If there's an error starting the discovery, add the error message
                if not started:
                    response['Error'] = 'Failed to start Kodiak capture!'
                else:
                    response['Success'] = 'Started auto discovery'
        else:
            response["Error"] = "Missing key : 'ipaddress'"

        return json.dumps(response, indent=4)


@app.route(f"/kodiak/locate", methods=['GET'])
def kodiak_endpoint_locate():
    """
    Get endpoint for scanning MDNs for Kodiak Ipaddresses.

    This function will attempt to get the port the Kodiak is attached to

    :return: JSON - With an appropriate success / error message.
    """
    global KodiakController
    global frigg_responses
    response = {}

    if frigg_responses:
        response['Success'] = str(['192.168.1.2', '192.168.1.3'])
        return json.dumps(response, indent=4)

    if request.method == 'GET':
        response = {}

        try:
            # call to MDNS scan function which will return a list of discovered IPAddresses
            ip_address_list = find_kodiak_ip_addresses()
            logging.debug(f"List of found ip's : {ip_address_list}")
            response['Success'] = str(ip_address_list)
        except Exception as err:
            response['Error'] = "Error whilst starting MDNS discovery!"

        return json.dumps(response, indent=4)


@app.route(f"/kodiak/port", methods=['GET'])
def kodiak_endpoint_port():
    """
    Get port endpoint.

    This function will attempt to get the port the Kodiak is attached to

    :return: JSON - With an appropriate success / error message.
    """
    global KodiakController
    global frigg_responses
    response = {}

    if frigg_responses:
        response['Success'] = '02'
        return json.dumps(response, indent=4)

    if request.method == 'GET':
        response = {}

        if request.args:
            # {'{"ipaddress":"192.168.1.247"}': ''}
            x = str(request.args)
            x = x.split("\"")
            ipaddress = x[3]

            # Get the items from the database
            query_response = KodiakController.db.get_kodiak_db(ipaddress)

            # if the response is missing then add an appropriate error message
            if not query_response:
                response['Error'] = "Missing Kodiak credentials, have you logged in?"

            else:
                # Create a wrapper and attempt to start the auto locate
                port_response = query_response[-2]

                if port_response:
                    response['Success'] = port_response

                else:
                    # If there wasn't a return from the locate_kodiak_port function then no port was found
                    response['Error'] = "Could not find port containing Kodiak Module!"
        else:
            response['Error'] = "Missing target Kodiak's IPAddress"

        return json.dumps(response, indent=4)


@app.route(f"/kodiak/status", methods=['GET'])
def kodiak_endpoint_get_status():
    """
    Get kodiak status for a given IP address.

    This function will attempt to get the status of the kodiak from the supplied IP

    :return: JSON - With an appropriate success / error message.
    """
    global KodiakController
    global frigg_responses
    response = {}

    if frigg_responses:
        response['Success'] = status_response_good
        return json.dumps(response, indent=4)

    if request.method == 'GET':
        response = {}

        if request.args:

            try:
                # {'{"ipaddress":"192.168.1.247"}': ''}
                x = str(request.args)
                x = x.split("\"")
                ipaddress = x[3]

                # Frigging the initial response
                response['Success'] = status_response_good

            except Exception as err:
                response['Error'] = "Badly formed IP address in /status get packet"

        else:
            response['Error'] = "Missing target Kodiak's IPAddress"

        return json.dumps(response, indent=4)

# @app.route(f"/server/shutdown")
# def server_endpoint_shutdown():
#     """
#     Shutdown server endpoint
#
#     Will shut down this running flask server.
#
#     :return: JSON - stating server is about to be shutdown
#     """
#
#     def shutdown_server():
#         app.
#
#     try:
#         response = {'Success': 'Shutting down server'}
#         return json.dumps(response, indent=4)
#     finally:
#         shutdown_server()


# @app.route(f"/kodiak/start", methods=['POST'])
# def kodiak_endpoint_start():
#     global KodiakController
#     if request.method == 'POST':
#         data = request.get_json()
#         response = {}
#         if 'error' in KodiakController.start():
#             response['Error'] = 'Error starting kodiak stream'
#         else:
#             response['Success'] = 'Successfully started kodiak stream'
#
#         return json.dumps(response, indent=4)
#
#
# @app.route(f"/kodiak/stop", methods=['POST'])
# def kodiak_endpoint_stop():
#     global KodiakController
#     if request.method == 'POST':
#         response = {}
#         if 'error' in KodiakController.stop():
#             response['Error'] = 'Error starting kodiak stream'
#         else:
#             response['Success'] = 'Successfully started kodiak stream'
#
#         return json.dumps(response, indent=4)


def create_app():
    app.run(port=4201, host='0.0.0.0')


if __name__ == "__main__":
    create_app()
