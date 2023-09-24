"""
Creates a test case class for use with the unittest library that is built into Python.
"""
from heaserver.service.testcase import expectedvalues
from heaserver.service.testcase.microservicetestcase import get_test_case_cls_default
from heaserver.service.testcase.dockermongo import DockerMongoManager
from heaserver.volume import service
from heaobject.user import NONE_USER
from heaserver.service.testcase.expectedvalues import Action, Link
from heaserver.service.testcase.dockermongo import RealRegistryContainerConfig

db_store = {
    service.MONGODB_VOLUME_COLLECTION: [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'invites': [],
        'shares': [],
        'modified': None,
        'name': 'heaobject.volume.MongoDBFileSystem^DEFAULT_FILE_SYSTEM',
        'owner': NONE_USER,
        'source': None,
        'type': 'heaobject.volume.Volume',
        'file_system_type': 'heaobject.volume.MongoDBFileSystem',
        'file_system_name': 'DEFAULT_FILE_SYSTEM',
        'folder_id': '666f6f2d6261722d71757578',
        'mime_type': 'application/x.volume',
        'credential_id': None
    },
    {
        'id': '0123456789ab0123456789ab',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Luximus',
        'invites': [],
        'shares': [],
        'modified': None,
        'name': 'heaobject.volume.AWSFileSystem^DEFAULT_FILE_SYSTEM',
        'owner': NONE_USER,
        'source': None,
        'type': 'heaobject.volume.Volume',
        'file_system_type': 'heaobject.volume.AWSFileSystem',
        'file_system_name': 'DEFAULT_FILE_SYSTEM',
        'folder_id': '0123456789ab0123456789ab',
        'mime_type': 'application/x.volume',
        'credential_id': None
    }],
    service.MONGODB_FILE_SYSTEM_COLLECTION: [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': 'Access to Amazon Web Services (AWS)',
        'display_name': 'Amazon Web Services',
        'invites': [],
        'shares': [],
        'modified': None,
        'name': 'DEFAULT_FILE_SYSTEM',
        'owner': NONE_USER,
        'source': None,
        'type': 'heaobject.volume.AWSFileSystem'
    },
        {
            'id': '0123456789ab0123456789ab',
            'created': None,
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'Local MongoDB instance',
            'invites': [],
            'shares': [],
            'modified': None,
            'name': 'DEFAULT_FILE_SYSTEM',
            'owner': NONE_USER,
            'source': None,
            'type': 'heaobject.volume.MongoDBFileSystem',
            'database_name': 'hea',
            'connection_string': 'mongodb://heauser:heauser@localhost:27017/hea'
        }],
    'folders': [{
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'id': '666f6f2d6261722d71757578',
        'invites': [],
        'modified': None,
        'name': 'reximus',
        'owner': NONE_USER,
        'shares': [],
        'source': None,
        'type': 'heaobject.folder.Folder',
        'version': None,
        'mime_type': 'application/x.folder'
    },
        {
            'created': None,
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'Reximus',
            'id': '666f6f2d6261722d71757579',
            'invites': [],
            'modified': None,
            'name': 'reximus',
            'owner': NONE_USER,
            'shares': [],
            'source': None,
            'type': 'heaobject.folder.Folder',
            'version': None,
            'mime_type': 'application/x.folder'
        }],
    'folders_items': [{
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'id': '666f6f2d6261722d71757578',
        'invites': [],
        'modified': None,
        'name': 'reximus',
        'owner': NONE_USER,
        'shares': [],
        'source': None,
        'type': 'heaobject.folder.Item',
        'version': None,
        'actual_object_type_name': 'heaobject.folder.Folder',
        'actual_object_id': '666f6f2d6261722d71757579',
        'folder_id': '666f6f2d6261722d71757578'
    }],
    'components': [{
            'id': '666f6f2d6261722d71757578',
            'created': None,
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'Reximus',
            'invited': [],
            'modified': None,
            'name': 'heaserver-volumes',
            'owner': NONE_USER,
            'shared_with': [],
            'source': None,
            'type': 'heaobject.registry.Component',
            'base_url': 'http://localhost:8080',
            'resources': [{'type': 'heaobject.registry.Resource', 'resource_type_name': 'heaobject.volume.Volume',
                           'base_path': 'volumes'}]
        }]
}


def get_test_case_cls(*args, **kwargs):
    """Get a test case class specifically for this microservice."""

    class MyTestCase(get_test_case_cls_default(*args, **kwargs)):
        def __init__(self, *args_, **kwargs_):
            super().__init__(*args_, **kwargs_)
            if self._body_post:
                modified_data = {**db_store[self._coll][0], 'display_name': 'My File System'}
                if 'id' in modified_data:
                    del modified_data['id']
                self._body_post = expectedvalues._create_template(modified_data)

    return MyTestCase


HEASERVER_REGISTRY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-registry:1.0.0b3'


VolumeTestCase = get_test_case_cls(coll=service.MONGODB_VOLUME_COLLECTION,
                                   href='http://localhost:8080/volumes',
                                   wstl_package=service.__package__,
                                   db_manager_cls=DockerMongoManager,
                                   fixtures=db_store,
                                   get_actions=[Action(name='heaserver-volumes-volume-get-properties',
                                                       rel=['hea-properties']),
                                                Action(name='heaserver-volumes-volume-get-open-choices',
                                                       url='http://localhost:8080/volumes/{id}/opener',
                                                       rel=['hea-opener-choices']),
                                                Action(name='heaserver-volumes-volume-duplicate',
                                                       url='http://localhost:8080/volumes/{id}/duplicator',
                                                       rel=['hea-duplicator'])
                                                ],
                                   get_all_actions=[Action(name='heaserver-volumes-volume-get-properties',
                                                           rel=['hea-properties']),
                                                    Action(name='heaserver-volumes-volume-get-open-choices',
                                                           url='http://localhost:8080/volumes/{id}/opener',
                                                           rel=['hea-opener-choices']),
                                                    Action(name='heaserver-volumes-volume-duplicate',
                                                           url='http://localhost:8080/volumes/{id}/duplicator',
                                                           rel=['hea-duplicator'])],
                                   expected_opener=Link(
                                       url=f'http://localhost:8080/volumes/{db_store[service.MONGODB_VOLUME_COLLECTION][0]["id"]}/content',
                                       rel=['hea-opener', 'hea-default', 'application/x.folder']),
                                   duplicate_action_name='heaserver-volumes-volume-duplicate-form',
                                   registry_docker_image=RealRegistryContainerConfig(HEASERVER_REGISTRY_IMAGE),
                                   put_content_status=405)

FileSystemTestCase = get_test_case_cls(coll=service.MONGODB_FILE_SYSTEM_COLLECTION,
                                       wstl_package=service.__package__,
                                       href='http://localhost:8080/filesystems',
                                       db_manager_cls=DockerMongoManager,
                                       fixtures=db_store,
                                       get_actions=[
                                           Action(name='heaserver-volumes-file-system-get-properties',
                                                  rel=['hea-properties']),
                                           Action(name='heaserver-volumes-file-system-duplicate',
                                                  url='http://localhost:8080/filesystems/{id}/duplicator',
                                                  rel=['hea-duplicator'])
                                       ],
                                       get_all_actions=[
                                           Action(name='heaserver-volumes-file-system-get-properties',
                                                  rel=['hea-properties']),
                                           Action(name='heaserver-volumes-file-system-duplicate',
                                                  url='http://localhost:8080/filesystems/{id}/duplicator',
                                                  rel=['hea-duplicator'])],
                                       duplicate_action_name='heaserver-volumes-file-system-duplicate-form',
                                       put_content_status=404)
