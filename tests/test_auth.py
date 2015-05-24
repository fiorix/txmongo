# coding: utf-8
# Copyright 2015 Ilya Skriblovsky <ilyaskriblovsky@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import txmongo
from bson.son import SON
from pymongo.errors import OperationFailure
from twisted.trial import unittest
from twisted.internet import base, defer

from txmongo.protocol import MongoAuthenticationError

from mongod import Mongod


base.DelayedCall.debug = True

mongo_host = "localhost"
mongo_port = 27018
mongo_uri = "mongodb://{0}:{1}/".format(mongo_host, mongo_port)


class TestMongoAuth(unittest.TestCase):
    """
    NB: This testcase requires:
        * auth=true in MongoDB configuration file
        * no configured users
        * localhost exception enabled (this is default)
    """

    db1 = "authtest1"
    db2 = "authtest2"
    coll = "mycol"

    login1 = "user1"
    password1 = "pwd1"

    login2 = "user2"
    password2 = "pwd2"

    ua_login = "useradmin"
    ua_password = "useradminpwd"

    def __get_connection(self, pool_size=1):
        return txmongo.connection.ConnectionPool(mongo_uri, pool_size)

    @defer.inlineCallbacks
    def createUserAdmin(self):
        conn = self.__get_connection()

        try:
            r = yield conn.admin.command("createUser", self.ua_login,
                                         pwd=self.ua_password,
                                         roles=[{"role": "userAdminAnyDatabase",
                                                 "db": "admin"}])

            try:
                # This should fail if authentication enabled in MongoDB since
                # we've created user but didn't authenticated
                yield conn[self.db1][self.coll].find_one()

                yield conn.admin.command("dropUser", self.ua_login)
                raise unittest.SkipTest("Authentication tests require authorization enabled "
                                        "in MongoDB configuration file")
            except OperationFailure:
                pass
        finally:
            yield conn.disconnect()

    @defer.inlineCallbacks
    def createDBUsers(self):
        conn = self.__get_connection()
        yield conn["admin"].authenticate(self.ua_login, self.ua_password)

        yield conn[self.db1].command("createUser", self.login1,
                                     pwd=self.password1,
                                     roles=[{"role": "readWrite",
                                             "db": self.db1}])

        yield conn[self.db2].command("createUser", self.login2,
                                    pwd=self.password2,
                                    roles=[{"role": "readWrite",
                                            "db": self.db2}])

        yield conn.disconnect()

    @defer.inlineCallbacks
    def setUp(self):
        self.__mongod = Mongod(port=mongo_port, auth=True)
        yield self.__mongod.start()

        yield self.createUserAdmin()
        yield self.createDBUsers()

    @defer.inlineCallbacks
    def tearDown(self):
        try:
            conn = self.__get_connection()
            yield conn["admin"].authenticate(self.ua_login, self.ua_password)
            yield conn[self.db1].authenticate(self.login1, self.password1)
            yield conn[self.db2].authenticate(self.login2, self.password2)

            yield conn[self.db1][self.coll].drop()
            yield conn[self.db2][self.coll].drop()
            yield conn[self.db1].command("dropUser", self.login1)
            yield conn[self.db2].command("dropUser", self.login2)
            yield conn["admin"].command("dropUser", self.ua_login)
            yield conn.disconnect()
        finally:
            yield self.__mongod.stop()

    @defer.inlineCallbacks
    def test_AuthConnectionPool(self):
        pool_size = 2

        conn = self.__get_connection(pool_size)
        db = conn[self.db1]
        coll = db[self.coll]

        try:
            yield db.authenticate(self.login1, self.password1)

            n = pool_size + 1

            yield defer.gatherResults([coll.insert({'x': 42}) for _ in range(n)])

            cnt = yield coll.count()
            self.assertEqual(cnt, n)
        finally:
            yield conn.disconnect()

    @defer.inlineCallbacks
    def test_AuthConnectionPoolUri(self):
        pool_size = 5

        conn = txmongo.connection.ConnectionPool(
            "mongodb://{0}:{1}@{2}:{3}/{4}".format(self.login1, self.password1, mongo_host,
                                                   mongo_port, self.db1)
        )
        db = conn.get_default_database()
        coll = db[self.coll]

        n = pool_size + 1

        try:
            yield defer.gatherResults([coll.insert({'x': 42}) for _ in range(n)])

            cnt = yield coll.count()
            self.assertEqual(cnt, n)
        finally:
            yield conn.disconnect()

    @defer.inlineCallbacks
    def test_AuthFailAtStartup(self):
        conn = self.__get_connection()
        db = conn[self.db1]

        try:
            db.authenticate(self.login1, self.password1 + 'x')
            yield self.assertFailure(conn[self.db1][self.coll].find_one(), OperationFailure)
        finally:
            yield conn.disconnect()

    @defer.inlineCallbacks
    def test_AuthFailAtRuntime(self):
        conn = self.__get_connection()
        db = conn[self.db1]

        try:
            yield self.assertFailure(conn[self.db1][self.coll].find_one(), OperationFailure)
            yield self.assertFailure(db.authenticate(self.login1, self.password1 + 'x'),
                                     MongoAuthenticationError)
            yield self.assertFailure(conn[self.db1][self.coll].find_one(), OperationFailure)
        finally:
            yield conn.disconnect()

    @defer.inlineCallbacks
    def test_AuthOnTwoDBsParallel(self):
        conn = self.__get_connection()

        try:
            yield self.assertFailure(conn[self.db1][self.coll].find_one(), OperationFailure)

            yield defer.gatherResults([
                conn[self.db1].authenticate(self.login1, self.password1),
                conn[self.db2].authenticate(self.login2, self.password2),
            ])

            yield defer.gatherResults([
                conn[self.db1][self.coll].insert({'x': 42}),
                conn[self.db2][self.coll].insert({'x': 42}),
            ])
        finally:
            yield conn.disconnect()

    @defer.inlineCallbacks
    def test_AuthOnTwoDBsSequential(self):
        conn = self.__get_connection()

        try:
            yield self.assertFailure(conn[self.db1][self.coll].find_one(), OperationFailure)

            yield conn[self.db1].authenticate(self.login1, self.password1)
            yield conn[self.db1][self.coll].find_one()

            yield conn[self.db2].authenticate(self.login2, self.password2)
            yield conn[self.db2][self.coll].find_one()
        finally:
            yield conn.disconnect()
