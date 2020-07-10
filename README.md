# Dynamic Data Manipulation API

This API is a tool to view and edit data dynamically based purely on configuration.

## Setup
To start the API the following steps have to be taken:
1. Create a `config.py` file with all necessary configuration (see [Configuration](#configuration));
2. Create a `openapi.yaml` based on the [OpenAPI specification](https://swagger.io/specification/) (see [OpenAPI Specification](#openapi-specification));
3. Generate OpenAPI models with the help of [OpenAPI generator](https://github.com/OpenAPITools/openapi-generator) (see [Models](#models));
4. Install Python packages from `requirements.txt`:
    ~~~bash
    pip3 install -r requirements.txt
    ~~~
5. Run the api:
    ~~~bash
    python3 -m openapi_server
    ~~~

### Configuration
Part of the configuration for this API is a `config.py` file containing some variables. This file contains the private configuration needed for 
authentication and database connections. To create a `config.py` file you can take a look at the [config.example.py](api_server/config.example.py) file.

The available variables are:
- `OAUTH_EXPECTED_AUDIENCE`: `[string]` The Azure AD audience needed for access
- `OAUTH_EXPECTED_ISSUER`: `[string]` The Azure AD issuer ID
- `OAUTH_JWKS_URL`: `[string]` The Azure AD URL for JWK info
- `ORIGINS`: `[required]` `[list]` A list containing allowed origins for access
- `DATABASE_TYPE`: `[required]` `[string]` The identifier for the database to be used (see [Database Type](#database-type))
- `AUDIT_LOGS_NAME`: `[string]` The identifier for the Database table where the audit logs will be inserted (see [Audit logging](#audit-logging))
- `KMS_KEY_INFO`: `[object]` KMS information for encrypting and decrypting sensitive information (see [Cursor encryption](#cursor-encryption))

#### Database Type
One of the configuration variables to be specified is the `DATABASE_TYPE`. This will specify the database the API will use to add, retrieve and edit
entities. Currently the API supports the following database types:
- `datastore`: [Google Cloud Datastore](https://cloud.google.com/datastore/docs)
- `firestore`: [Google Cloud Firestore](https://cloud.google.com/firestore/docs)

When no database type is specified the function will return a `500` code.

### OpenAPI Specification
A big part of this API is the specification based on [OpenAPI](https://swagger.io/specification/). To create the correct endpoints and retrieve 
and save data a specification has to be available to the API. The specification is based on four main pillars: [methods](#method-operations), [paths](#path-parameter), 
[schemas](#schemas) ans [security](#security). Because this API is generic of some sort the specification has to have some 
components to make the API work. Below these components are explained on how you use them. Make sure the file will be available in `openapi_server/openapi/openapi.yaml`. 

#### Method operations
To ensure the only configuration you need to make this API work there are some generic definitions specified within the API where data can be retrieved from
or posted to. These definitions make sure when a path is requested a function will process the request. There are three major definitions that can be used.
- `generic_get_multiple`: Retrieves all entities from a database table;
- `generic_get_multiple_page`: Retrieves entities from a database table page (see [Pagination](#pagination));
- `generic_get_single`: Retrieves one entity from a database table, based on a `unique_id`;
- `generic_post_single`: Creates a new entity in a database table, based on a request body;
- `generic_put_single`: Updates an existing entity from a database table, based on a `unique_id` and a request body.

You can add these operations with help op `operationId` within a path's method:
~~~yaml
paths:
  /pets:
    get:
      description: Get a list of all pets
      operationId: generic_get_multiple
      x-openapi-router-controller: openapi_server.controllers.default_controller
~~~

Because OpenAPI requires the specification to have unique `operationId`'s, this API has multiple versions of the methods described above.
To add two paths with both the posibility to post a single entity, the definitions `generic_post_single` and `generic_post_single2` can be used.
Both these operations execute the same function but have unique identifiers.

_For each definition are three implementations (e.g. `generic_post_single`, `generic_post_single2` and `generic_post_single3`)_

#### Path parameter
To create an endpoint for single entities, a path parameter has to be defined. This path parameter will be used to retrieve or update
a single entity in the specified database table(see [Database Reference](#database-reference)). The name of this parameter 
will be used to retrieve the identifier from the request and passed towards the database connections.

The parameter can be defined as described in the example below:
~~~yaml
paths:
  /pets/{pet_id}:
    get:
      description: Get a single pet by identifier
      operationId: generic_get_single  
      parameters:
        - explode: false
          in: path
          name: pet_id
          required: true
          schema:
            format: uuid
            type: string
          style: simple
      x-openapi-router-controller: openapi_server.controllers.default_controller
~~~

#### Pagination
Within the API it is also possible to create pagination by using a page cursor, size and action. It is important to implement
the pagination as described below to optimize the use of cursors.

First, two paths to be defined: one to request a list of entities without referencing any cursor and one to request a specific
page of entities based on a cursor. Both paths will use the operation implementation `generic_get_multiple_page*` as 
it is optimized to support both type of requests.

##### 1. Initial request
The first path method to be defined is a path that will retrieve all entities from a database table based on a page size. As seen
in the code below we are creating a `paths` that passes a `page_size` query parameter. This ensures the endpoint will retrieve
a list of X entities based on the `page_size`, that is defined within the `components/parameters/pageSizeParam` definition.

Furthermore a response is defined based on the `components/schemas/PetsResponse` definition. It is essential that the request's response
is defined with the same objects as in de example below. The parts that can be changed are the name of the definition and the `items` within the `results` array.

This initial request will get a list of entities and will return the uri towards the next list of entities.

~~~yaml
paths:
  /pets:
    get:
      description: Get a list of pets
      operationId: generic_get_multiple_page
      parameters:
        - $ref: '#/components/parameters/pageSizeParam'
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PetsResponse'
          description: Returns a list of pets
      x-openapi-router-controller: openapi_server.controllers.default_controller
components:
  parameters:
    pageSizeParam:
      in: query
      name: page_size
      required: false
      schema:
        default: 50
        maximum: 100
        minimum: 1
        type: integer
      description: The numbers of items within a page
  schemas:
    PetsResponse:
      example:
        status: Success
        page_size: 50
        next_page: https://example.com/pages/eee028e4-ef38-40fb-a92b-41c441660d2e
        results: []
      properties:
        status:
          description: The request status.
          type: string
        page_size:
          description: The current page size
          format: int32
          type: integer
        prev_page:
          description: The prev page uri
          type: string
        next_page:
          description: The next page uri
          type: string
        results:
          items:
            $ref: '#/components/schemas/Pets'
          type: array
      type: object
~~~

##### 2. Request based on a page
After the initial request has been done we can request specific pages based on the `page_cursor`. A cursor is a string 
that points towards a specific entity within the database and is generated by the API. The path that will process these 
specific pages is defined as below. It is essential that the path is a duplicated of the first request path (as described above)
extended with `/pages/{page_cursor}`. Within the API both these uri parts are used to retrieve the specific pages and create
a uri for the next page.

This path will also use the previously defined `page_size` query parameter, `PetsResponse` response schema and `generic_get_multiple_page2`
operation. Make sure this operation ID has a different implementation (e.g. `generic_get_multiple_page2` instead of `generic_get_multiple_page`) 
to ensure we conform to the Zally specifications  (see [Method operations](#method-operations)). The additions for this 
path are the `page_cursor` path parameter and `page_action` parameter. As explained the `page_cursor` will ensure the 
database returns entities from a specific point in the database and the `page_action` will define if we retrieve the 
entities after this point or before this point with the values `next` and `prev`.

~~~yaml
paths:
  /pets/pages/{page_cursor}:
    get:
      description: Get a list of pets from a specific page
      operationId: generic_get_multiple_page2
      parameters:
        - $ref: '#/components/parameters/pageCursorParam'
        - $ref: '#/components/parameters/pageSizeParam'
        - $ref: '#/components/parameters/pageActionParam'
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PetsResponse'
          description: Returns a list of pets
      x-openapi-router-controller: openapi_server.controllers.default_controller
components:
  parameters:
    pageCursorParam:
      in: path
      explode: false
      name: page_cursor
      required: true
      schema:
        type: string
      style: simple
      description: The cursor for retrieve a specific page
    pageActionParam:
      in: query
      name: page_action
      required: false
      schema:
        default: next
        enum:
          - prev
          - next
        type: string
      description: Selector to get next or previous page based on the cursor
~~~

##### Indexes
To make sure the database will order the entities as required a index has to be defined. This is only needed for the 
database type Datastore (see [Database Type](#database-type)). This index will ensure the entities are filtered on there 
key differenly for both the `next` as `prev` `page_action` action and is needed to support pagination for Datastore tables. 

The index can be deployed with the following configuration file 
(see [Creating Datastore Indexes](https://cloud.google.com/sdk/gcloud/reference/datastore/indexes/create)):
~~~yaml
indexes:
- kind: Pets
  properties:
  - name: __key__
    direction: desc
~~~

##### Cursor encryption
It is possible for a client to decode the cursors to expose information about entities, such as the project ID, 
entity kind, key name or numeric ID, ancestor keys, and properties used in the query's filters and sort orders. To ensure
this is not possible, the API supports [KMS](https://cloud.google.com/kms/docs/encrypt-decrypt) encryption and decryption for the cursors.
To enable this functionality, a configuration key has to be added to the `config.py` file as shown below:
~~~python
KMS_KEY_INFO = {
    "keyring": "keyring-name",
    "key": "key-name",
    "location": "location-name"
}
~~~

These configuration keys can be defined when creating a KMS keyring and its key and are necessary to encrypt and decrypt
the cursors. If this object is provided within the `config.py` the KMS encryption/decryption is automatically enabled. 
If not, it will return the cursor without decryption.


#### Database reference
To connect the endpoints to specific database tables, the custom [extension](https://swagger.io/docs/specification/openapi-extensions) 
`x-db-table-name` must be used to ensure each path has it's database table name. The extension for this API can only be added to 
individual paths, as shown below, and is required for each path.
~~~yaml
paths:
    /pets:
      get:
          description: Get a list of all pets
          operationId: generic_get_multiple
          x-openapi-router-controller: openapi_server.controllers.default_controller
      post:
        description: Create a new pet
        operationId: generic_post_single
        x-openapi-router-controller: openapi_server.controllers.default_controller
      x-db-table-name: Pets
~~~ 

#### Schemas
A big part of the OpenAPI specification are the [schemas](https://swagger.io/docs/specification/data-models/) that can be defined.
These schemas are used to validate all incoming information and to return the correct information from the database. 
OpenAPI requires to define a schema on each path's method to ensure this functionality. Fortunately schemas can be re-used 
and are ease to create. After creating the schemas the API also requires to generate the correct models as described in '[Models](#models)'.

The example below creates a schema within the OpenAPI specification.
~~~yaml
components:
  schemas:
    Pet:
      description: Information about a pet
      example:
        pet_id: a0e7fd7e-7134-46da-b6be-f152cff23da5
        name: Doggy
        breed: Bulldog
      properties:
        pet_id:
          format: uuid
          type: string
        name:
          maxLength: 100
          type: string
        breed:
          maxLength: 100
          type: string
~~~

To use this schema as a input validator, define this as the request body`:
~~~yaml
paths:
  /pets/{unique_id}:
    put:
      description: Updates an existing pet
      operationId: generic_put_single
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Pet'
        description: Pet to update
        required: true
~~~

To use this schema as an output validator, define this as the content from a response:
~~~yaml
paths:
  /pets/{unique_id}:
    get:
      description: Returns a pet
      operationId: generic_get_single
      responses:
        "200":
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Pet'
          description: Returns a pet
~~~

_Currently, the only [media type](https://swagger.io/docs/specification/describing-responses/#media-types) supported is `application/json`._

##### Schema identifier
The API will create response and body objects based on the schema's defined within a path method fully automatic. A big part of
this automated process is the use of an identifier. As described before, you can create a [path parameter](#path-parameter) 
to request a single entity. But to ensure the identifier is also available on each response object, a schema identifier has
to be defined. This schema-identifier will be used to pass the distinct ID towards the response object.

To let the API now on each request what attribute the ID is, two things have to be done:
1.  Mark a schema property as [read-only](https://swagger.io/docs/specification/data-models/data-types/#readonly-writeonly).
    This will ensure the property will be returned on a `GET`, but cannot be updated on a `PUT`, `PATCH` or `POST`. 
    Because of this you can use the same schema in both `GET` and `POST` requests;
    ~~~yaml
    pet_id:
      format: uuid
      type: string
      readOnly: true
    ~~~
2.  Define a property as a schema's identifier by adding the `x-db-table-id` extension, that is required with each single entity schema.
    ~~~yaml
    properties:
      pet_id:
        format: uuid
        type: string
        readOnly: true
      name:
        maxLength: 100
        type: string
    x-db-table-id: pet_id
    ~~~

#### Security
An option to secury the endpoints is also available in the Dynamic Data Manipulation API. For now it can only be used with the 
[Azure Active Directory](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app).
To use this option some environment variables have to be defined in the `config.py` file (as described in [Configuration](#Configuration)). The needed 
variables are `OAUTH_EXPECTED_AUDIENCE`, `OAUTH_EXPECTED_ISSUER` and `OAUTH_JWKS_URL`. These variables will be used to validate a token passed with the request
in the `security_controller`.

To create a security definition use the example below:
~~~yaml
components:
  securityschemas:
    oauth2:
      type: oauth2
      description: This API uses OAuth 2 with the implicit grant flow.
      flows:
        implicit:
          authorizationUrl: https://azuread.url/2.0/authorize
          scopes:
            customscope.read: View access to Dynamic Data Manipulation API
            customescope.edit: Edit access to Dynamic Data Manipulation API
      x-tokenInfoFunc: openapi_server.controllers.security_controller_.info_from_oAuth2
      x-scopeValidateFunc: connexion.decorators.security.validate_scope
~~~

The format above is necessary to enable the security within the API, where the only items that have to be changed are the `scopes`. These are Azure AD application
specific and thus can be find within the [application registry on Azure](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-configure-app-expose-web-apis#expose-a-new-scope-through-the-ui).

The enabling of scopes on an endpoint can be done as follow:
~~~yaml
paths:
  /pets:
    get:
      description: Get a list of all pets
      operationId: generic_get_multiple
      x-openapi-router-controller: openapi_server.controllers.default_controller
      security:
        - oauth2: [customscope.read]
    post:
      description: Create a new pet
      operationId: generic_post_single
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PetToAdd'
        description: Pet to add
        required: true
      x-openapi-router-controller: openapi_server.controllers.default_controller
      security:
        - oauth2: [customscope.edit]
~~~

### Models
After creating an OpenAPI specification the only thing left to do is generating models based on the defined schemas.
These models are used by the API to validate the input and output of requests. These models are generated with help of
the [OpenAPI generator](https://github.com/OpenAPITools/openapi-generator).

To generate these models for your local environment use the shell script provisioned within the API: 
~~~bash
./generate-models.sh
~~~

To generate this model within a GCP Cloud Build, use the build step defined below: 
~~~yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - '-c'
      - |
        docker run --rm -v /api_server:/local openapitools/openapi-generator-cli generate \
          -i /local/openapi_server/openapi/openapi.yaml \
          -g python-flask \
          -o /local \
          --global-property=models
~~~

### Audit logging
To track all changes that are made using the API some form of audit logging can be enabled. By declaring the 
configuration variable `AUDIT_LOGS_NAME` the API will log each transaction into the Database. This will create a new
table in the chosen database and will be filled with the following transaction information:
- Attributes changed
- Entity ID
- Table Name
- Timestamp
- User email or IP address

### Deploying to Google Cloud Platform
To deploy the API to the Google Cloud Platform a couple of options are available.

#### Cloud Run
The API can be deployed as serverless container to [Cloud Run](https://cloud.google.com/run/docs). The `Dockerfile` can be used to create a container
ready to run on Cloud Run. Use the example build steps defined in [cloudbuild.example.yaml](api_server/cloudbuild.example.yaml)
to deploy this API.


## License
This API is licensed under the [GPL-3](https://www.gnu.org/licenses/gpl-3.0.en.html) License