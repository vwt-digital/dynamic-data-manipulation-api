# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi_server.models.employee import Employee  # noqa: E501
from openapi_server.models.employee_to_add import EmployeeToAdd  # noqa: E501
from openapi_server.models.employees import Employees  # noqa: E501
from openapi_server.models.response import Response  # noqa: E501
from openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_generic_get_multiple(self):
        """Test case for generic_get_multiple

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/employees',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_generic_get_single(self):
        """Test case for generic_get_single

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/employee/{employee_id}'.format(employee_id='employee_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_generic_post_single(self):
        """Test case for generic_post_single

        
        """
        employee_to_add = {
  "firstname" : "Izzy",
  "lastname" : "Van isteren"
}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/employees',
            method='POST',
            headers=headers,
            data=json.dumps(employee_to_add),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_generic_put_single(self):
        """Test case for generic_put_single

        
        """
        employee_to_add = {
  "firstname" : "Izzy",
  "lastname" : "Van isteren"
}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/employee/{employee_id}'.format(employee_id='employee_id_example'),
            method='PUT',
            headers=headers,
            data=json.dumps(employee_to_add),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
