from __future__ import unicode_literals

from pyramid.security import Allow
from pyramid.security import Deny
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.security import ALL_PERMISSIONS
from pyramid.httpexceptions import HTTPNotFound


class BaseResource(object):
    def __init__(self, request, parent=None, name=None):
        self.__name__ = name
        self.__parent__ = parent
        self.request = request


class IndexResource(BaseResource):
    __acl__ = [
        #       principal      action
        (Allow, Authenticated, 'view'),
        (Allow, Authenticated, 'create'),
    ]

    #: the class of model
    MODEL_CLS = None

    #: entity name
    ENTITY_NAME = None

    #: entity resource
    ENTITY_RESOURCE = None

    def __init__(self, request, parent=None, name=None):
        super(IndexResource, self).__init__(request, parent, name)
        assert self.MODEL_CLS is not None
        assert self.ENTITY_NAME is not None
        assert self.ENTITY_RESOURCE is not None

    def __getitem__(self, key):
        model = self.MODEL_CLS(self.request.model_factory)
        entity = model.get(key)
        if entity is None:
            raise HTTPNotFound('No such {} {}'.format(self.ENTITY_NAME, key))
        return self.ENTITY_RESOURCE(self.request, entity, parent=self, name=key)


class EntityResource(BaseResource):

    def __init__(self, request, entity, parent=None, name=None):
        super(EntityResource, self).__init__(request, parent, name)
        self.entity = entity
        # make sure only the owner company can access the entity
        company_principal = 'company:{}'.format(self.company.guid)
        self.__acl__ = [
            #       principal, action
            (Allow, company_principal, 'view'),
            # Notice: denying Everyone principal makes sure we won't
            # allow user to access resource of other company via parent's
            # ACL
            (Deny, Everyone, ALL_PERMISSIONS),
        ]

    @property
    def company(self):
        raise NotImplemented()


class URLMapResource(BaseResource):

    def __init__(self, request, url_map, parent=None, name=None):
        super(URLMapResource, self).__init__(request, parent, name)
        self.url_map = url_map

    def __getitem__(self, item):
        return self.url_map.get(item)
