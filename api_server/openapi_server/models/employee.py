# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class Employee(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, firstname=None, lastname=None):  # noqa: E501
        """Employee - a model defined in OpenAPI

        :param id: The id of this Employee.  # noqa: E501
        :type id: str
        :param firstname: The firstname of this Employee.  # noqa: E501
        :type firstname: str
        :param lastname: The lastname of this Employee.  # noqa: E501
        :type lastname: str
        """
        self.openapi_types = {
            'id': str,
            'firstname': str,
            'lastname': str
        }

        self.attribute_map = {
            'id': 'id',
            'firstname': 'firstname',
            'lastname': 'lastname'
        }

        self._id = id
        self._firstname = firstname
        self._lastname = lastname

    @classmethod
    def from_dict(cls, dikt) -> 'Employee':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Employee of this Employee.  # noqa: E501
        :rtype: Employee
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this Employee.


        :return: The id of this Employee.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Employee.


        :param id: The id of this Employee.
        :type id: str
        """

        self._id = id

    @property
    def firstname(self):
        """Gets the firstname of this Employee.


        :return: The firstname of this Employee.
        :rtype: str
        """
        return self._firstname

    @firstname.setter
    def firstname(self, firstname):
        """Sets the firstname of this Employee.


        :param firstname: The firstname of this Employee.
        :type firstname: str
        """
        if firstname is not None and len(firstname) > 100:
            raise ValueError("Invalid value for `firstname`, length must be less than or equal to `100`")  # noqa: E501

        self._firstname = firstname

    @property
    def lastname(self):
        """Gets the lastname of this Employee.


        :return: The lastname of this Employee.
        :rtype: str
        """
        return self._lastname

    @lastname.setter
    def lastname(self, lastname):
        """Sets the lastname of this Employee.


        :param lastname: The lastname of this Employee.
        :type lastname: str
        """
        if lastname is not None and len(lastname) > 100:
            raise ValueError("Invalid value for `lastname`, length must be less than or equal to `100`")  # noqa: E501

        self._lastname = lastname
