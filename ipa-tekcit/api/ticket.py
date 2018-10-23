"""Module with End Points to fetch data related to tickets."""
# System imports
from datetime import datetime

# Third-party imports
from flask import (Blueprint, Response)
import json

# Local source tree imports
from utils.ticket_api import (DBConnect, FormatJson, DBQueries)


# Flask Blueprints
api = Blueprint('tickets_api', __name__)

ticket_default_fields = ['pedido_id', 'status', 'date_created', 'asn',
                         'assunto', 'form_source']

db_queries = DBQueries(ticket_default_fields)

# Handle datetime type from SQL Query
json.JSONEncoder.default = lambda self, obj: (obj.strftime("%c") if
                                              isinstance(obj, datetime)
                                              else None)

default_endpoint_root = '/api'


def query_response(fetch_query_tuple):
    """ This routine implements a repetitive code used to response an HTTP Get

    Receives a tuple, where each element is a result from a DB Query. Builds
    a dictionary (res_dict) and return it with the proper indentation and
    encoding. The endpoints can return it directly to the requester.

    Args:
        fetch_query_tuple: A tuple with all data fetched from database

    Returns: An HTTP response with a JSON with the proper indentation and
    decoding

    """
    res_dict = {}
    for ticket in fetch_query_tuple:
        res_dict[ticket['pedido_id']] = ticket

    response = Response(json.dumps(
        res_dict, ensure_ascii=False, indent=4).encode('utf8'),
                    mimetype='application/json;charset=utf-8')

    return response


@api.route(default_endpoint_root + '/tickets/', methods=['GET'])
def get_all_tickets():
    """ Returns all tickets (closed and open)

    Returns: json with the returned query

    """
    db_connect = DBConnect().mysql_connect(mysql_user='user5100',
                                           mysql_password='ePPkLlao')
    db_connect.execute(db_queries.query_all_tickets())
    db_results = db_connect.fetchall()
    db_connect.close()

    return query_response(db_results)


@api.route(default_endpoint_root + '/tickets/open/', methods=['GET'])
def get_tickets_open():
    """ Returns all open tickets

    Returns: json with the returned query

    """
    db_connect = DBConnect().mysql_connect(mysql_user='user5100',
                                           mysql_password='ePPkLlao')
    db_connect.execute(db_queries.query_open_ticket())

    db_results = db_connect.fetchall()
    db_connect.close()
    return query_response(db_results)


@api.route(default_endpoint_root + '/tickets/closed/', methods=['GET'])
def get_tickets_closed():
    """ Returns all closed tickets

    Returns: json with the returned query

    """
    db_connect = DBConnect().mysql_connect(mysql_user='user5100',
                                           mysql_password='ePPkLlao')
    db_connect.execute(db_queries.query_close_ticket())
    db_results = db_connect.fetchall()
    db_connect.close()
    return query_response(db_results)


@api.route(default_endpoint_root + '/tickets/<ticket_id>', methods=['GET'])
def get_ticket_detail(ticket_id):
    """ Returns detailed information regarding a specific ticket

    Returns: json with the returned query

    """

    # Get the IX from the ticket
    db_connect = DBConnect().mysql_connect(mysql_user='user5100',
                                           mysql_password='ePPkLlao')
    db_connect.execute(db_queries.query_ix_codigo(ticket_id))
    ix_code = db_connect.fetchall()

    db_connect.execute(db_queries.query_ticket_detail(ticket_id))

    json_to_send = FormatJson.format_ticket_detail(
        db_connect.fetchall()[-1],
        ticket_id,
        ix_code[0]['codigo'])

    json.dumps(json_to_send)
    db_connect.close()
    return Response(json_to_send, mimetype='application/json;charset=utf-8'),\
           200
