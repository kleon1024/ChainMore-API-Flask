from flask import current_app

from tests.base import BaseTestCase


class CertifyTestCase(BaseTestCase):

    def test_certification_group(self):
        self.login()
        domain_id = 1
        d = self.OK(self.post('/v1/domain/group',
                    json=dict(
                         domain=domain_id,
                         title='test',
                         intro='sha256'
                         )))
        self.assertEqual(d['items'][0]['domain_id'], 1)
        self.assertEqual(d['items'][0]['title'], 'test')
        self.assertEqual(d['items'][0]['intro'], 'sha256')
        group_id = d['items'][0]['id']

        d = self.OK(self.post('/v1/domain/mcp',
                              json=dict(
                                  text='Question Body',
                                  type='multiple_answer',
                              )))
        self.assertEqual(d['items'][0]['text'], 'Question Body')
        self.assertEqual(d['items'][0]['type'], 'multiple_answer')
        mcp = d
        mcp_id = d['items'][0]['id']

        d = self.OK(self.post('/v1/domain/mcp/choice',
                              json=dict(
                                  text='Choice Desc',
                                  mcp=mcp_id,
                                  answer=False
                              )))
        self.assertEqual(d['items'][0]['text'], 'Choice Desc')

        c1 = d
        c1_id = d['items'][0]['id']

        d = self.OK(self.post('/v1/domain/mcp/choice',
                               json=dict(
                                    text='Answer',
                                    mcp=mcp_id,
                                    answer=True
                               )))

        self.assertEqual(d['items'][0]['text'], 'Answer')

        c2 = d
        c2_id = d['items'][0]['id']

        d = self.OK(self.get('/v1/domain/mcp/choices',
                    query_string=dict(
                        id=mcp_id
                    )))
        self.assertEqual(len(d['items']), 2)
        self.assertTrue(d['items'][0]['id'] in [c1_id, c2_id])
        self.assertTrue(d['items'][1]['id'] in [c1_id, c2_id])

        d = self.OK(self.post('/v1/domain/certification',
                              json=dict(
                                  digest='sha256',
                                  group=group_id,
                                  type='multiple_choice_problem',
                                  mcp=mcp_id,
                              )))

        self.assertEqual(d['items'][0]['digest'], 'sha256')
        self.assertEqual(d['items'][0]['type'], 'multiple_choice_problem')
        self.assertEqual(d['items'][0]['mcp_id'], mcp_id)

        d = self.OK(self.get('/v1/domain/groups',
                              query_string=dict(
                                  id=domain_id
                              )))
        self.assertEqual(len(d['items']), 1)
        self.assertEqual(d['items'][0]['finished'], False)
        group_id = d['items'][0]['id']

        d = self.OK(self.get('/v1/domain/certifications',
                    query_string=dict(
                        id=group_id
                    )))
        
        self.format(d['items'])