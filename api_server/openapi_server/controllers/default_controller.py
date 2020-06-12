from flask import g, jsonify, make_response


def generic_get_columns():  # noqa: E501
    """generic_get_columns

    Returns column definitions # noqa: E501

    """
    return jsonify([
        {
            'title': 'id',
            'type': 'string'
        }, {
            'title': 'firstname',
            'type': 'string'
        }, {
            'title': 'lastname',
            'type': 'string'
        }
    ])


def generic_get_multiple():  # noqa: E501
    """generic_get_multiple

    Returns a list of entities based on a kind # noqa: E501

    """
    if not g.db_name:
        return make_response(jsonify("No database information available"), 400)

    return jsonify([
        {
            "id": "a0e7fd7e-7134-46da-b6be-f152cff23da5",
            "firstname": "Izzy",
            "lastname": "Van isteren"
        }, {
            "id": "a0e7fd7e-7134-46da-b6be-f152cff23da5",
            "firstname": "Peter",
            "lastname": "Celie"
        }
    ])


def generic_get_single(unique_id):  # noqa: E501
    """generic_get_single

    Returns an entity based on a kind # noqa: E501

    """
    if not g.db_name:
        return make_response(jsonify("No database information available"), 400)

    return jsonify({
        "id": "a0e7fd7e-7134-46da-b6be-f152cff23da5",
        "firstname": "Izzy",
        "lastname": "Van isteren"
    })


def generic_post_single():  # noqa: E501
    """generic_post_single

    Creates an entity based on a kind  # noqa: E501

    """
    if not g.db_name:
        return make_response(jsonify("No database information available"), 400)

    return jsonify({
        "id": "a0e7fd7e-7134-46da-b6be-f152cff23da5",
        "firstname": "Izzy",
        "lastname": "Van isteren"
    })


def generic_put_single(unique_id):  # noqa: E501
    """generic_put_single

    Updates an entity based on a kind  # noqa: E501

    """
    if not g.db_name:
        return make_response(jsonify("No database information available"), 400)

    return jsonify({
        "id": "a0e7fd7e-7134-46da-b6be-f152cff23da5",
        "firstname": "Izzy",
        "lastname": "Van isteren"
    })
