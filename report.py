import os


def _status_color(percent, warn=75, danger=90):
    if percent >= danger:
        return "#e74c3c"
    elif percent >= warn:
        return "#f39c12"
    return "#27ae60"


def _badge(percent, warn=75, danger=90):
    color = _status_color(percent, warn, danger)
    label = "Critical" if percent >= danger else ("Warning" if percent >= warn else "Good")
    return f'<span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-size:0.78em;font-weight:600;">{label}</span>'


def generate_html(data):
    s = data["system"]
    cpu = data["cpu"]
    ram = data["ram"]
    disks = data["disks"]
    net = data["network"]
    bat = data["battery"]
    boot = data["boot"]
    procs = data["processes"]
    temps = data["temperatures"]

    disk_rows = ""
    for d in disks:
        color = _status_color(d["usage_percent"])
        badge = _badge(d["usage_percent"])
        disk_rows += f"""
        <tr>
            <td>{d['device']}</td>
            <td>{d['mountpoint']}</td>
            <td>{d['filesystem']}</td>
            <td>{d['total_gb']} GB</td>
            <td>{d['used_gb']} GB</td>
            <td>{d['free_gb']} GB</td>
            <td>
                <div style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;background:#eee;border-radius:8px;height:10px;">
                        <div style="width:{d['usage_percent']}%;background:{color};height:10px;border-radius:8px;"></div>
                    </div>
                    <span>{d['usage_percent']}%</span>
                    {badge}
                </div>
            </td>
        </tr>"""

    proc_rows = ""
    for p in procs:
        proc_rows += f"""
        <tr>
            <td>{p['pid']}</td>
            <td>{p['name']}</td>
            <td>{round(p['cpu_percent'] or 0, 1)}%</td>
            <td>{round(p['memory_percent'] or 0, 2)}%</td>
        </tr>"""

    net_rows = ""
    for iface in net["interfaces"]:
        net_rows += f"<tr><td>{iface['interface']}</td><td>{iface['ip']}</td><td>{iface['netmask']}</td></tr>"

    temp_section = ""
    if temps:
        temp_rows = ""
        for sensor, entries in temps.items():
            for e in entries:
                warn_str = f"{e['high']}°C" if e['high'] else "N/A"
                crit_str = f"{e['critical']}°C" if e['critical'] else "N/A"
                color = "#e74c3c" if (e['high'] and e['current'] >= e['high']) else "#27ae60"
                temp_rows += f"<tr><td>{sensor}</td><td>{e['label']}</td><td style='color:{color};font-weight:600;'>{e['current']}°C</td><td>{warn_str}</td><td>{crit_str}</td></tr>"
        temp_section = f"""
        <div class="section">
            <h2>🌡️ Temperatures</h2>
            <table>
                <thead><tr><th>Sensor</th><th>Label</th><th>Current</th><th>High</th><th>Critical</th></tr></thead>
                <tbody>{temp_rows}</tbody>
            </table>
        </div>"""

    battery_section = ""
    if bat.get("available"):
        plugged = "✅ Plugged In" if bat["plugged_in"] else "🔋 On Battery"
        battery_section = f"""
        <div class="section">
            <h2>🔋 Battery</h2>
            <div class="stat-grid">
                <div class="stat-card"><div class="stat-label">Charge</div><div class="stat-value">{bat['percent']}%</div></div>
                <div class="stat-card"><div class="stat-label">Status</div><div class="stat-value">{plugged}</div></div>
                <div class="stat-card"><div class="stat-label">Time Left</div><div class="stat-value">{bat['time_left']}</div></div>
            </div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PC Diagnostics Report — {s['hostname']}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; color: #222; }}
  .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: #fff; padding: 36px 48px; }}
  .header h1 {{ font-size: 2em; font-weight: 700; letter-spacing: 1px; }}
  .header .meta {{ margin-top: 8px; opacity: 0.75; font-size: 0.95em; }}
  .container {{ max-width: 1100px; margin: 32px auto; padding: 0 24px 48px; }}
  .section {{ background: #fff; border-radius: 14px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
  .section h2 {{ font-size: 1.15em; font-weight: 700; margin-bottom: 18px; color: #1a1a2e; border-bottom: 2px solid #f0f2f5; padding-bottom: 10px; }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; }}
  .stat-card {{ background: #f7f8fa; border-radius: 10px; padding: 16px 20px; }}
  .stat-label {{ font-size: 0.78em; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
  .stat-value {{ font-size: 1.25em; font-weight: 700; color: #1a1a2e; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.9em; }}
  th {{ background: #f0f2f5; padding: 10px 12px; text-align: left; font-weight: 600; color: #555; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #f0f2f5; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #fafbfc; }}
  .footer {{ text-align: center; color: #aaa; font-size: 0.82em; margin-top: 32px; }}
</style>
</head>
<body>
<div class="header">
  <h1>🖥️ PC Diagnostics Report</h1>
  <div class="meta">
    <strong>{s['hostname']}</strong> &nbsp;·&nbsp; {s['os']} {s['os_release']} &nbsp;·&nbsp; Generated: {s['timestamp']}
  </div>
</div>
<div class="container">

  <div class="section">
    <h2>💻 System Overview</h2>
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-label">Hostname</div><div class="stat-value">{s['hostname']}</div></div>
      <div class="stat-card"><div class="stat-label">Operating System</div><div class="stat-value">{s['os']} {s['os_release']}</div></div>
      <div class="stat-card"><div class="stat-label">Architecture</div><div class="stat-value">{s['architecture']}</div></div>
      <div class="stat-card"><div class="stat-label">Boot Time</div><div class="stat-value">{boot['boot_time']}</div></div>
      <div class="stat-card"><div class="stat-label">Uptime</div><div class="stat-value">{boot['uptime']}</div></div>
    </div>
  </div>

  <div class="section">
    <h2>⚙️ CPU</h2>
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-label">Physical Cores</div><div class="stat-value">{cpu['physical_cores']}</div></div>
      <div class="stat-card"><div class="stat-label">Logical Cores</div><div class="stat-value">{cpu['logical_cores']}</div></div>
      <div class="stat-card"><div class="stat-label">Current Frequency</div><div class="stat-value">{cpu['frequency_mhz']} MHz</div></div>
      <div class="stat-card"><div class="stat-label">Max Frequency</div><div class="stat-value">{cpu['frequency_max_mhz']} MHz</div></div>
      <div class="stat-card"><div class="stat-label">Usage</div><div class="stat-value" style="color:{_status_color(cpu['usage_percent'])}">{cpu['usage_percent']}%</div></div>
    </div>
  </div>

  <div class="section">
    <h2>🧠 Memory (RAM)</h2>
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-label">Total RAM</div><div class="stat-value">{ram['total_gb']} GB</div></div>
      <div class="stat-card"><div class="stat-label">Used</div><div class="stat-value">{ram['used_gb']} GB</div></div>
      <div class="stat-card"><div class="stat-label">Free</div><div class="stat-value">{ram['free_gb']} GB</div></div>
      <div class="stat-card"><div class="stat-label">Usage</div><div class="stat-value" style="color:{_status_color(ram['usage_percent'])}">{ram['usage_percent']}%</div></div>
      <div class="stat-card"><div class="stat-label">Swap Used</div><div class="stat-value">{ram['swap_used_gb']} GB / {ram['swap_total_gb']} GB</div></div>
    </div>
  </div>

  <div class="section">
    <h2>💾 Disk Drives</h2>
    <table>
      <thead><tr><th>Device</th><th>Mount</th><th>Filesystem</th><th>Total</th><th>Used</th><th>Free</th><th>Usage</th></tr></thead>
      <tbody>{disk_rows}</tbody>
    </table>
  </div>

  <div class="section">
    <h2>🌐 Network</h2>
    <div class="stat-grid" style="margin-bottom:16px;">
      <div class="stat-card"><div class="stat-label">Primary IP</div><div class="stat-value">{net['primary_ip']}</div></div>
      <div class="stat-card"><div class="stat-label">Data Sent</div><div class="stat-value">{net['bytes_sent_mb']} MB</div></div>
      <div class="stat-card"><div class="stat-label">Data Received</div><div class="stat-value">{net['bytes_recv_mb']} MB</div></div>
    </div>
    <table>
      <thead><tr><th>Interface</th><th>IP Address</th><th>Netmask</th></tr></thead>
      <tbody>{net_rows}</tbody>
    </table>
  </div>

  {battery_section}
  {temp_section}

  <div class="section">
    <h2>📋 Top 10 Processes (by Memory)</h2>
    <table>
      <thead><tr><th>PID</th><th>Name</th><th>CPU %</th><th>Memory %</th></tr></thead>
      <tbody>{proc_rows}</tbody>
    </table>
  </div>

</div>
<div class="footer">Generated by PC Diagnostics Tool &nbsp;·&nbsp; {s['timestamp']}</div>
</body>
</html>"""
    return html


def save_report(data, output_dir="."):
    html = generate_html(data)
    path = os.path.join(output_dir, "diagnostics_report.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path