# No Bars Club Website Status Integration

The bridge exposes a deliberately small public API designed for `NoBarsClub.com`.

## Public endpoints

- `GET /api/status` — public operational status and counters
- `GET /healthz` — lightweight health check for monitoring

The public API does **not** expose message text, sender names, channel names,
channel secrets, serial ports, device identifiers, configuration content, or
administrative actions.

## Recommended public hostname

Use a dedicated hostname such as:

`https://bridge.nobarsclub.com/api/status`

The included Nginx example exposes only `/api/status` and `/healthz` and returns
404 for the rest of the NiceGUI application.

## Example browser widget

```html
<section id="nbc-mesh-bridge-status" aria-live="polite">
  <strong>No Bars Mesh Bridge</strong>
  <span id="nbc-bridge-state">Checking…</span>
  <span id="nbc-bridge-count"></span>
</section>

<script>
(async () => {
  const state = document.getElementById('nbc-bridge-state');
  const count = document.getElementById('nbc-bridge-count');

  try {
    const response = await fetch('https://bridge.nobarsclub.com/api/status', {
      cache: 'no-store'
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    state.textContent = data.status === 'online' ? 'Online' : 'Degraded';
    count.textContent = `${data.messages_forwarded.toLocaleString()} messages bridged`;
  } catch (error) {
    state.textContent = 'Status unavailable';
    count.textContent = '';
  }
})();
</script>
```

## Expected API response

```json
{
  "service": "No Bars Mesh Bridge",
  "status": "online",
  "generated_at": "2026-09-05T15:00:00+00:00",
  "uptime_seconds": 583920,
  "devices": {
    "a": {"connected": true},
    "b": {"connected": true}
  },
  "bridges_configured": 2,
  "messages_forwarded": 12482,
  "forwarded_a_to_b": 7000,
  "forwarded_b_to_a": 5482,
  "duplicates_blocked": 37,
  "last_activity": "10:59:31"
}
```

## Deployment rule

Do not iframe or reverse proxy the entire NiceGUI dashboard onto the public
website. The dashboard includes operational controls and message logs. Publish
only the read-only API endpoints and build the public UI from those values.
