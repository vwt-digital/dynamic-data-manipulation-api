from flask import current_app, jsonify, make_response


def check_database_configuration():
    if current_app.db_client is None or current_app.db_table_name is None or current_app.db_keys is None:
        return make_response(jsonify("Database information insufficient"), 500)


def generic_get_multiple():  # noqa: E501
    """Returns a array of entities

    :rtype: array
    """
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    return current_app.db_client.get_multiple(kind=current_app.db_table_name, keys=current_app.db_keys)


def generic_get_single(unique_id):  # noqa: E501
    """Returns an entity

    :param unique_id: A unique identifier
    :type unique_id: str

    :rtype: dict
    """
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    return current_app.db_client.get_single(
        unique_id=unique_id, kind=current_app.db_table_name, keys=current_app.db_keys)


def generic_post_single(body):  # noqa: E501
    """Creates an entity

    :param body:
    :type body: dict

    :rtype: dict
    """
    db_existence = check_database_configuration()
    if db_existence:
        return db_existence

    return current_app.db_client.post_single(body=body, kind=current_app.db_table_name, keys=current_app.db_keys)


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

    return current_app.db_client.put_single(
        unique_id=unique_id, body=body, kind=current_app.db_table_name, keys=current_app.db_keys)


def generic_get_multiple2():  # noqa: E501
    generic_get_multiple()


def generic_get_multiple3():  # noqa: E501
    generic_get_multiple()


def generic_get_single2(unique_id):  # noqa: E501
    generic_get_single(unique_id)


def generic_get_single3(unique_id):  # noqa: E501
    generic_get_single(unique_id)


def generic_post_single2(body):  # noqa: E501
    generic_post_single(body)


def generic_post_single3(body):  # noqa: E501
    generic_post_single(body)


def generic_put_single2(unique_id, body):  # noqa: E501
    generic_put_single(unique_id, body)


def generic_put_single3(unique_id, body):  # noqa: E501
    generic_put_single(unique_id, body)
