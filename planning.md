# Project Planning
Core idea: reading tracker and social media, 'Goodreads crossed with Reddit'.

## Semantic Layer
This is what I think could become the 'secret sauce' for this project. Consider a book, a chapter, an author, or a book series as possible 'objects'. By tying a room (forum/channel) to an object, we structure conversation around the topic. By using the structure of the objects, we can compose structure in the rooms.

## Tech Stack

Languages:
  - TypeScript frontend ([deno](https://deno.com/) runtime manager)
  - Python backend ([uv](https://docs.astral.sh/uv/) project manager)
  - XML document format (postgres supports [xml objects](https://www.postgresql.org/docs/9.1/datatype-xml.html))

### Standards

  + [XMPP](https://xmpp.org/) - Open communication standard
  + [OpenID](https://openid.net/developers/how-connect-works/) - Interoperable identity protocol for user authentication

### Backend

**Server Framework**
  + [FastAPI](https://fastapi.tiangolo.com/) - Type-hint driven API framework, better for modern python

**Database**
  + [Postgres](https://www.postgresql.org/) for relational database
    + [SQLAlchemy](https://www.sqlalchemy.org/) for python ORM layer

### Frontend

**UI Framework**
  + [React](https://react.dev/) - widely supported, but bloated OR

### Development

**Deployment**
  + [Docker](https://www.docker.com/) - Containers to run the application
  + [Nginx](https://nginx.org/) - HTTP Web server
  + [Granian](https://github.com/emmett-framework/granian) - Rust + Python HTTP server

**Development Tools**
  + [penpot](https://penpot.app/) - UI design platform (open source, self-host)
  + [redocly](https://redocly.com/) - Documentation generation


## Misc
Some other useful references.

  + [Open Library](https://openlibrary.org/about) - Internet Archive library project
    + [Data dumps](https://openlibrary.org/developers/dumps) - Open library TSV files with lots of data about books
  + [Twelve factor app](https://12factor.net/) - Good reference of best practices in application development and deployment
