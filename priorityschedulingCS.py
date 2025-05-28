import heapq
import uuid

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

def calculate_non_preemptive(processes):
    current_time = 0.0
    completed = []
    remaining_processes = processes.copy()
    
    while remaining_processes:
        available = [p for p in remaining_processes if p.arrival_time <= current_time]
        if not available:
            next_arrival = min(p.arrival_time for p in remaining_processes)
            current_time = next_arrival
            continue
        current_process = min(available, key=lambda x: x.priority)
        current_process.waiting_time = current_time - current_process.arrival_time
        current_process.turnaround_time = current_process.waiting_time + current_process.burst_time
        current_time += current_process.burst_time
        current_process.completion_time = current_time  # Set completion time
        completed.append(current_process)
        remaining_processes.remove(current_process)
    
    processes[:] = completed

def calculate_preemptive(processes):
    current_time = 0.0
    completed = []
    ready_queue = []
    current_process = None
    remaining_processes = processes.copy()
    
    for process in remaining_processes:
        process.remaining_time = process.burst_time
        process.start_time = None
        process.completion_time = None
    
    while len(completed) < len(processes):
        for proc in remaining_processes[:]:
            if proc.arrival_time <= current_time:
                heapq.heappush(ready_queue, proc)
                remaining_processes.remove(proc)
        if current_process and current_process.remaining_time > 0:
            heapq.heappush(ready_queue, current_process)
        if ready_queue:
            next_process = heapq.heappop(ready_queue)
            if next_process.start_time is None:
                next_process.start_time = current_time
            next_process.remaining_time -= 1
            if next_process.remaining_time == 0:
                next_process.completion_time = current_time + 1.0
                next_process.turnaround_time = next_process.completion_time - next_process.arrival_time
                next_process.waiting_time = next_process.turnaround_time - next_process.burst_time
                completed.append(next_process)
                current_process = None
            else:
                current_process = next_process
        else:
            current_process = None
        current_time += 1.0
    
    processes[:] = completed

def display_results(processes):
    print("\nProcess Results:")
    print(f"{'PID':<8}{'Arrival':<10}{'Burst':<8}{'Priority':<10}{'Waiting':<10}{'Turnaround':<12}{'Completion':<12}")
    for p in sorted(processes, key=lambda x: x.pid):
        completion = p.completion_time if p.completion_time is not None else 0.0
        print(f"{p.pid:<8}{p.arrival_time:<10.1f}{p.burst_time:<8.1f}{p.priority:<10}{p.waiting_time:<10.1f}{p.turnaround_time:<12.1f}{completion:<12.1f}")
    if processes:
        avg_waiting = sum(p.waiting_time for p in processes) / len(processes)
        avg_turnaround = sum(p.turnaround_time for p in processes) / len(processes)
        print(f"\nAverage Waiting Time: {avg_waiting:.2f}")
        print(f"Average Turnaround Time: {avg_turnaround:.2f}")

def main():
    processes = []
    while True:
        print("\n--- Priority Scheduling Simulator ---")
        print("1. Add Process")
        print("2. Run Non-Preemptive Schedule")
        print("3. Run Preemptive Schedule")
        print("4. Display Results")
        print("5. Clear All")
        print("6. About")
        print("7. Exit")
        
        choice = input("Select an option (1-7): ")
        
        if choice == "1":
            pid = input("Process ID (press Enter for auto): ") or str(uuid.uuid4())[:8]
            try:
                arrival = float(input("Arrival Time: "))
                burst = float(input("Burst Time: "))
                priority = int(input("Priority (lower = higher): "))
                if arrival < 0:
                    print("Error: Arrival time must be non-negative.")
                    continue
                if burst <= 0:
                    print("Error: Burst time must be positive.")
                    continue
                if priority < 0:
                    print("Error: Priority must be non-negative.")
                    continue
                processes.append(Process(pid, arrival, burst, priority))
                print(f"Process {pid} added.")
            except ValueError:
                print("Error: Invalid input. Use numeric values.")
                
        elif choice == "2":
            if not processes:
                print("Error: No processes to schedule.")
                continue
            calculate_non_preemptive(processes)
            print("Non-Preemptive schedule calculated.")
            
        elif choice == "3":
            if not processes:
                print("Error: No processes to schedule.")
                continue
            calculate_preemptive(processes)
            print("Preemptive schedule calculated.")
            
        elif choice == "4":
            if not processes:
                print("Error: No processes to display.")
                continue
            display_results(processes)
            
        elif choice == "5":
            processes.clear()
            print("All processes cleared.")
            
        elif choice == "6":
            print("\n--- About Priority Scheduling Simulator ---")
            print("Developed by Group #2")
            print("Group Members:")
            print("- Castilio, Paul Vincent")
            print("- Cabael, Ben Jiru")
            print("- Centeno, John Michael")
            print("- Copioso, Mark Rainier")
            print("Course: Operating Systems")
            
        elif choice == "7":
            print("Exiting...")
            break
            
        else:
            print("Invalid option. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    print(f"Priority Scheduling Simulator - Started at 10:38 AM PST, Wednesday, May 28, 2025")
    main()