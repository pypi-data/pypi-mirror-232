"""
The HEA Registry Service provides a table of all currently active HEA microservices. Microservices each have an unique
component name field, and the name may be used to get other information about the microservice including its base URL
to make REST API calls.
"""
import logging

from heaserver.service import response, appproperty
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action
from heaobject.registry import Component, Property, Collection
from heaobject.root import ShareImpl, Permission
from heaobject.volume import DEFAULT_FILE_SYSTEM, MongoDBFileSystem
from heaobject.user import ALL_USERS
from typing import AsyncIterator

MONGODB_COMPONENT_COLLECTION = 'components'
MONGODB_PROPERTIES_COLLECTION = 'properties'
MONGODB_COLLECTION_COLLECTION = 'collection'


@routes.get('/components/{id}')
@action('heaserver-registry-component-get-properties', rel='hea-properties')
@action('heaserver-registry-component-duplicate', rel='hea-duplicator', path='components/{id}/duplicator')
async def get_component(request: web.Request) -> web.Response:
    """
    Gets the component with the specified id.
    :param request: the HTTP request.
    :return: the requested component or Not Found.
    ---
    summary: A specific component, by id.
    tags:
        - heaserver-registry-component
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get(request, MONGODB_COMPONENT_COLLECTION)


@routes.get('/components/byname/{name}')
async def get_component_by_name(request: web.Request) -> web.Response:
    """
    Gets the component with the specified id.
    :param request: the HTTP request.
    :return: the requested component or Not Found.
    ---
    summary: A specific component, by name.
    tags:
        - heaserver-registry-component
    parameters:
        - $ref: '#/components/parameters/name'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get_by_name(request, MONGODB_COMPONENT_COLLECTION)


@routes.get('/components/bytype/{type}')
@routes.get('/components/bytype/{type}/byfilesystemtype/{filesystemtype}')
@routes.get('/components/bytype/{type}/byfilesystemtype/{filesystemtype}/byfilesystemname/{filesystemname}')
async def get_component_by_type(request: web.Request) -> web.Response:
    """
    Gets the component that serves resources of the specified HEA object type and file system. If no file system name
    is passed in, DEFAULT_FILE_SYSTEM is assumed. If not file system type is passed in,
    heaobject.volume.MongoDBFileSystem is assumed.

    :param request: the HTTP request.
    :return: the requested component or Not Found.
    ---
    summary: A specific component, by type and file system.
    tags:
        - heaserver-registry-component
    parameters:
        - name: type
          in: path
          required: true
          description: The type of the component to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A component type
              value: heaobject.folder.Folder
        - name: filesystemtype
          in: path
          required: true
          description: The type of the component's file system.
          schema:
            type: string
          examples:
            example:
              summary: A component type
              value: heaobject.volume.MongoDBFileSystem
        - name: filesystemname
          in: path
          required: true
          description: The name of the component's file system.
          schema:
            type: string
          examples:
            example:
              summary: A component name
              value: DEFAULT_FILE_SYSTEM
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    if 'filesystemname' in request.match_info:
        file_system_name = request.match_info['filesystemname']
    else:
        file_system_name = DEFAULT_FILE_SYSTEM
    if file_system_name == DEFAULT_FILE_SYSTEM:
        query_clause = {'$or': [{'file_system_name': {'$exists': False}}, {'file_system_name': {'$in': [file_system_name, None]}}]}
    else:
        query_clause = {'file_system_name': {'$eq': file_system_name}}
    if 'filesystemtype' in request.match_info:
        file_system_type = request.match_info['filesystemtype']
    else:
        file_system_type = MongoDBFileSystem.get_type_name()
    if file_system_type == MongoDBFileSystem.get_type_name():
        query_clause.update({'$or': [{'file_system_type': {'$exists': False}}, {'file_system_type': {'$in': [file_system_type, None]}}]})
    else:
        query_clause.update({'file_system_type': {'$eq': file_system_type}})
    mongo_attributes = {'resources': {
        '$elemMatch': {
            'resource_type_name': {'$eq': request.match_info['type']},
            **query_clause
        }}}
    result = await request.app[appproperty.HEA_DB].get(request,
                                                       MONGODB_COMPONENT_COLLECTION,
                                                       mongoattributes=mongo_attributes)
    return await response.get(request, result)


@routes.get('/components')
@routes.get('/components/')
@action('heaserver-registry-component-get-properties', rel='hea-properties')
@action('heaserver-registry-component-duplicate', rel='hea-duplicator', path='components/{id}/duplicator')
async def get_all_components(request: web.Request) -> web.Response:
    """
    Gets all components.
    :param request: the HTTP request.
    :return: all components.
    ---
    summary: All components.
    tags:
        - heaserver-registry-component
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    return await mongoservicelib.get_all(request, MONGODB_COMPONENT_COLLECTION)


