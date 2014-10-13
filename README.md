usermanager
===========
A proof-of-concept user management service implementation.

Installing
==========
Just run:
```
pip install -r requirements.txt
```

Testing
=======
To test, run 'make test'

Understanding
=============
First, observe that I'm not using a real database, and that the USERS and
GROUPS are just big dictionaries in usermanager.py. Then, open usermanager.py
and test_usermanager.py, and start reading the tests. They have carefully 
selected function names and docstrings indicating what condition they're
intended to assert; it should be fairly easy to read them and understand how
they exercise the API.

I try to keep things as simple as possible, and in my first cut at things,
generally avoid factoring badly by factoring very little. Consequently,
usermanager.py is a big bag of functions. They are, at least, grouped together
by topic and they have sane names and documentation. Their use should be fairly
straightforward:

* underscore-named functions are internal methods related to managing the USERS
and GROUPS tables; with use of an ORM, all of these would be replaced by
manipulations of User and Group model objects.
* There is no Group class, because the interface on dicts is very thin, but one
could easily imagine a model object for Group and the User/Group many-to-many
association table.
* All of the flask api endpoints are grouped together, apart from the
pseudo-datastore implementation, and presented in the order given in the spec.
* I follow the XXX convention for items I know are ugly but I'm doing anyway
* I follow the FIXME convention for things I think really need to be repaired

Comments
========
I'm not really happy with how this version is factored, but the instructions
said to hard cap at eight hours, and it took me some time to teach myself the
basics of Flask. Once I had enough bootstrapped to write plausible unit tests,
though, things went pretty fast, and I'm fairly confident that another half
day's effort would get things factored into a nice shape, i.e.:

* User and Group should be encapsulated in objects
* The User and Group APIs should be encapsulated in objects, too. I dislike
having all the endpoint methods just laying around.
* If I spent even a little more time with it, I'd capture common idioms, like
the Response object creation with type application/json, and replace their uses
with a tiny function call to make return values tidier, like 
```return as_json(value)```. I'd similarly encapsulate the parameter passing
to the 404 pages.
* I think the spec is slightly wrong. I believe I was faithful to it, but I
think that DELETE against a group should not only empty it, it should also
remove the empty group reference. This may be considered an implementation
detail because the spec only specifies Users, not Groups. I suppose everything
could be implemented in terms of Users. If one wanted to go this way, one
could assume that there was a piece of middleware mediating and caching access
to a User's groups, essentially creating the Groups backward-index lazily. But
introduction of an ORM (as I suggest below) and relations would be less 
surprising and consequently better.
* Use of some kind of ORM in front of a real database or key/value store would
be nice. 8 hours wasnt't enough to teach myself SQLAlchemy too. This might push
the refactoring time closer to a full day, perhaps more if SQLAlchemy displays
surprising behavior.
