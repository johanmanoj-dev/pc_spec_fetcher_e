import customtkinter as ctk
import threading
import os
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import diagnostics
import report
import mailer
import config_manager


class DiagnosticsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PC Diagnostics Tool")
        self.geometry("560x660")
        self.resizable(False, False)

        # Apply modern dark theme natively via CustomTkinter
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Try to set a taskbar icon (Windows)
        try:
            self.iconbitmap(default="icon.ico")
        except Exception:
            pass

        self._report_path = None
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Header / Logo Area
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(36, 24))
        
        ctk.CTkLabel(logo_frame, text="🖥️", font=("Segoe UI", 48)).pack()
        ctk.CTkLabel(logo_frame, text="PC Diagnostics Tool", font=("Segoe UI", 24, "bold")).pack(pady=(8, 0))
        ctk.CTkLabel(logo_frame, text="Automatic system report & email delivery", font=("Segoe UI", 13), text_color="gray").pack(pady=(4, 0))

        # Status card (Rounded native modern layout)
        self.card = ctk.CTkFrame(self, corner_radius=12)
        self.card.pack(fill="x", padx=40, pady=(10, 20))
        
        self._status_label = ctk.CTkLabel(self.card, text="Ready to scan your PC.", font=("Segoe UI", 15, "bold"))
        self._status_label.pack(anchor="w", padx=24, pady=(24, 6))
        
        self._sub_label = ctk.CTkLabel(self.card, text="Click the button below to start.", font=("Segoe UI", 12), text_color="gray")
        self._sub_label.pack(anchor="w", padx=24, pady=(0, 24))

        # Progress bar
        self._progress = ctk.CTkProgressBar(self.card, height=6)
        self._progress.pack(fill="x", padx=24, pady=(0, 24))
        self._progress.set(0)

        # Steps indicator
        steps_frame = ctk.CTkFrame(self, fg_color="transparent")
        steps_frame.pack(fill="x", padx=48, pady=(0, 24))
        
        self._step_labels = []
        steps = ["Collect system data", "Generate HTML report", "Send via email"]
        for i, step in enumerate(steps):
            row = ctk.CTkFrame(steps_frame, fg_color="transparent")
            row.pack(anchor="w", pady=8)
            dot = ctk.CTkLabel(row, text="○", font=("Segoe UI", 15, "bold"), text_color="gray", width=30)
            dot.pack(side="left")
            lbl = ctk.CTkLabel(row, text=step, font=("Segoe UI", 13, "bold"), text_color="gray")
            lbl.pack(side="left")
            self._step_labels.append((dot, lbl))

        # Buttons
        self._run_btn = ctk.CTkButton(self, text="Run Diagnostics", font=("Segoe UI", 15, "bold"), corner_radius=8, height=48, command=self._start)
        self._run_btn.pack(fill="x", padx=40, pady=(10, 0))

        # Footer
        ctk.CTkLabel(self, text=f"Host: {socket.gethostname()}", font=("Segoe UI", 11), text_color="gray").pack(side="bottom", pady=16)

    # ── Step indicator helpers ────────────────────────────────────────────────

    def _reset_steps(self):
        for dot, lbl in self._step_labels:
            dot.configure(text="○", text_color="gray")
            lbl.configure(text_color="gray")
        self._progress.configure(mode="indeterminate")
        self._progress.start()

    def _set_step(self, index, done=False):
        for i, (dot, lbl) in enumerate(self._step_labels):
            if i < index:
                dot.configure(text="✓", text_color="#10b981") # Emerald
                lbl.configure(text_color="#10b981")
            elif i == index:
                dot.configure(text="●", text_color="#3b82f6") # Blue
                lbl.configure(text_color=["#000000", "#FFFFFF"]) # Standard text color
            else:
                dot.configure(text="○", text_color="gray")
                lbl.configure(text_color="gray")
        if done:
            for dot, lbl in self._step_labels:
                dot.configure(text="✓", text_color="#10b981")
                lbl.configure(text_color="#10b981")

    # ── Main run flow ─────────────────────────────────────────────────────────

    def _start(self):
        self._run_btn.configure(state="disabled")
        self._reset_steps()
        threading.Thread(target=self._run_pipeline, daemon=True).start()

    def _run_pipeline(self):
        try:
            # Step 1 — collect
            self._update_status("Collecting system data…", "Scanning hardware and OS…")
            self.after(0, self._set_step, 0)
            data = diagnostics.collect_all()
            data["system"]["hostname"] = socket.gethostname()

            # Step 2 — report
            self._update_status("Generating report…", "Building your HTML diagnostics report…")
            self.after(0, self._set_step, 1)
            out_dir = os.path.dirname(os.path.abspath(__file__))
            self._report_path = report.save_report(data, out_dir)

            # Step 3 — email
            self._update_status("Sending email…", "Connecting to SMTP server…")
            self.after(0, self._set_step, 2)

            # Load credentials from environment variables
            cfg = {
                "sender_email": os.getenv("SENDER_EMAIL"),
                "app_password": os.getenv("APP_PASSWORD"),
                "recipient": os.getenv("RECIPIENT_EMAIL"),
                "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
                "smtp_port": os.getenv("SMTP_PORT", "587"),
                "hostname": data["system"]["hostname"]
            }

            if all([cfg["sender_email"], cfg["app_password"], cfg["recipient"]]):
                mailer.send_report(self._report_path, cfg)
                self._finish_ok("Report sent to your inbox! ✅",
                                "Email delivered successfully.")
            else:
                self._finish_warn("Report saved — email not configured.",
                                  "Please check your .env file to enable sending.")

        except Exception as e:
            self._finish_error(f"Error: {e}")

    # ── UI state updates (thread-safe) ────────────────────────────────────────

    def _update_status(self, main, sub=""):
        self.after(0, lambda: self._status_label.configure(text=main, text_color=["#000000", "#FFFFFF"]))
        self.after(0, lambda: self._sub_label.configure(text=sub, text_color="gray"))

    def _finish_ok(self, main, sub):
        self.after(0, self._do_finish_ok, main, sub)

    def _do_finish_ok(self, main, sub):
        self._progress.stop()
        self._progress.configure(mode="determinate")
        self._progress.set(1)
        self._status_label.configure(text=main, text_color="#10b981")
        self._sub_label.configure(text=sub, text_color="gray")
        self._set_step(-1, done=True)
        self._run_btn.configure(state="normal")

    def _finish_warn(self, main, sub):
        self.after(0, self._do_finish_warn, main, sub)

    def _do_finish_warn(self, main, sub):
        self._progress.stop()
        self._progress.configure(mode="determinate")
        self._progress.set(1)
        self._status_label.configure(text=main, text_color="#f59e0b")
        self._sub_label.configure(text=sub, text_color="gray")
        self._set_step(-1, done=True)
        self._run_btn.configure(state="normal")

    def _finish_error(self, msg):
        self.after(0, self._do_finish_error, msg)

    def _do_finish_error(self, msg):
        self._progress.stop()
        self._status_label.configure(text="Something went wrong.", text_color="#ef4444")
        self._sub_label.configure(text=msg, text_color="#ef4444")
        self._run_btn.configure(state="normal")

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = DiagnosticsApp()
    app.mainloop()