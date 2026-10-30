# Task 3 - viva questions and answers

**Task 3 - Requirements, Architecture and Technology Setup**

Source: section G of [task-03-requirements-architecture-and-setup.md](../../task-03-requirements-architecture-and-setup.md) - answers checked against the
repository and the evidence in this project.

1. **What is an SRS?** A Software Requirements Specification: what the system
   must do (functional) and qualities it must have (non-functional).
2. **Explain your layers.** Controllers handle HTTP, services hold business
   rules, DAOs hold all SQL, models are plain data. Each only calls the layer below.
3. **Why separate services from controllers?** Rules can be unit-tested
   without a web request, and they are not duplicated in several routes.
4. **Why SQLite?** Built into Python, zero setup, one file; enough for one
   hotel. Limitation: one writer at a time and one server only.
5. **How do you prevent double bookings?** Three layers: the service checks;
   the DAO checks and inserts inside `BEGIN IMMEDIATE` (a locked transaction);
   and database triggers refuse overlaps. A 10-thread test proves only one wins.
6. **(Project-specific) What does `/health` return and who uses it?**
   `{"status","env","version","commit"}`; used by the Docker HEALTHCHECK,
   the Jenkins health-check stage and the Ansible playbook.
7. **(Project-specific) Why can't another user cancel my booking?**
   `BookingService.get_booking` checks the owner and raises "not found"
   otherwise, so the route returns 404 - proven by an integration test.
8. **Is pip your Maven?** No. pip installs Python packages and pytest runs
   tests; they do the same jobs as Maven's dependency and test phases, but they
   are different tools. I need the professor's confirmation that this is acceptable.
9. **Why Gunicorn and Nginx instead of Tomcat?** Tomcat runs Java servlets.
   Python apps run on a WSGI server (Gunicorn); Nginx is the public entry
   point and serves static files.
10. **What is the booking state machine?** PENDING -> CONFIRMED, PENDING or
    CONFIRMED -> CANCELLED; nothing else. Status changes use
    `UPDATE ... WHERE status IN (allowed)` so check and change happen atomically.
11. **What is CSRF and how do you stop it?** Cross-Site Request Forgery: another
    site making your browser submit our forms. Every form has a secret token
    stored in the session; POSTs without it get HTTP 400.

## Extra questions that match this demonstration

1. **Is Maven or Tomcat used in this project?**
   No. They are Java tools; this is a Python project. The equivalents are requirements.txt for dependencies, pytest for tests, and Gunicorn behind Nginx for serving. The project document says plainly that if Maven or Tomcat is mandatory rather than an example in the course brief, that needs the professor's confirmation. This is the one open item of Task 3.
