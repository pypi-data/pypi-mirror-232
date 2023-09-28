from aldryn_forms.models import FormPlugin
from cms.api import add_plugin, create_page
from cms.test_utils.testcases import CMSTestCase
from djangocms_oidc.constants import DJANGOCMS_USER_SESSION_KEY


class TestOIDCFormPlugin(CMSTestCase):

    def setUp(self):
        self.page = create_page('test page', 'test_page.html', 'en', published=True, apphook='FormsApp')
        self.placeholder = self.page.placeholders.get(slot='content')

    def test_get_with_session(self):
        form_plugin = add_plugin(self.placeholder, 'OIDCFormPlugin', 'en')
        add_plugin(self.placeholder, 'OIDCTextField', 'en', name='name', target=form_plugin,
                   unmodifiable=False, oidc_attributes='name')
        add_plugin(self.placeholder, 'OIDCEmailField', 'en', name='email', oidc_attributes='email', required=True,
                   target=form_plugin)
        add_plugin(self.placeholder, 'BooleanField', 'en', name='student', target=form_plugin)
        add_plugin(self.placeholder, 'OIDCBooleanField', 'en', name='validated', target=form_plugin,
                   oidc_attributes='validated')
        add_plugin(self.placeholder, 'OIDCTextAreaField', 'en', name='address', target=form_plugin,
                   oidc_attributes='address')

        self.page.publish('en')

        session = self.client.session
        session[DJANGOCMS_USER_SESSION_KEY] = {
            'email': 'mail@foo.foo',
            'name': 'Tester',
            'validated': True,
            'address': {'formatted': 'Street 42\n123 00 City'}
        }
        session.save()

        response = self.client.get(self.page.get_absolute_url('en'))

        self.assertContains(
            response,
            """<input type="email" name="email" value="mail@foo.foo" class="" required disabled id="id_email">""",
            html=True)
        self.assertContains(
            response,
            """<input type="text" name="name" value="Tester" class="" id="id_name">""",
            html=True)
        self.assertContains(
            response, """<input type="checkbox" name="student" class="" id="id_student">""", html=True)
        self.assertContains(
            response,
            """<input type="checkbox" name="validated" value="True" class="" disabled id="id_validated" checked>""",
            html=True)
        self.assertContains(
            response, """
                <textarea name="address" type="text" class="" disabled id="id_address">
                    Street 42
                    123 00 City
                </textarea>""", html=True)

    def test_get_without_session(self):
        form_plugin = add_plugin(self.placeholder, 'OIDCFormPlugin', 'en')
        add_plugin(self.placeholder, 'OIDCTextField', 'en', name='name', required=True, target=form_plugin)
        add_plugin(self.placeholder, 'OIDCEmailField', 'en', name='email', required=True, target=form_plugin,
                   oidc_attributes='email')
        self.page.publish('en')
        response = self.client.get(self.page.get_absolute_url('en'))
        self.assertContains(
            response, """<input type="text" name="name" class="" required disabled id="id_name">""", html=True)
        self.assertContains(
            response, """<input type="email" name="email" class="" required disabled id="id_email">""", html=True)

    def test_post(self):
        form_plugin = add_plugin(self.placeholder, 'OIDCFormPlugin', 'en')
        add_plugin(self.placeholder, 'OIDCEmailField', 'en', name='email', required=True, target=form_plugin,
                   oidc_attributes='email')

        self.page.publish('en')
        aldryn_form = FormPlugin.objects.last()
        session = self.client.session
        session[DJANGOCMS_USER_SESSION_KEY] = {
            'email': 'mail@foo.foo',
        }
        session.save()

        response = self.client.post(self.page.get_absolute_url('en'), {
            "form_plugin_id": aldryn_form.pk,
            "email": "tester@foo.foo"
        })
        self.assertContains(response, "Thank you for submitting your information.")

    def test_post_invalid(self):
        form_plugin = add_plugin(self.placeholder, 'OIDCFormPlugin', 'en')
        add_plugin(self.placeholder, 'OIDCEmailField', 'en', name='email', required=True, target=form_plugin,
                   oidc_attributes='email')

        self.page.publish('en')
        aldryn_form = FormPlugin.objects.last()

        response = self.client.post(self.page.get_absolute_url('en'), {
            "form_plugin_id": aldryn_form.pk,
            "email": "tester@foo.foo"
        })
        self.assertEqual(response.context['form'].errors, {'email': ['This field is required.']})