@routes.get('/components/{id}/duplicator')
@action(name='heaserver-registry-component-duplicate-form')
async def get_component_duplicator(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested component.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested component was not found.
    ---
    summary: A specific component, by id.
    tags:
        - heaserver-registry-component
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get(request, MONGODB_COMPONENT_COLLECTION)


@routes.post('/components/duplicator')
async def post_component_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided component for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    ---
    summary: Component duplication.
    tags:
        - heaserver-registry-component
    requestBody:
      description: A duplicate component object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "template": {
                  "data": [{
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "description",
                    "value": null
                  },
                  {
                    "name": "display_name",
                    "value": "Joe"
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "joe"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shares",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "base_url",
                    "value": "http://localhost/foo"
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "resource_type_name",
                    "value": "heaobject.folder.Folder",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "type",
                    "value": "heaobject.registry.Resource",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "base_path",
                    "value": "/folders"
                  },
                  {
                   "section": "resources",
                    "index": 0,
                    "name": "file_system_name",
                    "value": "DEFAULT_MONGODB"
                  },
                  {
                    "name": "type",
                    "value": "heaobject.registry.Component"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Joe",
                "modified": null,
                "name": "joe",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "type": "heaobject.registry.Component",
                "version": null,
                "base_url": "http://localhost/foo",
                "resources": [{
                    "type": "heaobject.registry.Resource",
                    "resource_type_name": "heaobject.folder.Folder",
                    "base_path": "/folders",
                    "file_system_name": "DEFAULT_MONGODB"
                }]
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'

    """
    return await mongoservicelib.post(request, MONGODB_COMPONENT_COLLECTION, Component)


@routes.post('/components')
@routes.post('/components/')
async def post_component(request: web.Request) -> web.Response:
    """
    Posts the provided component.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    ---
    summary: Component creation
    tags:
        - heaserver-registry-component
    requestBody:
      description: A new component object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "template": {
                  "data": [{
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "derived_by",
                    "value": null
                  },
                  {
                    "name": "derived_from",
                    "value": []
                  },
                  {
                    "name": "description",
                    "value": null
                  },
                  {
                    "name": "display_name",
                    "value": "Joe"
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "joe"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shares",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "base_url",
                    "value": "http://localhost/foo"
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "resource_type_name",
                    "value": "heaobject.folder.Folder",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "type",
                    "value": "heaobject.registry.Resource",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "base_path",
                    "value": "/folders"
                  },
                  {
                   "section": "resources",
                    "index": 0,
                    "name": "file_system_name",
                    "value": "DEFAULT_MONGODB"
                  },
                  {
                    "name": "type",
                    "value": "heaobject.registry.Component"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Joe",
                "modified": null,
                "name": "joe",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "type": "heaobject.registry.Component",
                "version": null,
                "base_url": "http://localhost/foo",
                "resources": [{
                    "type": "heaobject.registry.Resource",
                    "resource_type_name": "heaobject.folder.Folder",
                    "base_path": "/folders",
                    "file_system_name": "DEFAULT_MONGODB"
                }]
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.post(request, MONGODB_COMPONENT_COLLECTION, Component)


@routes.put('/components/{id}')
async def put_component(request: web.Request) -> web.Response:
    """
    Updates the component with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    ---
    summary: Component updates
    tags:
        - heaserver-registry-component
    parameters:
        - $ref: '#/components/parameters/id'
    requestBody:
      description: An updated component object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "template": {
                  "data": [{
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "derived_by",
                    "value": null
                  },
                  {
                    "name": "derived_from",
                    "value": []
                  },
                  {
                    "name": "description",
                    "value": null
                  },
                  {
                    "name": "display_name",
                    "value": "Reximus Max"
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "reximus"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shares",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "base_url",
                    "value": "http://localhost/foo"
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "resource_type_name",
                    "value": "heaobject.folder.Folder",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "type",
                    "value": "heaobject.registry.Resource",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "base_path",
                    "value": "/folders"
                  },
                  {
                   "section": "resources",
                    "index": 0,
                    "name": "file_system_name",
                    "value": "DEFAULT_MONGODB"
                  },
                  {
                  "name": "id",
                  "value": "666f6f2d6261722d71757578"
                  },
                  {
                  "name": "type",
                  "value": "heaobject.registry.Component"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "id": "666f6f2d6261722d71757578",
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Reximus Max",
                "modified": null,
                "name": "reximus",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "type": "heaobject.registry.Component",
                "version": null,
                "base_url": "http://localhost/foo",
                "resources": [{
                    "type": "heaobject.registry.Resource",
                    "resource_type_name": "heaobject.folder.Folder",
                    "base_path": "/folders",
                    "file_system_name": "DEFAULT_MONGODB"
                }]
              }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.put(request, MONGODB_COMPONENT_COLLECTION, Component)


@routes.delete('/components/{id}')
async def delete_component(request: web.Request) -> web.Response:
    """
    Deletes the component with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Component deletion
    tags:
        - heaserver-registry-component
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.delete(request, MONGODB_COMPONENT_COLLECTION)


@routes.get('/properties/{id}')
async def get_property(request: web.Request) -> web.Response:
    """
    Gets the property with the specified id.
    :param request: the HTTP request.
    :return: the requested property or Not Found.
    ---
    summary: A specific property, by id.
    tags:
        - heaserver-registry-property
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get(request, MONGODB_PROPERTIES_COLLECTION)


@routes.get('/properties/byname/{name}')
async def get_property_by_name(request: web.Request) -> web.Response:
    """
    Gets the property with the specified id.
    :param request: the HTTP request.
    :return: the requested property or Not Found.
    ---
    summary: A specific property, by name.
    tags:
        - heaserver-registry-property
    parameters:
        - name: name
          in: path
          required: true
          description: The name of the property.
          schema:
            type: string
          examples:
            example:
              summary: A property name
              value: applicationName

    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get_by_name(request, MONGODB_PROPERTIES_COLLECTION)


@routes.get('/properties')
@routes.get('/properties/')
async def get_all_properties(request: web.Request) -> web.Response:
    """
    Gets all properties.
    :param request: the HTTP request.
    :return: all properties.
    ---
    summary: All properties.
    tags:
        - heaserver-registry-property
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    return await mongoservicelib.get_all(request, MONGODB_PROPERTIES_COLLECTION)


@routes.post('/properties')
@routes.post('/properties/')
async def post_property(request: web.Request) -> web.Response:
    """
    Posts the provided property.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    ---
    summary: Property creation
    tags:
        - heaserver-registry-property
    requestBody:
      description: A new property object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Property example
              value: {
                "template": {
                  "data": [
                    {"name": "name", "value": "exampleProperty"},
                    {"name": "value", "value": "some value"},
                    {"name": "display_name", "value": "Example Property"},
                    {"name": "type", "value": "heaobject.registry.Property"}
                  ]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Property example
              value: {
                "name": "exampleProperty",
                "value": "some value",
                "display_name": "Example Property",
                "type": "heaobject.registry.Property"
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.post(request, MONGODB_PROPERTIES_COLLECTION, Property)


@routes.put('/properties/{id}')
async def put_property(request: web.Request) -> web.Response:
    """
    Updates the property with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    ---
    summary: Property updates
    tags:
        - heaserver-registry-property
    parameters:
        - $ref: '#/components/parameters/id'
    requestBody:
      description: An updated property object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: A property example
              value: {
                "template": {
                  "data": [
                    {
                      "name": "name",
                      "value": "HEA"
                    },
                    {
                      "name": "created",
                      "value": null
                    },
                    {
                      "name": "derived_by",
                      "value": null
                    },
                    {
                      "name": "derived_from",
                      "value": []
                    },
                    {
                      "name": "description",
                      "value": null
                    },
                    {
                      "name": "display_name",
                      "value": "Reximus"
                    },
                    {
                      "name": "modified",
                      "value": null
                    },
                    {
                      "name": "owner",
                      "value": "system|none"
                    },
                    {
                      "name": "shares",
                      "value": []
                    },
                    {
                      "name": "source",
                      "value": null
                    },
                    {
                      "name": "version",
                      "value": null
                    },
                    {
                      "name": "base_url",
                      "value": "http://localhost/foo"
                    },
                    {
                      "section": "resources",
                      "index": 0,
                      "name": "resource_type_name",
                      "value": "heaobject.folder.Folder"
                    },
                    {
                      "section": "resources",
                      "index": 0,
                      "name": "base_path",
                      "value": "/folders"
                    },
                    {
                      "section": "resources",
                      "index": 0,
                      "name": "file_system_name",
                      "value": "DEFAULT_MONGODB"
                    },
                    {
                      "name": "id",
                      "value": "666f6f2d6261722d71757578"
                    },
                    {
                      "name": "type",
                      "value": "heaobject.registry.Property"
                    }
                  ]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: A property example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Untitled Property",
                "id": "618da15104811d77ca7221fd",
                "invites": [],
                "modified": null,
                "name": "applicationName",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "type": "heaobject.registry.Property",
                "value": "HEA",
                "version": null
              }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.put(request, MONGODB_PROPERTIES_COLLECTION, Property)


@routes.delete('/properties/{id}')
async def delete_property(request: web.Request) -> web.Response:
    """
    Deletes the property with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Property deletion
    tags:
        - heaserver-registry-property
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.delete(request, MONGODB_PROPERTIES_COLLECTION)


@routes.get('/collections')
@routes.get('/collections/')
@action(name='heaserver-registry-collection-get-open-choices', rel='hea-opener-choices', path='collections/{id}/opener')
@action(name='heaserver-registry-collection-get-properties', rel='hea-properties')
@action(name='heaserver-registry-collection-get-self', rel='self', path='collections/{id}')
async def get_all_collections(request: web.Request) -> web.Response:
    """
    Gets all collections.

    :param request: the HTTP request.
    :return: all collections.
    ---
    summary: All collections.
    tags:
        - heaserver-registry-collection
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    collections = []
    async for obj in mongoservicelib.get_all_gen(request, MONGODB_COMPONENT_COLLECTION):
        for resource in obj['resources']:
            c = Collection()
            c.id = resource['resource_type_name']
            c.name = resource['resource_type_name']
            c.display_name = resource['resource_collection_type_display_name']
            c.collection_type_name = resource['resource_type_name']
            c.url = resource['base_path']
            share = ShareImpl()
            share.user = ALL_USERS
            share.permissions = [Permission.VIEWER, Permission.CHECK_DYNAMIC]
            c.shares = [share]
            collections.append(c.to_dict())
    return await response.get_all(request, collections)


@routes.get('/collections/{id}')
@action(name='heaserver-registry-collection-get-open-choices', rel='hea-opener-choices', path='collections/{id}/opener')
@action(name='heaserver-registry-collection-get-properties', rel='hea-properties')
@action(name='heaserver-registry-collection-get-self', rel='self', path='collections/{id}')
async def get_collection(request: web.Request) -> web.Response:
    """
    Gets a collection.

    :param request: the HTTP Request.
    :return: A Response object with a status of Multiple Choices or Not Found.
    ---
    summary: Collection
    tags:
        - heaserver-registry-collection
    parameters:
        - name: id
          in: path
          required: true
          description: The id of the collection.
          schema:
            type: string
          examples:
            example:
              summary: A collection id
              value: heaobject.folder.Item
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_collection(request)


@routes.get('/collections/byname/{name}')
@action(name='heaserver-registry-collection-get-self', rel='self', path='collections/{id}')
async def get_collection_by_name(request: web.Request) -> web.Response:
    """
    Gets a collection by name.

    :param request: the HTTP Request.
    :return: A Response object with a status of Multiple Choices or Not Found.
    ---
    summary: Collection
    tags:
        - heaserver-registry-collection
    parameters:
        - name: name
          in: path
          required: true
          description: The name of the collection.
          schema:
            type: string
          examples:
            example:
              summary: A collection name
              value: heaobject.folder.Item
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    request.match_info['id'] = request.match_info['name']
    return await _get_collection(request)

@routes.get('/collections/{id}/opener')
@action('heaserver-registry-collection-open', rel=f'hea-opener hea-default', path='{+url}')
async def get_collection_opener(request: web.Request) -> web.Response:
    """
    Gets a collection with a default link to open it, if the format in the Accept header supports links.

    :param request: the HTTP Request.
    :return: A Response object with a status of Multiple Choices or Not Found.
    ---
    summary: Collection opener choices
    tags:
        - heaserver-registry-collection
    parameters:
        - name: id
          in: path
          required: true
          description: The id of the collection.
          schema:
            type: string
          examples:
            example:
              summary: A collection id
              value: heaobject.folder.Item
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_collection(request)


def main() -> None:
    config = init_cmd_line(description='Registry of HEA services, HEA web clients, and other web sites of interest',
                           default_port=8080)
    start(db=mongo.MongoManager,
          wstl_builder_factory=builder_factory(__package__), config=config)


async def _get_collection(request: web.Request) -> web.Response:
    mongo_attributes = {'resources': {
        '$elemMatch': {
            'resource_type_name': {'$eq': request.match_info['id']},
        }}}
    async for obj in mongoservicelib.get_all_gen(request, MONGODB_COMPONENT_COLLECTION, mongoattributes=mongo_attributes):
        for resource in (r for r in obj['resources'] if r['resource_type_name'] == request.match_info['id']):
            c = Collection()
            c.id = resource['resource_type_name']
            c.name = resource['resource_type_name']
            c.display_name = resource['resource_collection_type_display_name']
            c.collection_type_name = resource['resource_type_name']
            c.url = resource['base_path']
            share = ShareImpl()
            share.user = ALL_USERS
            share.permissions = [Permission.VIEWER, Permission.CHECK_DYNAMIC]
            c.shares = [share]
            return await response.get(request, c.to_dict())
    return await response.get(request, None)
