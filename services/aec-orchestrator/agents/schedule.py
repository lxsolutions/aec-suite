



import sympy as sp
from datetime import datetime, timedelta

def generate_gantt_chart(project_tasks: dict):
    """Generate Gantt chart data for project scheduling."""

    # Example task structure:
    # tasks = {
    #     "Foundation": {"duration_days": 30},
    #     "Structure": {"duration_days": 45, "dependencies": ["Foundation"]},
    #     "Interiors": {"duration_days": 60, "dependencies": ["Structure"]}
    # }

    task_names = list(project_tasks.keys())
    durations = [task["duration_days"] for task in project_tasks.values()]

    # Calculate start dates based on dependencies
    start_dates = {}
    current_date = datetime.now()

    for task_name in task_names:
        task = project_tasks[task_name]
        deps = task.get("dependencies", [])

        if not deps:
            # No dependencies, start immediately
            start_dates[task_name] = current_date
        else:
            # Start after all dependencies are complete
            dep_end_dates = [start_dates[dep] + timedelta(days=project_tasks[dep]["duration_days"]) for dep in deps]
            start_dates[task_name] = max(dep_end_dates)

    # Generate Gantt chart data
    gantt_data = []
    for task_name, start_date in start_dates.items():
        duration = project_tasks[task_name]["duration_days"]
        end_date = start_date + timedelta(days=duration)
        gantt_data.append({
            "task": task_name,
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "duration_days": duration
        })

    total_duration = (max([start_dates[dep] + timedelta(days=project_tasks[dep]["duration_days"]) for dep in task_names]) - current_date).days

    return {
        "gantt_chart": gantt_data,
        "total_project_duration_days": int(total_duration),
        "estimated_completion_date": (current_date + timedelta(days=int(total_duration))).strftime("%Y-%m-%d")
    }

if __name__ == "__main__":
    # Example usage
    sample_tasks = {
        "Foundation": {"duration_days": 30},
        "Structure": {"duration_days": 45, "dependencies": ["Foundation"]},
        "Interiors": {"duration_days": 60, "dependencies": ["Structure"]}
    }

    result = generate_gantt_chart(sample_tasks)
    print(f"Gantt chart generated: {result}")


