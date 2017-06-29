=====
Kaira
=====

blablabla blabla blablabla blabla::

    from kaira.app import App
    from kaira.response import response


    app = App()


    @app.route("/")
    def hello_world(request):
        return response.text('Hello World!')

    if __name__ == '__main__':
        app.run(host="0.0.0.0", port=8000)

(Note the double-colon and 4-space indent formatting above.)

Paragraphs are separated by blank lines. *Italics*, **bold**,
and ``monospace`` look like this.


A Section
=========

Lists look like this:

* First

* Second. Can be multiple lines
  but must be indented properly.

A Sub-Section
-------------

Numbered lists look like you'd expect:

1. hi there

2. must be going

Urls are http://like.this and links can be
written `like this <http://www.example.com/foo/bar>`_.