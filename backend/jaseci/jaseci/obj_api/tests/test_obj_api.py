from django.contrib.auth import get_user_model
from django.urls import reverse

from core.utils.utils import TestCaseHelper

from rest_framework import status
from rest_framework.test import APIClient

from base.models import JaseciObject


NODE_URL = reverse('obj_api:jaseciobject-list')


class PublicNodeApiTests(TestCaseHelper):
    """Test the publicly available node API"""

    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def tearDown(self):
        super().tearDown()

    def test_login_required(self):
        """Test that login required for retrieving nodes"""
        res = self.client.get(NODE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateNodeApiTests(TestCaseHelper):
    """Test the authorized user node API"""

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            'JSCITfdfdEST_test@jaseci.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        super().tearDown()

    def test_retrieve_nodes(self):
        """Test retrieving node list"""
        JaseciObject.objects.create(user=self.user, name='Vegan')
        JaseciObject.objects.create(user=self.user, name='Dessert')

        res = self.client.get(NODE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_nodes_limited_to_user(self):
        """Test that nodes returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'JSCITEST_other@jaseci.com',
            'testpass'
        )
        JaseciObject.objects.create(user=user2, name='Fruity')
        node = JaseciObject.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(NODE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertEqual(res.data['results'][1]['name'], node.name)
        user2.delete()

    def test_create_node_successful(self):
        """Test creating a new node"""
        payload = {'name': 'Simple', 'j_type': 'node'}
        self.client.post(NODE_URL, payload)

        exists = JaseciObject.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)
