Changelog
=========

Release 16.3.0 (UNRELEASED)
---------------------------

Features
^^^^^^^^

- Full-text indexes can be used with new ``filter.TEXT()``
- Client authentication by X509 certificates. Use your client certificate when connecting
  to MongoDB and then call ``Database.authenticate`` with certificate subject as username,
  empty password and ``mechanism="MONGODB-X509"``.
- ``get_version()`` to approximate the behaviour of get_version in PyMongo. One noteable exception		
  is the omission of searching by random (unindexed) meta-data which should be considered a bad idea		
  as it may create *very* variable conditions in terms of loading and timing. An additional index is		
  also added to facilitate bi-directional movement between versions. Additional Unit test for GFS also added.

Release 16.2.0 (2016-10-02)
---------------------------

Features
^^^^^^^^

- ``Collection.bulk_write()`` that maches behavior of corresponding PyMongo's method. It accepts
  an iterable of ``InsertOne``, ``UpdateOne``, ... from ``pymongo.operations``, packs them into
  batches and returns aggregated response from MongoDB.
- ``codec_options`` properties for ``ConnectionPool``, ``Database`` and ``Collection``.
  ``Collection.with_options(codec_options=CodecOptions(document_class=...))`` is now preferred
  over ``Collection.find(..., as_class=...)``.
  
Bugfixes
^^^^^^^^

- Fixed bug in `find()` that can cause undefined ordering of the results when sorting on multiple fields is requested.

Release 16.1.0 (2016-06-15)
---------------------------

API Changes
^^^^^^^^^^^

- ``insert_many()`` raises ``BulkWriteError`` instead ``WriteError``/``DuplicateKeyError`` to
  match PyMongo's behavior. This is also allows to extract multiple duplicate key errors from
  exception object when ``insert_many`` is used with ``ordered=False``.
- ``fields`` parameter removed for ``Collection.count()``.
- ``ConnectionPool`` has two new parameters: ``watchdog_interval`` which is how many seconds before
  testing a connection to see if it is stale, and ``watchdog_timeout``is how long the check takes
  before dropping the stale connection and try to reconnect.

Features
^^^^^^^^

- Stale connections are now dropped after failing to contact mongodb longer than ``watchdog_timeout``.
- ``insert_many()`` is now able to insert more than 1000 documents and more than 16Mb of documents at once.
- GridFS's default ``chunkSize`` changed to 255kB, to avoid the overhead with usePowerOf2Sizes option.
- Add ``GridFS.indexes_created`` to obtain a defer on the creation of the current
  GridFS instance's indexes
- GridFS create indexes for the ``files`` collection in addition to the ``chunks`` one

Release 16.0.1 (2016-03-03)
---------------------------

Features
^^^^^^^^

- Make existing logging more verbose, indicate that it is TxMongo raising the error or sending the message.
- Add additional logging.

Release 16.0.0 (2016-02-25)
---------------------------

Bugfixes
^^^^^^^^

- Memory leak fixed in `find_with_cursor` that affected almost all query methods


Release 15.3.1 (2015-10-26)
---------------------------

API Changes
^^^^^^^^^^^

- ``connection.ConnectionPool`` exposes `max_delay` which is used to set the maximum number of
  seconds between connection attempts. The default is set to 60.

Features
^^^^^^^^

- Updated and simplified setup.py, enforce minimal versions of PyMongo and Twisted necessary to
  install TxMongo.


Release 15.3.0 (2015-09-29)
---------------------------

API Changes
^^^^^^^^^^^

- ``NotMaster`` instead of ``AutoReconnect`` error will be returned when a call can be safely
  retried.

Features
^^^^^^^^

- Added ``deadline`` to ``collection`` methods, this will raise a ``DeadlineExceeded`` when the
  deadline, a unix timestamp in seconds, is exceeded. This happens only in methods with
  ``getprotocol()`` and methods that reference them.
- Added ``timeout`` to ``collection`` methods, this will raise a ``TimeoutExceeded`` when the
  timeout, in seconds, is exceeded. This happens only in methods with ``getprotocol()`` and methods that
  reference them.

Bugfixes
^^^^^^^^

- Fixed ``collection.count()`` to return an int instead of float, this matches how count
  in with PyMongo.


Release 15.2.2 (2015-09-15)
---------------------------

Bugfix release to handle str assert that wasn't passing unicode properly in
python 2.6, used Twisted compat library StringType.


Release 15.2.1 (2015-09-07)
---------------------------

Bugfix release to handle uncaught exceptions in logging and to remove support
for python 2.6 and since it was removed in latest Twisted.


Release 15.2 (2015-09-05)
-------------------------

This release makes TxMongo fully Python3 compatible and has an API change that
breaks older TxMongo compatibility by bringing it inline with PyMongo.

API Changes
^^^^^^^^^^^

- ``txmongo.dbref`` removed. Use ``bson.dbref`` instead.
  **Incompatibility note:** ``bson.dbref.DBRef`` takes collection name as string while
  ``txmongo.dbref.DBRef`` was able to accept ``Collection`` instance. Please use
  ``collection.name`` instead.
