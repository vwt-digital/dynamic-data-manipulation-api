from flask import current_app, jsonify, make_response


def check_database_configuration():
    if current_app.db_client is None or current_app.db_table_name is None or \
            current_app.db_table_id is None or current_app.db_keys is None:
        return make_response(jsonify("Database information insufficient"), 500)


def check_identifier(kwargs):
    if current_app.request_id is None or current_app.request_id not in kwargs:
        return make_response(jsonify("Identifier name not found"), 500)


def generic_get_multiple():  # noqa: E501
    """Returns a array of entities

    :rtype: array
    """
    # Check for Database configuration
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    db_response = current_app.db_client.get_multiple(kind=current_app.db_table_name, keys=current_app.db_keys)

    if db_response:
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
    db_response = current_app.db_client.get_single(
        id=kwargs.get(current_app.request_id), kind=current_app.db_table_name, keys=current_app.db_keys)

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
    db_response = current_app.db_client.post_single(
        body=kwargs.get('body', {}), kind=current_app.db_table_name, keys=current_app.db_keys)

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
    if db_existence or current_app.entity_id not in kwargs:
        return db_existence

    # Check if identifier exists and in kwargs
    id_existence = check_identifier(kwargs)
    if id_existence:
        return id_existence

    # Call DB func
    db_response = current_app.db_client.put_single(
        id=kwargs.get(current_app.request_id), body=kwargs.get('body', {}), kind=current_app.db_table_name,
        keys=current_app.db_keys)

    if db_response:
        return make_response(jsonify(db_response), 201)

    return make_response('Not found', 404)


def generic_get_multiple2():  # noqa: E501
    generic_get_multiple()


def generic_get_multiple3():  # noqa: E501
    generic_get_multiple()


def generic_get_single2(**kwargs):  # noqa: E501
    generic_get_single(**kwargs)


def generic_get_single3(**kwargs):  # noqa: E501
    generic_get_single(**kwargs)


def generic_post_single2(**kwargs):  # noqa: E501
    generic_post_single(**kwargs)


def generic_post_single3(**kwargs):  # noqa: E501
    generic_post_single(**kwargs)


def generic_put_single2(**kwargs):  # noqa: E501
    generic_put_single(**kwargs)


def generic_put_single3(**kwargs):  # noqa: E501
    generic_put_single(**kwargs)
