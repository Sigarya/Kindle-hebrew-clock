# Kindle-hebrew-clock

![hebrew-clock on a Kindle e-paper display](assets/screenshots/heb-clock.jpg)

A Hebrew word-clock server that generates 800×480 black-and-white PNG images optimized for e-paper displays. The server expresses the current Israel time in natural written Hebrew, together with an analog clock face, the day/date, and a live weather icon. This fork is designed to run on a jailbroken **Kindle** e-reader using [kindle-shortcut-browser](https://github.com/mitchellurgero/kindle-shortcut-browser) to display the clock interface in full-screen.

---

## How It Works

1. The Kindle loads the clock interface from the server using the fullscreen browser.
2. The server renders the current Israel time as written Hebrew words (e.g. *שֶׁבַע וָרֶבַע בָּעֶרֶב* — "quarter past seven in the evening"), draws an analog clock and a weather icon, and returns a 1-bit PNG.
3. The Kindle's browser displays the rendered clock full-screen and auto-refreshes the view at a regular interval.

---

## Display Modes

### Normal clock

The main view shows:
- **Analog clock** at the top centre
- **Hebrew time** in large text (hour + minute phrase + time-of-day period)
- **Day name and date** in the bottom-left cell
- **Time-of-day period** (*בַּבֹּקֶר*, *בָּעֶרֶב*, …) in the centre cell
- **Weather** (icon + temperature + condition) in the bottom-right cell

![Normal clock — Heebo-Bold, Raanana](assets/screenshots/clock-main-heebo-raanana.png)
*Heebo-Bold font — Raanana, 22°C partly cloudy*

![Normal clock — NotoSansHebrew-Bold, Tel Aviv](assets/screenshots/clock-main-noto-telaviv.png)
*NotoSansHebrew-Bold font — Tel Aviv*

![Normal clock — FrankRuhlLibre-Bold, Jerusalem](assets/screenshots/clock-main-frankruh-jerusalem.png)
*FrankRuhlLibre-Bold font — Jerusalem, 19°C sunny*

### Morning quiet window (06:00 – 07:30)

Between 06:00 and 07:30 Israel time the display switches to a minimal "do not disturb" screen so early risers are not bothered by the full refresh flicker.

![Morning quiet — Heebo-Bold, Raanana](assets/screenshots/clock-heebo-raanana.png)
*Heebo-Bold font*

![Morning quiet — NotoSansHebrew-Bold, Tel Aviv](assets/screenshots/clock-noto-telaviv.png)
*NotoSansHebrew-Bold font*

![Morning quiet — FrankRuhlLibre-Bold, Jerusalem](assets/screenshots/clock-frankruh-jerusalem.png)
*FrankRuhlLibre-Bold font*

### Jewish (Hebrew) calendar mode

When `calendar=jewish` is passed, the bottom-left cell shows the full Hebrew date — day numeral, month name, and Hebrew year — fetched from the [hebcal.com](https://www.hebcal.com) converter API and cached for 24 hours.

![Jewish calendar — Heebo-Bold, Raanana](assets/screenshots/clock-jewish.png)
*Hebrew date: כ״ז בְּסִיוָן תשפ״ו*

### Night / sleep mode

When `sleeptime=1` is sent by the browser (during the configured sleep window), the server returns a dark star-field image with a Hebrew "time to sleep" message.

![Night sleep mode](assets/screenshots/clock-sleep.png)

---

## API

The server exposes a single image endpoint at the root path (also reachable as `/clock` or `/clock.png`).

```
GET /?font=<name>&sleeptime=<0|1>&location=<city>&calendar=<gregorian|jewish>
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `font` | `NotoSansHebrew-Bold` | Hebrew font. See [Available Fonts](#available-fonts). |
| `sleeptime` | `0` | Set to `1` to render the night image. |
| `location` | `Tel Aviv` | City passed to the weather API. |
| `calendar` | `gregorian` | `gregorian` for day + Gregorian month; `jewish` for Hebrew date + year (fetched from hebcal.com). |

Response: `image/png`, 800×480, 1-bit, `Cache-Control: no-cache`.

Interactive API docs: `http://<host>:8765/api/docs`

### Example URLs

```
# Heebo-Bold, Raanana, normal mode
https://clk.cloudguard.co.il/?font=Heebo-Bold&sleeptime=0&location=Raanana

# Jewish calendar
https://clk.cloudguard.co.il/?font=Heebo-Bold&sleeptime=0&location=Raanana&calendar=jewish

# Night/sleep image
https://clk.cloudguard.co.il/?font=Heebo-Bold&sleeptime=1
```

---

## Available Fonts

| Font name | Style |
|-----------|-------|
| `NotoSansHebrew-Bold` | Clean modern sans-serif (default) |
| `Heebo-Bold` | Rounded contemporary sans-serif |
| `FrankRuhlLibre-Bold` | Classic serif |
| `FrankRuhlLibre` | Classic serif, regular weight |
| `DavidLibre-Bold` | Traditional Hebrew typeface |

Font files (`.ttf`) must be placed alongside the application (the directory set by the `FONT_DIR` environment variable, default: the project root).

---

## Running with Docker

```yaml
# docker-compose.yml (already included in the repo)
services:
  hebclk:
    build: .
    ports:
      - "8765:8765"
    environment:
      PORT: 8765
      DISPLAY_LAG: 8   # seconds added to displayed time (compensates for refresh delay)
      LOG_LEVEL: info
    restart: unless-stopped
```

```bash
docker compose up -d
```

The container expects font `.ttf` files and `sleeping.png` to be present at build time (the `Dockerfile` copies `*.ttf sleeping.png` from the project root into `/app/`).

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8765` | Listening port |
| `DISPLAY_LAG` | `8` | Seconds added to Israel time before rendering (accounts for ePaper refresh time) |
| `LOG_LEVEL` | `info` | Loguru log level |
| `FONT_DIR` | app root | Directory containing `.ttf` files |

---

## Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8765
```

---

## Deploying to Render

[Render](https://render.com) is a managed cloud platform that can run the server for free with zero infrastructure setup.

### Prerequisites — font files

Render deploys directly from the repository, so the Hebrew font `.ttf` files and `sleeping.png` must be committed to the repo root before deploying. Add the files you want to use (any subset is fine; the server falls back gracefully):

```
NotoSansHebrew-Bold.ttf   ← recommended minimum
Heebo-Bold.ttf
FrankRuhlLibre-Bold.ttf
FrankRuhlLibre.ttf
DavidLibre-Bold.ttf
sleeping.png
```

### Option A — one-click deploy (render.yaml)

The repo includes a `render.yaml` blueprint. Click the button below, connect your GitHub account, and Render will pre-fill all settings:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Option B — manual setup

1. Log in to [render.com](https://render.com) and click **New → Web Service**.
2. Connect your GitHub account and select the `hebrew-clock` repository.
3. Fill in the service settings:

   | Field | Value |
   |-------|-------|
   | **Name** | `hebrew-clock` (or any name you like) |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. Under **Environment Variables**, add:

   | Key | Value | Notes |
   |-----|-------|-------|
   | `FONT_DIR` | `.` | Repo root — where the `.ttf` files live |
   | `DISPLAY_LAG` | `8` | Seconds ahead to render (adjust to match your display's refresh time) |
   | `LOG_LEVEL` | `info` | |

5. Set the **Health Check Path** to `/health`.
6. Click **Create Web Service**. Render will build and deploy; the service URL appears in the dashboard.

---

## Kindle Setup

To view the Hebrew clock on a jailbroken Kindle, you can use the **[kindle-shortcut-browser](https://github.com/mitchellurgero/kindle-shortcut-browser)** application to render the page full-screen.

### Setup Instructions

1. **Download the Latest Release:**
   Obtain the latest ZIP archive from the [kindle-shortcut-browser releases page](https://github.com/mitchellurgero/kindle-shortcut-browser/releases).

2. **Extract to Kindle Root:**
   Connect your Kindle to a computer and extract the contents of the ZIP archive directly to the root directory of your Kindle's mounted storage.

3. **Configure the Server URL:**
   You can direct the Kindle browser to your Hebrew Clock server using one of the following methods:
   * **Method A (Via HTML index):** Open the file `<YourKindle>\documents\shortcutbrowser\index.html` and modify `https://example.com` to point to your Hebrew clock server (e.g., `http://<your-server-ip>:8765/` or your Render deployment URL).
   * **Method B (Via Shell Script):** Open `<YourKindle>\documents\shortcut_browser.sh` and set the `FULLSCREEN_SITE` variable to your clock server URL:
     ```bash
     FULLSCREEN_SITE="http://<your-server-ip>:8765/"
     ```

4. **Launch the Interface:**
   Safely eject the Kindle from your computer, open your Kindle's library or KUAL menu, and launch the shortcut browser app to run the clock.

---

## Project Structure

```
app/
  main.py              # FastAPI app + lifespan
  api/v1/router.py     # GET / endpoint
  core/config.py       # Settings (pydantic-settings)
  services/
    clock.py           # Image generation (PIL, Hebrew word-clock logic)
    weather.py         # wttr.in weather cache
    jewish_cal.py      # hebcal.com Hebrew date fetch + cache
assets/screenshots/    # README images
Dockerfile
docker-compose.yml
requirements.txt
```
