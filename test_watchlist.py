import unittest
# from hello import sayhello

# class SayHelloTestCase(unittest.TestCase):
#     def setUp(self):
#         pass
#     def tearDown(self):
#         pass
#     def test_sayhello(self):
#         rv = sayhello()
#         self.assertEqual(rv,'Hello!')
#     def test_sayhello_to_somebody(self):
#         rv = sayhello('Wenjun')
#         self.assertEqual(rv,'Hello, Wenjun!')
# if __name__=='__main__':
#     unittest.main()
from app import app , db, Movie, User, forge, initdb

class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        app.app_context().push()    
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        
        db.create_all()
        user = User(name='Test', username='test')
        user.set_password('123')
        movie = Movie(title='Test Movie Title',year='2019')
        db.session.add_all([user,movie])
        db.session.commit()
        self.client=app.test_client()
        self.runner = app.test_cli_runner()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    def test_app_exist(self):
        self.assertIsNotNone(app)
    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])        
    def test_404_case(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code,404)
    
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist',data)
        self.assertIn('Test Movie Title',data)
        self.assertEqual(response.status_code,200)    
    def login(self):
        self.client.post('/login',data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
    def test_create_item(self):
        self.login()
        response = self.client.post('/',data=dict(
            title='New Movie',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created',data)
        self.assertIn('New Movie',data)
        # 测试创建条目操作，但电影名字为空
        response = self.client.post('/',data=dict(
            title='',
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

        # 测试创建条目操作，但电影年份为空
        response = self.client.post('/', data=dict(
            title='New Movie',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)
        
    def test_update_item(self):
        self.login()
        # test edit page
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie Title',data)
        self.assertIn('2019',data)
        
        # test edit update function
        response = self.client.post('/movie/edit/1',data=dict(
            title='New Movie Edited',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.',data)
        self.assertIn('New Movie Edited',data)
        
        response = self.client.post('/movie/edit/1', data=dict(
            title='',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.',data)
        self.assertIn('Invalid input.',data)
    def test_delete_item(self):
        self.login()
        
        response = self.client.post('/movie/delete/1',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.',data)
        self.assertNotIn('Test Movie Title',data)
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout',data)
        self.assertNotIn('Setting',data)
        self.assertNotIn('<from method="post">',data)
        self.assertNotIn('Delete',data)
        self.assertNotIn('Edit',data)
    def test_login(self):
        response = self.client.post('/login',data=dict(
            username='test',
            password='123'
        ), follow_redirects = True)
        data = response.get_data(as_text=True)
        self.assertIn('Login Success.', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)
        
        response = self.client.post('/login', data=dict(
        username='test',
        password='456'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 测试使用错误的用户名登录
        response = self.client.post('/login', data=dict(
            username='wrong',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 测试使用空用户名登录
        response = self.client.post('/login', data=dict(
            username='',
            password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)

        # 测试使用空密码登录
        response = self.client.post('/login', data=dict(
            username='test',
            password=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid input.', data)
    def test_settings(self):
        self.login()
        # test settings page
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings',data)
        self.assertIn('Your Name',data)
        
        #test updating settings
        
        response = self.client.post('/settings',data=dict(
            name='Wenjun Zhang'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated.',data)
        self.assertIn('Wenjun Zhang',data)
        
        # test updating settings, set name to empty
        response = self.client.post('/settings', data=dict(
            name='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated.', data)
        self.assertIn('Invalid input.', data)
    # test fake data
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done.', result.output)        
        self.assertNotEqual(Movie.query.count(), 0)
    # test initdb
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)
    # test generating admin account 
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result=self.runner.invoke(args=['admin','--username','wenjun','--password','123'])
        self.assertIn('Creating User...',result.output)
        self.assertIn('Done.',result.output)
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username,'wenjun')
        self.assertTrue(User.query.first().validate_password('123'))
        
    def test_admin_command_update(self):
        # use args to provide full command arguments
        result = self.runner.invoke(args=['admin', '--username', 'peter', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'peter')
        self.assertTrue(User.query.first().validate_password('456'))
if __name__=='__main__':
    unittest.main()