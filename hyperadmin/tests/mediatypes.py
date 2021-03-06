from django.utils import unittest
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.test.client import RequestFactory, FakePayload
from django.utils import simplejson as json

from hyperadmin.mediatypes.collectionjson import CollectionJSON, CollectionNextJSON
from hyperadmin.views import ResourceViewMixin
from hyperadmin.resources import SiteResource, ApplicationResource
from hyperadmin.sites import site

class MockResourceView(ResourceViewMixin):
    def __init__(self, items=[], content_type='application/vnd.Collection+JSON'):
        self.items = items
        self.content_type = content_type
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        ResourceViewMixin.__init__(self)
    
    def get_items(self, **kwargs):
        return self.items
    
    def get_content_type(self):
        return self.content_type
    
    def get_form_class(self, **kwargs):
        class GenForm(forms.ModelForm):
            class Meta:
                model = ContentType
        return GenForm
    
    def get_instance_url(self, instance):
        return None
    
    def get_embedded_links(self, instance=None):
        return []
    
    def get_outbound_links(self, instance=None):
        return []
    
    def get_templated_queries(self):
        return []
    
    def get_ln_links(self, instance=None):
        return []
    
    def get_li_links(self, instance=None):
        return []

class CollectionJsonTestCase(unittest.TestCase):
    def test_queryset_serialize(self):
        items = ContentType.objects.all()
        view = MockResourceView(items)
        adaptor = CollectionJSON(view)
        response = adaptor.serialize(content_type='application/vnd.Collection.next+JSON')
        data = json.loads(response.content)
        json_items = data['collection']['items']
        self.assertEqual(len(json_items), len(items))
    
    def test_model_instance_serialize(self):
        items = [ContentType.objects.all()[0]]
        view = MockResourceView(items)
        adaptor = CollectionJSON(view)
        response = adaptor.serialize(instance=items[0], content_type='application/vnd.Collection.next+JSON')
        data = json.loads(response.content)
        json_items = data['collection']['items']
        self.assertEqual(len(json_items), 1)
    
    def test_site_resource_serialize(self):
        site_resource = SiteResource(site=site)
        items = [site_resource]
        view = MockResourceView(items)
        adaptor = CollectionJSON(view)
        response = adaptor.serialize(content_type='application/vnd.Collection.next+JSON')
        data = json.loads(response.content)
        json_items = data['collection']['items']
        #assert False, str(json_items)
    
    def test_application_resource_serialize(self):
        app_resource = ApplicationResource(site=site, app_name='testapp')
        items = [app_resource]
        view = MockResourceView(items)
        adaptor = CollectionJSON(view)
        response = adaptor.serialize(content_type='application/vnd.Collection.next+JSON')
        data = json.loads(response.content)
        json_items = data['collection']['items']
        #assert False, str(json_items)
    
    def test_model_instance_deserialize(self):
        items = [ContentType.objects.all()[0]]
        payload = '''{"data":{}}'''
        view = MockResourceView(items)
        view.request = view.factory.post('/', **{'wsgi.input':FakePayload(payload), 'CONTENT_LENGTH':len(payload)})
        adaptor = CollectionJSON(view)
        data = adaptor.deserialize(form_class=view.get_form_class())
        #json_items = data['collection']['items']

class CollectionNextJsonTestCase(unittest.TestCase):
    def test_convert_field(self):
        view = MockResourceView([], content_type='application/vnd.Collection.next+JSON')
        form_class = view.get_form_class()
        form = form_class()
        fields = form.fields.items()
        name, field = fields[0]
        adaptor = CollectionNextJSON(view)
        field_r = adaptor.convert_field(field, name)
        self.assertEqual(field_r['required'], field.required)
    
    def test_convert_errors(self):
        view = MockResourceView([], content_type='application/vnd.Collection.next+JSON')
        form_class = view.get_form_class()
        form = form_class(data={})
        assert form.errors
        adaptor = CollectionNextJSON(view)
        error_r = adaptor.convert_errors(form.errors)
        self.assertEqual(len(error_r['messages']), len(form.errors))
        

