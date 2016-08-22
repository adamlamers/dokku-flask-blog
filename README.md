# Flask Dokku Blog

You can probably view a running example of this repository [here](http://blog.adamlamers.com)

This is a blog engine created with [Flask](http://flask.pocoo.org/) and
[Bulma](http://bulma.io). It uses [SimpleMDE](https://simplemde.com/) as a backend for editing, and
[highlightjs](https://highlightjs.org/) for source code highlighting in blog posts.

This repo is designed to work and be deployed with the [Dokku](http://dokku.io) docker tool.

Don't forget to change SECRET_KEY in config.py if you deploy this on your own server.

## Features

* GitHub flavored markdown in posts.
* Highlight.js on code blocks out of the box.
* Post tagging.
* idk

Installation with Dokku
------------------

1. Set up [dokku](http://dokku.viewdocs.io/dokku/getting-started/installation/) on a host
2. Create an app on that host
3. Create a [postgres service](https://github.com/dokku/dokku-postgres) with dokku and link it to the app you created
4. Push this app to your dokku host
5. Visit http://yourapp.com/init
6. Login with admin/password and change the password or create a new admin user and delete the
   default admin user.
