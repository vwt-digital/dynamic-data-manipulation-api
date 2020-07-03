import re

from flask import request, current_app, jsonify, make_response


def check_database_configuration():
    if current_app.db_client is None or current_app.db_table_name is None or \
            current_app.db_table_id is None or current_app.db_keys is None:
        return make_response(jsonify("Database information insufficient"), 500)


def check_identifier(kwargs):
    if current_app.request_id is None or current_app.request_id not in kwargs:
        return make_response(jsonify("Identifier name not found"), 500)


def generic_get_multiple():  # noqa: E501
    """Returns a array of entities

    :param kwargs: Keyword argument list
    :type kwargs: dict

    :rtype: array
    """

    # Check for Database configuration
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    try:
        db_response = current_app.db_client.get_multiple(kind=current_app.db_table_name, keys=current_app.db_keys)
    except ValueError as e:
        return make_response(jsonify(str(e)), 400)

    if db_response:
        return db_response

    return make_response(jsonify([]), 204)


def generic_get_multiple_page(**kwargs):  # noqa: E501
    """Returns a dict containing entities and pagination information

    :param kwargs: Keyword argument list
    :type kwargs: dict

    :rtype: array
    """

    # Check for Database configuration
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    page_cursor = kwargs.get('page_cursor', None)
    page_size = kwargs.get('page_size', 50)
    page_action = kwargs.get('page_action', 'next')

    try:
        db_response = current_app.db_client.get_multiple_page(
            kind=current_app.db_table_name, keys=current_app.db_keys, page_cursor=page_cursor, page_size=page_size,
            page_action=page_action)
    except ValueError as e:
        return make_response(jsonify(str(e)), 400)

    if db_response:
        if db_response.get('next_page'):
            url_rule = re.sub(r'<.*?>', '', str(request.url_rule)).strip('/')

            if not url_rule.endswith("/pages"):
                url_rule = f"{url_rule}/pages"

            db_response['next_page'] = f"{request.host_url}{url_rule}/{db_response['next_page']}" \
                                       f"?page_size={page_size}&page_action=next"

        return db_response

    return make_response(jsonify([]), 204)


def generic_get_single(**kwargs):  # noqa: E501
    """Returns an entity

    :param kwargs: Keyword argument list
    :type kwargs: dict

    :rtype: dict
    """

    # Check for Database configuration
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    # Check if identifier exists and in kwargs
    id_existence = check_identifier(kwargs)
    if id_existence:
        return id_existence

    # Call DB func
    try:
        db_response = current_app.db_client.get_single(
            id=kwargs.get(current_app.request_id), kind=current_app.db_table_name, keys=current_app.db_keys)
    except ValueError as e:
        return make_response(jsonify(str(e)), 400)

    if db_response:
        return db_response

    return make_response('Not found', 404)


def generic_post_single(**kwargs):  # noqa: E501
    """Creates an entity

    :param kwargs: Keyword argument list
    :type kwargs: dict

    :rtype: dict
    """

    # Check for Database configuration
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    # Call DB func
    try:
        db_response = current_app.db_client.post_single(
            body=kwargs.get('body', {}), kind=current_app.db_table_name, keys=current_app.db_keys)
    except ValueError as e:
        return make_response(jsonify(str(e)), 400)

    if db_response:
        return make_response(jsonify(db_response), 201)

    return make_response('Something went wrong', 400)


def generic_put_single(**kwargs):  # noqa: E501
    """Updates an entity

    :param kwargs: Keyword argument list
    :type kwargs: dict

    :rtype: dict
    """

    # Check for Database configuration
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    # Check if identifier exists and in kwargs
    id_existence = check_identifier(kwargs)
    if id_existence:
        return id_existence

    # Call DB func
    try:
        db_response = current_app.db_client.put_single(
            id=kwargs.get(current_app.request_id), body=kwargs.get('body', {}), kind=current_app.db_table_name,
            keys=current_app.db_keys)
    except ValueError as e:
        return make_response(jsonify(str(e)), 400)

    if db_response:
        return make_response(jsonify(db_response), 201)

    return make_response('Not found', 404)


def generic_get_multiple2():  # noqa: E501
    return generic_get_multiple()


def generic_get_multiple3():  # noqa: E501
    return generic_get_multiple()


def generic_get_multiple_page2(**kwargs):  # noqa: E501
    return generic_get_multiple_page(**kwargs)


def generic_get_multiple_page3(**kwargs):  # noqa: E501
    return generic_get_multiple_page(**kwargs)


def generic_get_single2(**kwargs):  # noqa: E501
    return generic_get_single(**kwargs)


def generic_get_single3(**kwargs):  # noqa: E501
    return generic_get_single(**kwargs)


def generic_post_single2(**kwargs):  # noqa: E501
    return generic_post_single(**kwargs)


def generic_post_single3(**kwargs):  # noqa: E501
    return generic_post_single(**kwargs)


def generic_put_single2(**kwargs):  # noqa: E501
    return generic_put_single(**kwargs)


def generic_put_single3(**kwargs):  # noqa: E501
    return generic_put_single(**kwargs)
