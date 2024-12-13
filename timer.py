import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

class AdvancedTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Developer Timer")
        self.root.geometry("500x850")  # Increased height to 850
        self.bg_color = "#e6e6fa"  # Lavender background color
        self.root.configure(bg=self.bg_color)
        self.root.iconbitmap('clock-icon.ico')

        # Default values
        self.work_time = tk.DoubleVar(value=50.0)
        self.break_time = tk.DoubleVar(value=10.0)
        self.work_warning_time = tk.DoubleVar(value=2.0)
        self.break_warning_time = tk.DoubleVar(value=1.0)
        self.reminder_interval = tk.DoubleVar(value=10.0)
        self.earning_per_hour = tk.DoubleVar(value=60)
        self.end_of_day = tk.StringVar(value="17:00")

        # Currency selection
        self.currency_var = tk.StringVar(value="PLN")

        # Variables for tracking time and earnings
        self.running = False
        self.paused = False
        self.state = "settings"
        self.start_time = None

        self.total_seconds = 0
        self.total_work_seconds = 0
        self.total_break_seconds = 0
        self.earnings = 0.0
        self.earning_rate = 0.0

        self.waiting_for_confirmation = False
        self.skip_to_next_cycle = False  # Flag to skip to the next cycle

        # Set up the interface
        self.setup_interface()

    def setup_interface(self):
        # Top title
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(fill='x', pady=10)

        tk.Label(title_frame, text="Timer Settings", font=("Arial", 20, "bold"), bg=self.bg_color).pack(side='left', padx=10)

        # Work Settings section
        work_frame = tk.LabelFrame(self.root, text="Work Settings", font=("Arial", 16, "bold"), bg=self.bg_color)
        work_frame.pack(fill='x', padx=10, pady=5)

        self.create_labeled_entry(work_frame, "Work time (minutes):", self.work_time, row=0)
        self.create_labeled_entry(work_frame, "Work warning time before end (minutes):", self.work_warning_time, row=1)

        # Break Settings section
        break_frame = tk.LabelFrame(self.root, text="Break Settings", font=("Arial", 16, "bold"), bg=self.bg_color)
        break_frame.pack(fill='x', padx=10, pady=5)

        self.create_labeled_entry(break_frame, "Break time (minutes):", self.break_time, row=0)
        self.create_labeled_entry(break_frame, "Break warning time before end (minutes):", self.break_warning_time, row=1)

        # Eye Care Settings section
        eye_care_frame = tk.LabelFrame(self.root, text="Eye Care Settings", font=("Arial", 16, "bold"), bg=self.bg_color)
        eye_care_frame.pack(fill='x', padx=10, pady=5)

        self.create_labeled_entry(eye_care_frame, "Look away reminder (minutes):", self.reminder_interval, row=0)

        # Earnings Settings section
        earnings_frame = tk.LabelFrame(self.root, text="Earnings Settings", font=("Arial", 16, "bold"), bg=self.bg_color)
        earnings_frame.pack(fill='x', padx=10, pady=5)

        self.create_labeled_entry(earnings_frame, "Earnings per hour:", self.earning_per_hour, row=0)

        # Currency selection
        currency_label = tk.Label(earnings_frame, text="Currency:", font=("Arial", 14), bg=self.bg_color)
        currency_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)

        currency_options = ["PLN", "USD", "EUR"]
        currency_menu = tk.OptionMenu(earnings_frame, self.currency_var, *currency_options)
        currency_menu.config(font=("Arial", 14), width=5)
        currency_menu.grid(row=1, column=1, sticky='e', padx=5, pady=5)
        currency_menu.config(bg=self.bg_color)

        # End of Work Day section
        end_of_day_frame = tk.LabelFrame(self.root, text="End of Work Day", font=("Arial", 16, "bold"), bg=self.bg_color)
        end_of_day_frame.pack(fill='x', padx=10, pady=5)

        self.create_labeled_entry(end_of_day_frame, "End of workday (HH:MM):", self.end_of_day, entry_width=5, row=0)

        # Start button (keep it centered)
        start_button = tk.Button(self.root, text="Start", font=("Arial", 16, "bold"), command=self.open_tracking_window,
                                 bg="#4CAF50", fg="white", width=10, height=2)
        start_button.pack(pady=20)

        # Summary section
        self.summary_frame = tk.LabelFrame(self.root, text="Summary", font=("Arial", 16, "bold"), bg=self.bg_color)
        self.summary_frame.pack(fill='x', padx=10, pady=5)
        self.summary_label = tk.Label(self.summary_frame, text="No data yet.", font=("Arial", 14), justify="center", bg=self.bg_color)
        self.summary_label.pack(pady=10, fill='x')

        # Bottom frame for Description and Reset buttons
        bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        bottom_frame.pack(fill='x', side='bottom', pady=10)

        button_font = ("Arial", 13)
        button_width = 11

        description_button = tk.Button(bottom_frame, text="Description", command=self.show_description,
                                       font=button_font, bg="#2196F3", fg="white", width=button_width)
        description_button.pack(side='left', padx=10, pady=5)

        reset_button = tk.Button(bottom_frame, text="Reset", command=self.reset_values, font=button_font,
                                 bg="#f44336", fg="white", width=button_width)
        reset_button.pack(side='right', padx=10, pady=5)

    def create_labeled_entry(self, parent, label_text, variable, entry_width=10, row=0, padx=5, pady=5):
        label = tk.Label(parent, text=label_text, font=("Arial", 14), bg=self.bg_color)
        label.grid(row=row, column=0, sticky='w', padx=padx, pady=pady)
        entry = tk.Entry(parent, textvariable=variable, font=("Arial", 14), width=entry_width)
        entry.grid(row=row, column=1, sticky='e', padx=padx, pady=pady)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

    def open_tracking_window(self):
        self.root.withdraw()

        self.tracking_window = tk.Toplevel(self.root)
        self.tracking_window.geometry("600x400")
        self.tracking_window.protocol("WM_DELETE_WINDOW", self.on_close_tracking_window)

        # Set end of workday time
        try:
            end_time_str = self.end_of_day.get()
            self.end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter a valid time in HH:MM format.")
            self.running = False
            self.root.deiconify()
            return

        # Initialize current mode variables
        self.work_seconds = int(self.work_time.get() * 60)
        self.break_seconds = int(self.break_time.get() * 60)
        self.work_warning_seconds = int(self.work_warning_time.get() * 60)
        self.break_warning_seconds = int(self.break_warning_time.get() * 60)
        self.reminder_interval_seconds = int(self.reminder_interval.get() * 60)
        self.earning_rate = self.earning_per_hour.get() / 3600  # Earnings per second
        self.currency = self.currency_var.get()

        self.current_mode = "Work time"
        self.current_seconds = self.work_seconds
        self.warning_seconds = self.work_warning_seconds
        self.elapsed = 0
        self.warning_triggered = False

        # Calculate time to end of day
        now = datetime.now()
        end_datetime = datetime.combine(now.date(), self.end_time)
        if end_datetime < now:
            end_datetime += timedelta(days=1)
        self.end_of_day_seconds = int((end_datetime - now).total_seconds())

        # Create labels and widgets before updating the window title
        # Total time label (with reduced border)
        total_minutes = self.total_seconds // 60
        total_hours = total_minutes // 60
        total_minutes = total_minutes % 60

        self.total_time_label = tk.Label(self.tracking_window, text=f"Total time: {total_hours:02}:{total_minutes:02}",
                                         font=("Arial", 18), relief="flat", bd=0)
        self.total_time_label.pack(pady=10, padx=20, fill='x')

        earnings_text = f"Earnings: {self.earnings:.2f} {self.currency}" if self.earning_per_hour.get() != 0 else ""
        self.earnings_label = tk.Label(self.tracking_window, text=earnings_text, font=("Arial", 18),
                                       relief="flat", bd=0)
        self.earnings_label.pack(pady=10, padx=20, fill='x')

        # Mode label (with reduced border)
        self.cycle_label = tk.Label(self.tracking_window, text=self.current_mode, font=("Arial", 28, "bold"),
                                    relief="flat", bd=0)
        self.cycle_label.pack(pady=5, padx=20, fill='x')

        # Countdown label (with reduced border)
        self.cycle_time_label = tk.Label(self.tracking_window, text="", font=("Arial", 24),
                                         relief="flat", bd=0)
        self.cycle_time_label.pack(pady=5, padx=20, fill='x')

        # Buttons: Pause, Skip, Stop, Change Time
        button_frame = tk.Frame(self.tracking_window)
        button_frame.pack(pady=10)

        self.pause_button = tk.Button(button_frame, text="Pause", command=self.toggle_pause, font=("Arial", 16),
                                      bg="#FFC107", fg="black", width=10, height=2)
        self.pause_button.pack(side="left", padx=10, pady=5)

        self.skip_button = tk.Button(button_frame, text="Skip", command=self.skip_current_cycle, font=("Arial", 16),
                                     bg="#FF9800", fg="white", width=10, height=2)
        self.skip_button.pack(side="left", padx=10, pady=5)

        self.change_time_button = tk.Button(button_frame, text="Change Time", command=self.change_current_cycle_time,
                                            font=("Arial", 16), bg="#2196F3", fg="white", width=12, height=2)
        self.change_time_button.pack(side="left", padx=10, pady=5)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.on_close_tracking_window, font=("Arial", 16),
                                     bg="#f44336", fg="white", width=10, height=2)
        self.stop_button.pack(side="left", padx=10, pady=5)

        # Bottom labels: Start time (left), Time to end of day (right)
        bottom_frame = tk.Frame(self.tracking_window)
        bottom_frame.pack(fill='x', side='bottom', pady=10)

        self.start_time = datetime.now().strftime("%H:%M")
        self.start_time_label = tk.Label(bottom_frame, text=f"Start: {self.start_time}",
                                         font=("Arial", 14, "italic"))
        self.start_time_label.pack(side="left", padx=10)

        self.time_to_end_label = tk.Label(bottom_frame, text="", font=("Arial", 14, "italic"))
        self.time_to_end_label.pack(side="right", padx=10)

        # Now update the window title and background colors
        self.update_window_title()

        self.running = True
        self.paused = False
        self.state = "counting"

        self.update_timer()

    def update_window_title(self):
        if self.current_mode == "Work time":
            self.current_bg_color = "light green"
            self.tracking_window.title("Timer (Working...)")
        else:
            self.current_bg_color = "light blue"
            self.tracking_window.title("Timer (Break...)")

        self.tracking_window.configure(bg=self.current_bg_color)
        self.update_background_colors()
        self.update_cycle_label_color()

    def update_background_colors(self):
        # Update backgrounds of labels to match the current background color
        labels = [
            self.total_time_label,
            self.earnings_label,
            self.cycle_label,
            self.cycle_time_label,
            self.start_time_label,
            self.time_to_end_label,
        ]
        for label in labels:
            label.configure(bg=self.current_bg_color)

        # Update frames
        self.tracking_window.configure(bg=self.current_bg_color)
        self.pause_button.master.configure(bg=self.current_bg_color)
        self.start_time_label.master.configure(bg=self.current_bg_color)

    def update_cycle_label_color(self):
        if self.current_mode == "Work time":
            if not self.warning_triggered:
                self.cycle_label.config(fg="dark green")
        else:
            if not self.warning_triggered:
                self.cycle_label.config(fg="dark blue")

    def on_close_tracking_window(self):
        self.running = False
        self.tracking_window.destroy()
        self.root.deiconify()
        self.update_summary_label()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="Resume", bg="#4CAF50")
        else:
            self.pause_button.config(text="Pause", bg="#FFC107")
            if self.skip_to_next_cycle:
                self.skip_to_next_cycle = False
                self.move_to_next_cycle()
            else:
                # Continue current cycle
                pass

    def skip_current_cycle(self):
        # Skip current cycle and move to the next
        self.move_to_next_cycle()

    def change_current_cycle_time(self):
        # Dialog to change current cycle time
        dialog = tk.Toplevel()
        dialog.title("Change Current Cycle Time")
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        dialog.resizable(False, False)

        tk.Label(dialog, text="Enter new time in minutes:", font=("Arial", 14)).pack(pady=10)

        new_time_var = tk.IntVar(value=int((self.current_seconds - self.elapsed) / 60))
        entry = tk.Entry(dialog, textvariable=new_time_var, font=("Arial", 14), width=10)
        entry.pack(pady=5)

        def confirm_change():
            try:
                new_time = int(new_time_var.get()) * 60
                if new_time <= 0:
                    raise ValueError
                self.current_seconds = self.elapsed + new_time
                self.warning_triggered = False
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Invalid Time", "Please enter a valid positive integer.")
                return

        confirm_button = tk.Button(dialog, text="Confirm", command=confirm_change, font=("Arial", 12))
        confirm_button.pack(pady=10)

    def show_description(self):
        description = (
            "Developer Timer Application:\n"
            "- Set work time, break time, warning times for work and break, reminder intervals, earnings rate, and end of work day.\n"
            "- Start the timer, which alternates between work and break times.\n"
            "- After each cycle, confirm if you want to continue.\n"
            "- Total time and earnings continue to accumulate.\n"
            "- You can pause, skip cycles, change current cycle time, or stop the timer.\n"
            "- The application shows the time left until the end of the workday.\n"
            "- If warning times are set to 0, warnings are skipped."
        )
        messagebox.showinfo("Application Description", description)

    def update_timer(self):
        if not self.running:
            return

        # Update time to end of day
        self.end_of_day_seconds -= 1
        time_to_end_minutes = self.end_of_day_seconds // 60
        time_to_end_hours = time_to_end_minutes // 60
        time_to_end_minutes = time_to_end_minutes % 60
        self.time_to_end_label.config(text=f"End in: {time_to_end_hours}h {time_to_end_minutes}min")

        if self.end_of_day_seconds <= 0:
            self.end_of_workday()
            return

        if self.paused:
            self.tracking_window.after(1000, self.update_timer)
            return

        # Update total time and earnings
        self.total_seconds += 1
        self.earnings += self.earning_rate
        self.update_total_time_and_earnings()

        if self.waiting_for_confirmation:
            # Waiting for user decision
            self.tracking_window.after(1000, self.update_timer)
            return

        if self.state == "counting":
            if self.elapsed < self.current_seconds:
                self.elapsed += 1

                remaining_time = self.current_seconds - self.elapsed
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                self.cycle_time_label.config(text=f"{minutes}:{seconds:02}")

                # Summing work and break times
                if self.current_mode == "Work time":
                    self.total_work_seconds += 1
                else:
                    self.total_break_seconds += 1

                # Check for warning
                if remaining_time <= self.warning_seconds and self.warning_seconds != 0 and not self.warning_triggered:
                    self.cycle_label.config(fg="red")
                    self.warning_triggered = True
                    # Display minutes and seconds in notification
                    self.show_custom_notification(
                        "Warning",
                        f"{self.current_mode} is ending in {remaining_time // 60} min {remaining_time % 60} sec."
                    )

                # Reminder to look away
                if (self.current_mode == "Work time" and
                    self.reminder_interval_seconds != 0 and
                    self.elapsed % self.reminder_interval_seconds == 0 and
                    self.elapsed != 0):
                    self.show_custom_notification("Reminder", "Look into the distance.")

                self.tracking_window.after(1000, self.update_timer)
            else:
                # Current cycle ended
                self.state = "waiting"
                self.warning_triggered = False
                self.elapsed = 0

                self.wait_for_confirmation()
                self.tracking_window.after(1000, self.update_timer)

        elif self.state == "waiting":
            # Waiting for user decision
            self.tracking_window.after(1000, self.update_timer)

    def update_total_time_and_earnings(self):
        total_minutes = self.total_seconds // 60
        total_hours = total_minutes // 60
        total_minutes = total_minutes % 60
        self.total_time_label.config(text=f"Total time: {total_hours:02}:{total_minutes:02}")
        if self.earning_per_hour.get() != 0:
            self.earnings_label.config(text=f"Earnings: {self.earnings:.2f} {self.currency}")
        else:
            self.earnings_label.config(text="")

        # Update summary on settings screen
        self.update_summary_label()

    def update_summary_label(self):
        total_minutes = self.total_seconds // 60
        total_hours = total_minutes // 60
        total_minutes = total_minutes % 60

        summary_text = (
            f"Total Time: {total_hours}h {total_minutes}min\n"
            f"Total Earnings: {self.earnings:.2f} {self.currency}"
        )
        self.summary_label.config(text=summary_text)

    def wait_for_confirmation(self):
        self.waiting_for_confirmation = True
        if self.current_mode == "Work time":
            title = "End of work time"
            message = "End of work time.\nStart break?"
        else:
            title = "End of break time"
            message = "End of break time.\nReturn to work?"
        self.show_custom_dialog(title, message)

    def show_custom_dialog(self, title, message):
        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Center the dialog on the screen
        dialog.update_idletasks()
        width = 400
        height = 200
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Larger font for the cycle ending message
        tk.Label(dialog, text=message.split('\n')[0], font=("Arial", 16, "bold"), wraplength=350, justify="center").pack(pady=10, padx=20)
        # Smaller font for the continuation question
        tk.Label(dialog, text=message.split('\n')[1], font=("Arial", 14), wraplength=350, justify="center").pack(pady=5, padx=20)

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        def on_yes():
            dialog.destroy()
            self.waiting_for_confirmation = False
            self.move_to_next_cycle()

        def on_no():
            dialog.destroy()
            self.waiting_for_confirmation = False
            # Pause timer
            self.skip_to_next_cycle = True
            if not self.paused:
                self.toggle_pause()

        no_button = tk.Button(button_frame, text="No", command=on_no, font=("Arial", 12), width=10, bg="red", fg="white")
        no_button.pack(side="left", padx=10)

        yes_button = tk.Button(button_frame, text="Yes", command=on_yes, font=("Arial", 12), width=10, bg="green", fg="white")
        yes_button.pack(side="right", padx=10)

        # If the application is minimized, restore it to display the dialog
        if self.tracking_window.state() == "iconic":
            self.tracking_window.deiconify()
            self.tracking_window.attributes("-topmost", True)
            self.tracking_window.after(500, lambda: self.tracking_window.attributes("-topmost", False))

    def move_to_next_cycle(self):
        # Move to the next cycle
        if self.current_mode == "Work time":
            if self.break_seconds > 0:
                self.current_mode = "Break time"
                self.current_seconds = self.break_seconds
                self.warning_seconds = self.break_warning_seconds
            else:
                self.current_mode = "Work time"
                self.current_seconds = self.work_seconds
                self.warning_seconds = self.work_warning_seconds
        else:
            self.current_mode = "Work time"
            self.current_seconds = self.work_seconds
            self.warning_seconds = self.work_warning_seconds

        self.elapsed = 0
        self.warning_triggered = False
        self.cycle_label.config(text=self.current_mode)
        self.update_window_title()
        self.cycle_time_label.config(fg="black")
        self.state = "counting"

    def end_of_workday(self):
        self.running = False
        self.tracking_window.destroy()
        # Display custom summary window
        self.show_summary_window()
        self.root.deiconify()
        self.update_summary_label()

    def show_summary_window(self):
        summary_window = tk.Toplevel()
        summary_window.title("End of Workday Summary")
        summary_window.geometry("500x450")
        summary_window.resizable(False, False)
        summary_window.configure(bg="#f0f0f0")

        # Center the window on the screen
        summary_window.update_idletasks()
        width = 500
        height = 450
        x = (summary_window.winfo_screenwidth() // 2) - (width // 2)
        y = (summary_window.winfo_screenheight() // 2) - (height // 2)
        summary_window.geometry(f"{width}x{height}+{x}+{y}")

        # Success icon (you can replace this with an image)
        success_label = tk.Label(summary_window, text="🎉", font=("Arial", 50), bg="#f0f0f0")
        success_label.pack(pady=(20, 10))

        # Bold text "Your workday has ended."
        title_text = "Congratulations!\nYour workday has ended."
        title_label = tk.Label(summary_window, text=title_text, font=("Arial", 24, "bold"), bg="#f0f0f0", justify="center")
        title_label.pack(pady=(0, 10))

        # Calculate times
        total_minutes = self.total_seconds // 60
        total_hours = total_minutes // 60
        total_minutes = total_minutes % 60

        # Summary text
        summary_text = (
            f"Total Time: {total_hours}h {total_minutes}min\n"
            f"Total Earnings: {self.earnings:.2f} {self.currency}"
        )

        summary_label = tk.Label(summary_window, text=summary_text, font=("Arial", 16), bg="#f0f0f0", justify="center")
        summary_label.pack(pady=10, fill='both', expand=True)

        # Buttons
        button_frame = tk.Frame(summary_window, bg="#f0f0f0")
        button_frame.pack(pady=20)

        def close_summary():
            summary_window.destroy()

        ok_button = tk.Button(button_frame, text="OK", command=close_summary, font=("Arial", 14), width=10)
        ok_button.pack()

        # Prevent interaction with other windows
        summary_window.grab_set()
        summary_window.attributes("-topmost", True)

    def show_custom_notification(self, title, message):
        notification = tk.Toplevel()
        notification.title(title)
        notification.attributes("-topmost", True)
        notification.resizable(False, False)

        # Position the window in the bottom right corner
        notification.update_idletasks()
        width = 300
        height = 100
        x = notification.winfo_screenwidth() - width - 10
        y = notification.winfo_screenheight() - height - 50
        notification.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(notification, text=message, font=("Arial", 12), wraplength=280, justify="left").pack(pady=10, padx=10)

        def close_notification():
            notification.destroy()

        notification.after(10000, close_notification)

    def reset_values(self):
        # Reset all tracked values to initial
        self.total_seconds = 0
        self.total_work_seconds = 0
        self.total_break_seconds = 0
        self.earnings = 0.0
        self.summary_label.config(text="No data yet.")
        self.update_summary_label()

root = tk.Tk()
app = AdvancedTimerApp(root)
root.mainloop()
