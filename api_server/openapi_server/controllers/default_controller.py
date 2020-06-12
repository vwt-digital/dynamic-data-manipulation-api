from flask import g, jsonify, make_response


def check_database_configuration():
    if 'db_client' not in g or 'db_kind' not in g or 'db_keys' not in g:
        return make_response(jsonify("Database information insufficient"), 400)


def generic_get_columns():  # noqa: E501
    """Returns column definitions

    :rtype: array
    """
    return jsonify(g.db_keys)


def generic_get_multiple():  # noqa: E501
    """Returns a array of entities

    :rtype: array
    """
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    return g.db_client.get_multiple(kind=g.db_kind, keys=g.db_keys)


def generic_get_single(unique_id):  # noqa: E501
    """Returns an entity

    :param unique_id: A unique identifier
    :type unique_id: str

    :rtype: dict
    """
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    return g.db_client.get_single(unique_id=unique_id, kind=g.db_kind, keys=g.db_keys)


def generic_post_single(body):  # noqa: E501
    """Creates an entity

    :param body:
    :type body: dict

    :rtype: dict
    """
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    return g.db_client.post_single(body=body, kind=g.db_kind, keys=g.db_keys)


def generic_put_single(unique_id, body):  # noqa: E501
    """Updates an entity

    :param unique_id: A unique identifier
    :type unique_id: str
    :param body:
    :type body: dict

    :rtype: dict
    """
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    return g.db_client.put_single(unique_id=unique_id, body=body, kind=g.db_kind, keys=g.db_keys)
