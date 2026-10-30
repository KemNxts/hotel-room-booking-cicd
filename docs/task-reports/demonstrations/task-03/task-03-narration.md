# Task 3 - narration script

**Task 3 - Requirements, Architecture and Technology Setup**

Read this aloud (or let the video's voice-over do it). The voice-over in the video is a
synthetic Windows text-to-speech voice, not a human recording. Each step has the four
parts: what I am doing, why, what the output means, and one sentence for the professor.

## Step 1 - SRS summary: requirements mapped to code [video 00:01]

**What I am doing:** running

```powershell
Select-String -Path docs/03-srs-architecture.md -Pattern '^\| FR' | ForEach-Object { $p = $_.Line -split '\|'; $p[1].Trim() + '  ' + $p[3].Trim() }
```

**Spoken script (as in the video):**

> This is Task 3, requirements, architecture and technology setup. The Software Requirements Specification, or SRS, lists what the system must do. There are eleven functional requirements, FR one to FR eleven. Here I print each requirement number next to the exact code that implements it, for example FR three, showing room availability, is implemented in BookingService dot search rooms.

**What the output means:** FR1 to FR11, each followed by the class or file that implements it.

**What I will tell the professor:** "Every requirement points to the code that implements it, so I can trace it."

## Step 2 - Use-case diagram [video 00:32]

**What I am doing:** running

```powershell
Get-Content docs/03-srs-architecture.md | Select-Object -Skip 34 -First 22
```

**Spoken script (as in the video):**

> A use case diagram shows who uses the system and what they can do. This is the source of the diagram. The guest has six use cases, the six booking features. The developer pushes a commit that starts the pipeline, and the operator deploys and rolls back a release. On GitHub this text is drawn as a picture.

**What the output means:** Mermaid diagram source with three actors: Guest, Developer, Operator, linked to nine use cases.

**What I will tell the professor:** "Three kinds of people use the system: guests, developers and operators."

## Step 3 - Architecture diagram [video 00:57]

**What I am doing:** running

```powershell
Get-Content docs/03-srs-architecture.md | Select-Object -Skip 59 -First 17
```

**Spoken script (as in the video):**

> This is the architecture. A request comes from the browser to Nginx, then Gunicorn, then our Flask app. Inside Flask there are layers: controllers handle web requests, services hold business rules, DAOs, which means data access objects, are the only place with SQL, and models hold the data. At the bottom is the SQLite file. The rules of the layers are written below the diagram.

**What the output means:** Browser, then Nginx, Gunicorn, Controllers, Services, DAOs, Models, SQLite file on a named volume. Under it three rules: no SQL in controllers, no HTTP in services, SQL only in DAOs.

**What I will tell the professor:** "The app is layered: controller, service, DAO, database, and each layer has one job."

## Step 4 - Application folder structure [video 01:27]

**What I am doing:** running

```powershell
Get-ChildItem app -Recurse -File -Include *.py,*.sql | Where-Object { $_.FullName -notmatch '__pycache__' } | Resolve-Path -Relative
```

**Spoken script (as in the video):**

> Now the real folders. Under the app folder there are controllers, services, dao, plus models, config, db and the schema file. These match the diagram exactly. Controllers are the web layer, services are the business rules, and dao files contain the database queries. Templates and static files for the pages are in other folders.

**What the output means:** About 20 Python and SQL files under app\controllers, app\services, app\dao, plus app\models.py, app\db.py, app\config.py and app\schema.sql.

**What I will tell the professor:** "The folder layout mirrors the architecture diagram."

## Step 5 - Dependencies and configuration [video 01:55]

**What I am doing:** running

```powershell
Get-Content requirements.txt; Select-String -Path app/config.py -Pattern 'environ.get' | ForEach-Object { $_.Line.Trim() }
```

**Spoken script (as in the video):**

> Dependencies are in requirements dot txt, pinned to exact versions, so every computer and the Jenkins server install the same thing. This is the Python equivalent of a Maven pom file. Configuration is in app config dot py, and every setting comes from an environment variable. That lets the same code run in development, test and production with different values, without secrets in the code.

**What the output means:** Flask and Gunicorn with exact versions, then the environment variables: APP_ENV, SECRET_KEY, DATABASE_PATH, MAX_NIGHTS, APP_VERSION, GIT_COMMIT and the cookie setting.

**What I will tell the professor:** "Versions are pinned and all settings come from environment variables."

## Step 6 - SQLite schema and the six seeded rooms [video 02:24]

**What I am doing:** running

```powershell
Get-Content app/schema.sql | Select-Object -Skip 10 -First 6; Get-Content app/schema.sql | Select-Object -Skip 71
```

**Spoken script (as in the video):**

> The database is SQLite. Here is the rooms table with its columns, and below it the seed data: six demo rooms, two singles, two doubles, a deluxe and a suite. Insert or ignore means that running the schema again never creates duplicates, so it is safe on every start. The same schema file also defines the users and bookings tables and the triggers that prevent double booking.

**What the output means:** CREATE TABLE rooms with id, room_number, room_type, capacity and price; then INSERT OR IGNORE with rooms 101, 102, 201, 202, 301 and 401.

**What I will tell the professor:** "The schema creates the tables and seeds six rooms, and running it twice is safe."

## Step 7 - Starting the application locally [video 02:53]

**What I am doing:** running

```powershell
$env:DATABASE_PATH = "$env:TEMP/hotel-demo-t03.db"; $env:APP_VERSION = 'demo'; $server = Start-Process python -ArgumentList 'wsgi.py' -PassThru -WindowStyle Hidden; Start-Sleep 4; Invoke-RestMethod http://127.0.0.1:5000/health
```

**Spoken script (as in the video):**

> Now I start the real application with the documented command, python wsgi dot py. I give it a temporary database through an environment variable so that your real data is not touched. After four seconds I call the health endpoint. Status ok, environment dev, and the version I set. The server is running.

**What the output means:** status: ok, env: dev, version: demo, commit: unknown (no commit is baked in when running locally).

**What I will tell the professor:** "The portal starts with one command and reports its own health and version."

## Step 8 - A real request: checking room availability [video 03:18]

**What I am doing:** running

```powershell
$r = Invoke-WebRequest 'http://127.0.0.1:5000/rooms?check_in=2030-01-10&check_out=2030-01-12' -UseBasicParsing; "HTTP status: $($r.StatusCode)"; ($r.Content -split '\n' | Select-String 'rooms available').Line.Trim(); 'Available badges: ' + [regex]::Matches($r.Content, 'badge-ok">Available').Count
```

**Spoken script (as in the video):**

> Now I follow one real request. This is what the browser does when a guest searches rooms from the tenth to the twelfth of January 2030. I request the rooms page with those dates. The answer is HTTP 200, and the page says six of six rooms are available, with six Available badges. Next I show which code produced this answer.

**What the output means:** HTTP status 200, '6 of 6 rooms available.' and six Available badges, because no bookings exist in the temporary database.

**What I will tell the professor:** "The same URL a guest uses returns the availability for every room."

## Step 9 - Step 1 of the code path: the controller [video 03:45]

**What I am doing:** running

```powershell
Get-Content app/controllers/room_routes.py | Select-Object -Skip 15 -First 24
```

**Spoken script (as in the video):**

> First, the controller. The function list rooms receives the request, reads the two dates from the web address, and calls the service. It does not contain any database code. If the dates are invalid, the service raises an error and the controller shows it as a message. Then it renders the template, which is the HTML page sent back to the browser.

**What the output means:** list_rooms() reads check_in and check_out from request.args, calls service.search_rooms, catches BookingError, renders rooms.html.

**What I will tell the professor:** "The controller only handles the web request and delegates to the service."

## Step 10 - Step 2 and 3: the service and the DAO [video 04:13]

**What I am doing:** running

```powershell
Get-Content app/services/booking_service.py | Select-Object -Skip 36 -First 6; Get-Content app/dao/booking_dao.py | Select-Object -Skip 5 -First 8; Get-Content app/dao/booking_dao.py | Select-Object -Skip 25 -First 8
```

**Spoken script (as in the video):**

> Second, the service. Search rooms first validates the dates, then asks the booking DAO which rooms are already booked in that period, and marks every other room as available. This is the business rule. Third, the DAO runs the SQL. The overlap rule is written once here: a stay overlaps another when it starts before the other ends and ends after the other starts. Cancelled bookings never block a room.

**What the output means:** search_rooms: validate, booked_room_ids, return (room, available) pairs. Then the overlap SQL condition and booked_room_ids running SELECT DISTINCT room_id.

**What I will tell the professor:** "The service decides what is allowed; the DAO runs the SQL and returns the result."

## Step 11 - Why SQL belongs in the DAO layer [video 04:45]

**What I am doing:** running

```powershell
'SQL lines in controllers + services: ' + (Select-String -CaseSensitive -Path app/controllers/*.py,app/services/*.py -Pattern 'SELECT |INSERT |UPDATE |DELETE ' | Measure-Object).Count; 'SQL lines in dao: ' + (Select-String -CaseSensitive -Path app/dao/*.py -Pattern 'SELECT |INSERT |UPDATE |DELETE ' | Measure-Object).Count
```

**Spoken script (as in the video):**

> Why is SQL only in the DAO? I prove it with a search. In the controllers and services there are zero lines containing SQL keywords. In the DAO files there are ten. Keeping SQL in one layer means that business rules can be tested without a web server, the database can be changed in one place, and nobody can accidentally write a query inside a web page function.

**What the output means:** 0 SQL lines in controllers and services, 10 in the DAO files.

**What I will tell the professor:** "SQL lives only in the DAO layer, which keeps the business logic testable and the database replaceable."

## Step 12 - Python tooling is not Maven [video 05:13]

**What I am doing:** running

```powershell
Get-Content docs/03-srs-architecture.md | Select-Object -Skip 182 -First 17
```

**Spoken script (as in the video):**

> A necessary clarification. The course brief mentions Maven and Tomcat. Those are Java tools. This project is Python, so I use the Python equivalents shown in this table: requirements dot txt instead of a pom file, pytest instead of Maven test, and Gunicorn behind Nginx instead of Tomcat. The document says clearly that if Maven is mandatory and not just an example, I must confirm that with the professor. That is the one unresolved point of Task 3.

**What the output means:** A mapping table Java world versus this project, and the note 'To confirm with the professor'.

**What I will tell the professor:** "I used the Python equivalents and I would like to confirm with you that Maven is not mandatory."

## Step 13 - Stopping the demo server [video 05:50]

**What I am doing:** running

```powershell
taskkill /PID $server.Id /T /F | Out-Null; Remove-Item $env:DATABASE_PATH -ErrorAction SilentlyContinue; try { Invoke-RestMethod http://127.0.0.1:5000/health -TimeoutSec 2 | Out-Null; 'still running' } catch { 'server stopped - nothing answers on port 5000' }
```

**Spoken script (as in the video):**

> Finally I stop the demo server, delete the temporary database, and confirm that nothing answers on port 5000 any more. The demonstration leaves your real database and files unchanged.

**What the output means:** 'server stopped - nothing answers on port 5000'.

**What I will tell the professor:** "The demo cleans up after itself."
