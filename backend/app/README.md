Backend notes:
- DATA_ROOT is where .tar.gz files are stored (default "data")
- OUTPUT_ROOT is where per-task outputs are written (default "storage")
- Use API /api/files/list to see files
- Use /api/tasks/start with JSON {"files":["rack1_2024-10-01.tar.gz"]} to start
- Check progress via WebSocket /ws/progress or /api/tasks/{task_id}/progress
