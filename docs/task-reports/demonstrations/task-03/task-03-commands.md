# Task 3 - command sheet

**Task 3 - Requirements, Architecture and Technology Setup**

## Before you start

- Port 5000 must be free. The local Docker registry also uses port 5000, so if `hotel-jenkins-registry-1` is running, stop it first: `docker stop hotel-jenkins-registry-1`.
- The project `.venv` must exist (Flask is installed there).
- The demo starts the app on a throw-away database in your TEMP folder, so your real `instance/hotel.db` is never touched.
- Open PowerShell in the project folder.

Working directory for every command:

```powershell
cd D:\DevOPS\CICD_FOR_HOTEL_ROOM_BOOKING
```

## Commands in the order they are run in the video

| # | Step | Command / action | Expected result |
|---|---|---|---|
| 1 | SRS summary: requirements mapped to code | `Select-String -Path docs/03-srs-architecture.md -Pattern '^\\| FR' \| ForEach-Object { $p = $_.Line -split '\\|'; $p[1].Trim() + '  ' + $p[3].Trim() }` | FR1 to FR11, each followed by the class or file that implements it. |
| 2 | Use-case diagram | `Get-Content docs/03-srs-architecture.md \| Select-Object -Skip 34 -First 22` | Mermaid diagram source with three actors: Guest, Developer, Operator, linked to nine use cases. |
| 3 | Architecture diagram | `Get-Content docs/03-srs-architecture.md \| Select-Object -Skip 59 -First 17` | Browser, then Nginx, Gunicorn, Controllers, Services, DAOs, Models, SQLite file on a named volume. Under it three rules: no SQL in controllers, no HTTP in services, SQL only in DAOs. |
| 4 | Application folder structure | `Get-ChildItem app -Recurse -File -Include *.py,*.sql \| Where-Object { $_.FullName -notmatch '__pycache__' } \| Resolve-Path -Relative` | About 20 Python and SQL files under app\controllers, app\services, app\dao, plus app\models.py, app\db.py, app\config.py and app\schema.sql. |
| 5 | Dependencies and configuration | `Get-Content requirements.txt; Select-String -Path app/config.py -Pattern 'environ.get' \| ForEach-Object { $_.Line.Trim() }` | Flask and Gunicorn with exact versions, then the environment variables: APP_ENV, SECRET_KEY, DATABASE_PATH, MAX_NIGHTS, APP_VERSION, GIT_COMMIT and the cookie setting. |
| 6 | SQLite schema and the six seeded rooms | `Get-Content app/schema.sql \| Select-Object -Skip 10 -First 6; Get-Content app/schema.sql \| Select-Object -Skip 71` | CREATE TABLE rooms with id, room_number, room_type, capacity and price; then INSERT OR IGNORE with rooms 101, 102, 201, 202, 301 and 401. |
| 7 | Starting the application locally | `$env:DATABASE_PATH = "$env:TEMP/hotel-demo-t03.db"; $env:APP_VERSION = 'demo'; $server = Start-Process python -ArgumentList 'wsgi.py' -PassThru -WindowStyle Hidden; Start-Sleep 4; Invoke-RestMethod http://127.0.0.1:5000/health` | status: ok, env: dev, version: demo, commit: unknown (no commit is baked in when running locally). |
| 8 | A real request: checking room availability | `$r = Invoke-WebRequest 'http://127.0.0.1:5000/rooms?check_in=2030-01-10&check_out=2030-01-12' -UseBasicParsing; "HTTP status: $($r.StatusCode)"; ($r.Content -split '\n' \| Select-String 'rooms available').Line.Trim(); 'Available badges: ' + [regex]::Matches($r.Content, 'badge-ok">Available').Count` | HTTP status 200, '6 of 6 rooms available.' and six Available badges, because no bookings exist in the temporary database. |
| 9 | Step 1 of the code path: the controller | `Get-Content app/controllers/room_routes.py \| Select-Object -Skip 15 -First 24` | list_rooms() reads check_in and check_out from request.args, calls service.search_rooms, catches BookingError, renders rooms.html. |
| 10 | Step 2 and 3: the service and the DAO | `Get-Content app/services/booking_service.py \| Select-Object -Skip 36 -First 6; Get-Content app/dao/booking_dao.py \| Select-Object -Skip 5 -First 8; Get-Content app/dao/booking_dao.py \| Select-Object -Skip 25 -First 8` | search_rooms: validate, booked_room_ids, return (room, available) pairs. Then the overlap SQL condition and booked_room_ids running SELECT DISTINCT room_id. |
| 11 | Why SQL belongs in the DAO layer | `'SQL lines in controllers + services: ' + (Select-String -CaseSensitive -Path app/controllers/*.py,app/services/*.py -Pattern 'SELECT \|INSERT \|UPDATE \|DELETE ' \| Measure-Object).Count; 'SQL lines in dao: ' + (Select-String -CaseSensitive -Path app/dao/*.py -Pattern 'SELECT \|INSERT \|UPDATE \|DELETE ' \| Measure-Object).Count` | 0 SQL lines in controllers and services, 10 in the DAO files. |
| 12 | Python tooling is not Maven | `Get-Content docs/03-srs-architecture.md \| Select-Object -Skip 182 -First 17` | A mapping table Java world versus this project, and the note 'To confirm with the professor'. |
| 13 | Stopping the demo server | `taskkill /PID $server.Id /T /F \| Out-Null; Remove-Item $env:DATABASE_PATH -ErrorAction SilentlyContinue; try { Invoke-RestMethod http://127.0.0.1:5000/health -TimeoutSec 2 \| Out-Null; 'still running' } catch { 'server stopped - nothing answers on port 5000' }` | 'server stopped - nothing answers on port 5000'. |

Note: the recorder prepends `.venv\Scripts` to PATH, so `pytest` and `python` mean the
project's virtual-environment versions. In your own terminal use `.venv\Scripts\pytest`
(or activate with `.venv\Scripts\Activate.ps1`). Variables such as `$c` or `$s` are set by an
earlier step, so run the steps of one part in the same PowerShell window and in order.

## Extra commands (not recorded, for your own practice)

- Run the real development server yourself and open it in a browser:

  ```powershell
  .venv\Scripts\python wsgi.py   # then open http://127.0.0.1:5000
  ```

- Open the architecture and ER diagrams drawn (VS Code preview or GitHub):

  ```powershell
  code docs/03-srs-architecture.md
  ```

## If something is not running (recovery)

| Symptom | What to do |
|---|---|
| /health does not answer | The server needs a few seconds. Wait 5 seconds and run the health command again. If it still fails, start it in a visible window to see the error: `python wsgi.py`. |
| Port 5000 already in use | `Get-NetTCPConnection -LocalPort 5000 -State Listen` shows the owner. Stop the registry (`docker stop hotel-jenkins-registry-1`) or an old Python process (`taskkill /PID <pid> /T /F`). |
| `python` is not recognised or Flask is missing | Use `.venv\Scripts\python wsgi.py`, or create the environment: `python -m venv .venv` then `.venv\Scripts\pip install -r requirements-dev.txt`. |
| A leftover server keeps running after the demo | `Get-Process python | Stop-Process` (only if you have no other Python programs running), or `taskkill /PID <pid> /T /F`. |

Re-record with:

```powershell
powershell -ExecutionPolicy Bypass -File docs\task-reports\demonstrations\_tools\record-demo.ps1 -TaskId 03
```
