import tkinter as tk
from tkinter import ttk, messagebox
import uuid
import heapq

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.waiting_time = 0
        self.turnaround_time = 0
        self.start_time = None
        self.completion_time = None

    def __lt__(self, other):
        # Priority Queue: smaller priority value = higher priority
        return self.priority < other.priority if self.priority != other.priority else self.arrival_time < other.arrival_time

class PrioritySchedulingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Priority Scheduling Simulator")
        self.root.geometry("900x700")
        self.root.resizable(False, False)  # Fixed window size
        self.root.configure(bg="#f0f2f5")  # Light gray background
        
        # Apply modern theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", font=("Helvetica", 10), background="#f0f2f5")
        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=8, background="#4a90e2", foreground="white")
        style.map("TButton", background=[("active", "#357abd")])
        style.configure("TLabelFrame", font=("Helvetica", 12, "bold"), background="#f0f2f5")
        style.configure("TLabelFrame.Label", font=("Helvetica", 12, "bold"), background="#f0f2f5")
        style.configure("TFrame", background="#f0f2f5")
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
        
        # List to store processes and schedule
        self.processes = []
        self.schedule = []
        self.scheduling_mode = tk.StringVar(value="Non-Preemptive")
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Input Frame with border effect
        input_border = tk.Frame(self.root, bg="#d9dfe5", bd=2)
        input_border.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        input_frame = ttk.LabelFrame(input_border, text="Add New Process", padding=(15, 10))
        input_frame.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        
        # Scheduling Mode Selection
        mode_frame = ttk.Frame(input_frame)
        mode_frame.grid(row=0, column=0, columnspan=8, pady=5, sticky="w")
        ttk.Label(mode_frame, text="Scheduling Mode:").grid(row=0, column=0, padx=(0, 5), pady=5)
        ttk.Radiobutton(mode_frame, text="Non-Preemptive", value="Non-Preemptive", variable=self.scheduling_mode).grid(row=0, column=1, padx=5, pady=5)
        ttk.Radiobutton(mode_frame, text="Preemptive", value="Preemptive", variable=self.scheduling_mode).grid(row=0, column=2, padx=5, pady=5)
        
        # Input Fields
        fields = [
            ("Process ID:", "pid_entry", "Optional"),
            ("Arrival Time:", "arrival_entry", "e.g., 0"),
            ("Burst Time:", "burst_entry", "e.g., 5"),
            ("Priority:", "priority_entry", "Lower = Higher Priority")
        ]
        
        for i, (label, entry_name, placeholder) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=1, column=i*2, padx=(0, 10), pady=(0, 10), sticky="w")
            entry = ttk.Entry(input_frame, width=15, font=("Helvetica", 10))
            entry.grid(row=1, column=i*2+1, padx=(0, 10), pady=(0, 10))
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e, entry=entry, placeholder=placeholder: self.clear_placeholder(e, entry, placeholder))
            entry.bind("<FocusOut>", lambda e, entry=entry, placeholder=placeholder: self.restore_placeholder(e, entry, placeholder))
            setattr(self, entry_name, entry)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=8, pady=10)
        ttk.Button(button_frame, text="Add Process", command=self.add_process).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(button_frame, text="Calculate Schedule", command=self.calculate_schedule).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(button_frame, text="About", command=self.show_about).grid(row=0, column=3, padx=5, pady=5)
        
        # Process Table
        self.tree = ttk.Treeview(self.root, columns=("PID", "Arrival Time", "Burst Time", "Priority", "Waiting Time", "Turnaround Time"), show="headings")
        self.tree.heading("PID", text="Process ID")
        self.tree.heading("Arrival Time", text="Arrival Time")
        self.tree.heading("Burst Time", text="Burst Time")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Waiting Time", text="Waiting Time")
        self.tree.heading("Turnaround Time", text="Turnaround Time")
        for col in ("PID", "Arrival Time", "Burst Time", "Priority", "Waiting Time", "Turnaround Time"):
            self.tree.column(col, width=100, anchor="center")
        self.tree.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        
        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Gantt Chart Frame with border effect
        gantt_border = tk.Frame(self.root, bg="#d9dfe5", bd=2)
        gantt_border.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        self.gantt_frame = ttk.LabelFrame(gantt_border, text="Gantt Chart", padding=(15, 10))
        self.gantt_frame.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        self.canvas = tk.Canvas(self.gantt_frame, height=120, bg="white", bd=0)
        self.canvas.grid(row=0, column=0, sticky="ew")
        
        # Results Label
        self.result_label = ttk.Label(self.root, text="", font=("Helvetica", 11), background="#f0f2f5")
        self.result_label.grid(row=3, column=0, padx=15, pady=(10, 15))
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.gantt_frame.grid_columnconfigure(0, weight=1)
        
    def show_about(self):
        # Create a new Toplevel window for the About section
        about_window = tk.Toplevel(self.root)
        about_window.title("About Priority Scheduling Simulator")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.configure(bg="#f0f2f5")
        
        # About content
        ttk.Label(
            about_window,
            text="Priority Scheduling Simulator",
            font=("Helvetica", 14, "bold"),
            background="#f0f2f5"
        ).pack(pady=10)
        
        ttk.Label(
            about_window,
            text="Developed by Group #2",
            font=("Helvetica", 12),
            background="#f0f2f5"
        ).pack(pady=5)
        
        ttk.Label(
            about_window,
            text="Group Members:",
            font=("Helvetica", 11, "bold"),
            background="#f0f2f5"
        ).pack(pady=5)
        
        members = [
            "Cabael, Ben Jiru",
            "Copioso, Mark Rainier S.",
            "Castillo, John Paul",
            "Centeno, John Michael",
            "Yolola, Lenar Andrei P.",
            "Sulte, Steven",
            "Valdesco, Apple",
            "Verana, Naomi",
            "Tan, Samantha",
            "Wagan, Rowena"
        ]
        
        for member in members:
            ttk.Label(
                about_window,
                text=member,
                font=("Helvetica", 10),
                background="#f0f2f5"
            ).pack(pady=2)
        
        ttk.Label(
            about_window,
            text="Course: Operating Systems\nSemester: Spring 2025\nInstitution: [Your University]",
            font=("Helvetica", 10),
            background="#f0f2f5",
            justify="center"
        ).pack(pady=10)
        
        # Close button
        ttk.Button(
            about_window,
            text="Close",
            command=about_window.destroy
        ).pack(pady=10)
        
    def clear_placeholder(self, event, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
    
    def restore_placeholder(self, event, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            
    def add_process(self):
        try:
            pid = self.pid_entry.get()
            if pid == "Optional":
                pid = ""
            arrival_time_str = self.arrival_entry.get()
            burst_time_str = self.burst_entry.get()
            priority_str = self.priority_entry.get()
            
            if arrival_time_str == "e.g., 0":
                arrival_time_str = ""
            if burst_time_str == "e.g., 5":
                burst_time_str = ""
            if priority_str == "Lower = Higher Priority":
                priority_str = ""
                
            if not pid:
                pid = str(uuid.uuid4())[:8]
            if not arrival_time_str:
                raise ValueError("Arrival time is required")
            if not burst_time_str:
                raise ValueError("Burst time is required")
            if not priority_str:
                raise ValueError("Priority is required")
                
            arrival_time = float(arrival_time_str)
            burst_time = float(burst_time_str)
            priority = int(priority_str)
            
            if arrival_time < 0:
                raise ValueError("Arrival time must be non-negative")
            if burst_time <= 0:
                raise ValueError("Burst time must be positive")
            if priority < 0:
                raise ValueError("Priority must be non-negative")
                
            # Add process to list and treeview
            self.processes.append(Process(pid, arrival_time, burst_time, priority))
            self.tree.insert("", "end", values=(pid, arrival_time, burst_time, priority, 0, 0))
            
            # Clear entries
            self.pid_entry.delete(0, tk.END)
            self.pid_entry.insert(0, "Optional")
            self.arrival_entry.delete(0, tk.END)
            self.arrival_entry.insert(0, "e.g., 0")
            self.burst_entry.delete(0, tk.END)
            self.burst_entry.insert(0, "e.g., 5")
            self.priority_entry.delete(0, tk.END)
            self.priority_entry.insert(0, "Lower = Higher Priority")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
            
    def calculate_schedule(self):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to schedule")
            return
            
        # Clear previous Gantt chart and schedule
        self.canvas.delete("all")
        self.schedule = []
        
        if self.scheduling_mode.get() == "Non-Preemptive":
            self.calculate_non_preemptive()
        else:
            self.calculate_preemptive()
            
        # Update treeview
        self.tree.delete(*self.tree.get_children())
        for process in self.processes:
            self.tree.insert("", "end", values=(
                process.pid,
                process.arrival_time,
                process.burst_time,
                process.priority,
                process.waiting_time,
                process.turnaround_time
            ))
        
        # Draw Gantt chart
        self.draw_gantt_chart()
        
    def calculate_non_preemptive(self):
        current_time = 0
        completed = []
        total_waiting = 0
        total_turnaround = 0
        remaining_processes = self.processes.copy()
        
        while remaining_processes:
            # Get available processes
            available = [p for p in remaining_processes if p.arrival_time <= current_time]
            
            if not available:
                next_arrival = min(p.arrival_time for p in remaining_processes)
                self.schedule.append({"pid": "Idle", "start": current_time, "end": next_arrival})
                current_time = next_arrival
                continue
            
            # Select process with highest priority
            current_process = min(available, key=lambda x: x.priority)
            
            # Calculate times
            current_process.waiting_time = current_time - current_process.arrival_time
            current_process.turnaround_time = current_process.waiting_time + current_process.burst_time
            total_waiting += current_process.waiting_time
            total_turnaround += current_process.turnaround_time
            
            # Add to schedule
            self.schedule.append({
                "pid": current_process.pid,
                "start": current_time,
                "end": current_time + current_process.burst_time
            })
            
            # Update current time
            current_time += current_process.burst_time
            
            # Move process to completed
            completed.append(current_process)
            remaining_processes.remove(current_process)
        
        # Restore processes
        self.processes = completed
        
        # Display average times
        avg_waiting = total_waiting / len(self.processes) if self.processes else 0
        avg_turnaround = total_turnaround / len(self.processes) if self.processes else 0
        self.result_label.config(text=f"Average Waiting Time: {avg_waiting:.2f} | Average Turnaround Time: {avg_turnaround:.2f}")
        
    def calculate_preemptive(self):
        current_time = 0
        completed = []
        total_waiting = 0
        total_turnaround = 0
        ready_queue = []
        current_process = None
        remaining_processes = self.processes.copy()
        
        # Initialize process attributes
        for process in remaining_processes:
            process.remaining_time = process.burst_time
            process.start_time = None
            process.completion_time = None
        
        while len(completed) < len(self.processes):
            # Add newly arrived processes to ready queue
            for proc in remaining_processes[:]:  # Use slice to avoid modifying during iteration
                if proc.arrival_time <= current_time:
                    heapq.heappush(ready_queue, proc)
                    remaining_processes.remove(proc)
            
            # Push current process back to queue if it exists and not completed
            if current_process and current_process.remaining_time > 0:
                heapq.heappush(ready_queue, current_process)
            
            if ready_queue:
                next_process = heapq.heappop(ready_queue)
                
                # Record start time if first execution
                if next_process.start_time is None:
                    next_process.start_time = current_time
                
                # Add to schedule (for Gantt chart)
                if not self.schedule or self.schedule[-1]["pid"] != next_process.pid or self.schedule[-1]["end"] < current_time:
                    self.schedule.append({"pid": next_process.pid, "start": current_time, "end": current_time + 1})
                else:
                    self.schedule[-1]["end"] = current_time + 1
                
                # Execute for one time unit
                next_process.remaining_time -= 1
                
                if next_process.remaining_time == 0:
                    next_process.completion_time = current_time + 1
                    next_process.turnaround_time = next_process.completion_time - next_process.arrival_time
                    next_process.waiting_time = next_process.turnaround_time - next_process.burst_time
                    total_waiting += next_process.waiting_time
                    total_turnaround += next_process.turnaround_time
                    completed.append(next_process)
                    current_process = None
                else:
                    current_process = next_process
            else:
                # CPU is idle
                if not self.schedule or self.schedule[-1]["pid"] != "Idle":
                    self.schedule.append({"pid": "Idle", "start": current_time, "end": current_time + 1})
                else:
                    self.schedule[-1]["end"] = current_time + 1
                current_process = None
            
            current_time += 1
        
        # Restore processes
        self.processes = completed
        
        # Display average times
        avg_waiting = total_waiting / len(self.processes) if self.processes else 0
        avg_turnaround = total_turnaround / len(self.processes) if self.processes else 0
        self.result_label.config(text=f"Average Waiting Time: {avg_waiting:.2f} | Average Turnaround Time: {avg_turnaround:.2f}")
        
    def draw_gantt_chart(self):
        if not self.schedule:
            return
            
        # Canvas dimensions
        canvas_width = 820
        canvas_height = 120
        self.canvas.config(width=canvas_width)
        
        # Calculate total time for scaling
        total_time = max(segment["end"] for segment in self.schedule)
        if total_time == 0:
            return
            
        scale = (canvas_width - 70) / total_time  # 70 pixels for labels
        y_start = 40
        bar_height = 40
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEEAD", "#D4A5A5"]  # Modern color palette
        
        # Draw background grid
        self.canvas.create_rectangle(50, 20, canvas_width - 20, canvas_height - 20, fill="white", outline="#d9dfe5")
        
        # Draw time labels and grid lines
        for t in range(0, int(total_time) + 1):
            x = 50 + t * scale
            self.canvas.create_line(x, y_start - 10, x, y_start + bar_height + 10, fill="#d9dfe5", dash=(2, 2))
            self.canvas.create_text(x, y_start - 15, text=str(t), font=("Helvetica", 9), fill="#333333")
        
        # Draw process bars
        pid_to_color = {}
        color_index = 0
        for segment in self.schedule:
            pid = segment["pid"]
            if pid != "Idle" and pid not in pid_to_color:
                pid_to_color[pid] = colors[color_index % len(colors)]
                color_index += 1
            color = pid_to_color.get(pid, "#e0e0e0")  # Use gray for Idle
            x_start = 50 + segment["start"] * scale
            x_end = 50 + segment["end"] * scale
            self.canvas.create_rectangle(x_start, y_start, x_end, y_start + bar_height, fill=color, outline="#333333")
            # Only show text if segment is wide enough
            if x_end - x_start > 20:
                text_x = (x_start + x_end) / 2
                text_y = y_start + bar_height / 2
                self.canvas.create_text(text_x, text_y, text=pid, font=("Helvetica", 10, "bold"), fill="#333333")
        
        # Draw Y-axis label
        self.canvas.create_text(30, y_start + bar_height / 2, text="Processes", angle=90, font=("Helvetica", 10, "bold"), fill="#333333")
        
    def clear_all(self):
        self.processes = []
        self.schedule = []
        self.tree.delete(*self.tree.get_children())
        self.canvas.delete("all")
        self.result_label.config(text="")
        self.pid_entry.delete(0, tk.END)
        self.pid_entry.insert(0, "Optional")
        self.arrival_entry.delete(0, tk.END)
        self.arrival_entry.insert(0, "e.g., 0")
        self.burst_entry.delete(0, tk.END)
        self.burst_entry.insert(0, "e.g., 5")
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, "Lower = Higher Priority")

if __name__ == "__main__":
    root = tk.Tk()
    app = PrioritySchedulingApp(root)
    root.mainloop()