- Added ``timeout`` parameter for ``connection.ConnectionPool`` that can passed on to
  Twisted's ``connectTCP`` and ``connectSSL`` methods.

Features
^^^^^^^^

- ``name``, ``full_name`` and ``database`` properties of ``Collection``
- Python3 compatible.


Release 15.1 (2015-06-08)
-------------------------

This is a major release in that while increasing code coverage to 95%
( see https://coveralls.io/builds/2749499 ), we've also caught several
bugs, added features and changed functionality to be more inline with PyMongo.

This is no small thanks to travis-ci and coveralls while using tox to cover all iterations
that we support.

We can officially say that we are Python 2.6, 2.7 and PyPy compatible.

API Changes
^^^^^^^^^^^

- **TxMongo now requires PyMongo 3.x**, if you need PyMongo 2.x support, please use 15.0, otherwise
  it is highgly recommend to use PyMongo 3.x which still support MongoDB 2.6.
- Better handling of replica-sets, we now raise an ``autoreconnect`` when master is unreachable.
- Changed the behaviour of ``find_one`` to return ``None`` instead of an empty
  dict ``{}`` when no result is found.
- New-style query methods: ``insert_one/many``, ``update_one/many``, ``delete_one/many``,
  ``replace_one`` and ``find_one_and_update/replace``

Features
^^^^^^^^

- Added ``db.command`` function, just like PyMongo.
- Added support for named indexes in ``filter``.
- ``insert()``, ``update()``, ``save()`` and ``remove()`` now support write-concern options via
  named args: ``w``, ``wtimeout``, ``j``, ``fsync``. ``safe`` argument is still supported for
  backward compatibility.
- Default write-concern can be specified for ``Connection`` using named arguments in constructor
  or by URI options.
- Write-concern options can also be set for ``Database`` and ``Collection`` with ``write_concern``
  named argument of their constructors. In this case write-concern is specified by instance of
  ``pymongo.write_concern.WriteConcern``
- ``txmongo.protocol.INSERT_CONTINUE_ON_ERROR`` flag defined for using with ``insert()``
- Replaced all traditional deferred callbacks (and errbacks) to use @defer.inlineCallbacks

Bugfixes
^^^^^^^^

- Fixed typo in ``map_reduce()`` when returning results.
- Fixed hang in ``create_collection()`` in case of error.
- Fixed typo in ``rename()`` that wasn't using the right factory.
- Fixed exception in ``drop_index`` that was being thrown when dropping a non-existent collection.
  This makes the function idempotent.
- Fixed URI prefixing when "mongodb://" is not present in URI string in ``connection``.
- Fixed fail-over when using replica-sets in ``connection``.  It now raises ``autoreconnect`` when
  there is a problem with the existing master. It is then up to the client code to reconnect to the
  new master.
- Fixed number of cursors in protocol so that it works with py2.6, py2.6 and pypy.


Release 15.0 (2015-05-04)
-------------------------

This is the first release using the Twisted versioning method.

API Changes
^^^^^^^^^^^

- ``collections.index_information`` now mirrors PyMongo's method.
- ``getrequestid`` is now ``get_request_id``

Features
^^^^^^^^

- Add support for 2dsphere indexes, see http://docs.mongodb.org/manual/tutorial/build-a-2dsphere-index/
- PEP8 across files as we work through them.
- Authentication reimplemented for ConnectionPool support with multiple DBs.
- Add support for MongoDB 3.0

Bugfixes
^^^^^^^^

- Fixed failing tests due to changes in Python in 2.6
- Fixed limit not being respected, which should help performance.
- Find now closes MongoDB cursors.
- Fixed 'hint' filter to correctly serialize with double dollar signs.


Improved Documentation
^^^^^^^^^^^^^^^^^^^^^^

- Added, updated and reworked documentation using Sphinx.
- The documentation is now hosted on https://txmongo.readthedocs.org/.


Release 0.6 (2015-01-23)
------------------------

This is the last release in this version scheme, we'll be switching to the Twisted version scheme in the next release.

API Changes
^^^^^^^^^^^

- TxMongo: None

Features
^^^^^^^^

- Added SSL support using Twisted SSLContext factory
- Added "find with cursor" like pymongo
- Test coverage is now measured. We're currently at around 78%.

Bugfixes
^^^^^^^^

- Fixed import in database.py


Release 0.5 (2014-10-02)
------------------------

Code review and cleanup


Bugfixes
^^^^^^^^

- Bug fixes


Release 0.4 (2013-01-07)
------------------------

Significant performance improvements.

API Changes
^^^^^^^^^^^

- TxMongo: None

Features
^^^^^^^^

- Support AutoReconnect to connect to fail-over master.
- Use pymongo instead of in-tree copy.

Bugfixes
^^^^^^^^

- Bug fixes

Release 0.3 (2010-09-13)
------------------------

Initial release.

License
^^^^^^^

- Apache 2.0
