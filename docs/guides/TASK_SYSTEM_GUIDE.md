# Task System Guide

## Overview

The Task System automatically discovers and executes Microsoft Rewards tasks beyond basic searches, including:

- **URL Reward Tasks**: Simple visit-and-earn tasks
- **Quiz Tasks**: Interactive question-based tasks
- **Poll Tasks**: Opinion poll tasks

This guide explains how to configure and use the task system.

## Configuration

### Enabling the Task System

Add the following to your `config.yaml`:

```yaml
task_system:
  enabled: true              # Enable task system
  min_delay: 2              # Minimum delay between tasks (seconds)
  max_delay: 5              # Maximum delay between tasks (seconds)
  skip_completed: true      # Skip already completed tasks
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable/disable task system |
| `min_delay` | integer | `2` | Minimum delay between tasks (seconds) |
| `max_delay` | integer | `5` | Maximum delay between tasks (seconds) |
| `skip_completed` | boolean | `true` | Skip tasks already marked as completed |

## Usage

### Basic Usage

Once enabled, the task system runs automatically as part of the main workflow:

```bash
python main.py
```

The task system will:
1. Navigate to the Microsoft Rewards dashboard
2. Discover all available tasks
3. Execute incomplete tasks sequentially
4. Report results in the execution summary

### Command Line Options

Skip task execution:
```bash
python main.py --skip-daily-tasks
```

Dry run (see what would be executed):
```bash
python main.py --dry-run
```

## Task Types

### URL Reward Tasks

Simple tasks that require visiting a URL.

**How it works:**
1. Navigate to the task URL
2. Wait for page to load
3. Check for completion indicators
4. Wait additional time for tracking scripts

**Example:**
```
Task: Visit Bing News
Points: 10
Type: urlreward
```

### Quiz Tasks

Interactive question-based tasks.

**How it works:**
1. Navigate to the quiz page
2. Detect answer options
3. Select random answers
4. Continue until quiz completes

**Example:**
```
Task: Daily Quiz
Points: 30
Type: quiz
```

**Note:** The current implementation selects random answers. Future versions may implement smarter answer selection.

### Poll Tasks

Opinion poll tasks.

**How it works:**
1. Navigate to the poll page
2. Detect poll options
3. Select a random option
4. Submit the poll

**Example:**
```
Task: Daily Poll
Points: 10
Type: poll
```


## Execution Flow

```
┌─────────────────────────────────────┐
│  Navigate to Rewards Dashboard      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Parse Task Elements                │
│  - Extract metadata                 │
│  - Identify task types              │
│  - Check completion status          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Filter Tasks                       │
│  - Skip completed (if configured)   │
│  - Skip unsupported types           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Execute Tasks Sequentially         │
│  - Execute task handler             │
│  - Add random delay                 │
│  - Track results                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Generate Execution Report          │
│  - Completed count                  │
│  - Failed count                     │
│  - Points earned                    │
└─────────────────────────────────────┘
```

## Execution Report

After task execution, you'll see a summary like:

```
Task Execution Report:
  Total: 8
  Completed: 6
  Failed: 1
  Skipped: 1
  Points Earned: 70
  Execution Time: 45.23s
```

The report includes:
- **Total**: Total number of tasks discovered
- **Completed**: Successfully completed tasks
- **Failed**: Tasks that encountered errors
- **Skipped**: Tasks skipped (already completed or unsupported)
- **Points Earned**: Total points earned from completed tasks
- **Execution Time**: Total time spent executing tasks

## Troubleshooting

### No Tasks Found

**Problem:** Task system reports "No tasks found"

**Solutions:**
1. Verify you're logged in to Microsoft Rewards
2. Check that tasks are available on the dashboard
3. Ensure your account has tasks to complete

### Tasks Failing

**Problem:** Tasks are marked as failed

**Solutions:**
1. Check logs for specific error messages
2. Verify network connectivity
3. Try running with `--mode slow` for more reliable execution
4. Some tasks may require manual intervention

### Tasks Not Executing

**Problem:** Task system is enabled but tasks don't execute

**Solutions:**
1. Verify `task_system.enabled: true` in config
2. Check that you're not using `--skip-daily-tasks` flag
3. Ensure tasks are not already completed

## Advanced Configuration

### Custom Delays

Adjust delays to match your preference:

```yaml
task_system:
  min_delay: 3    # Slower, more human-like
  max_delay: 8
```

Or faster execution:

```yaml
task_system:
  min_delay: 1    # Faster, but may be detected
  max_delay: 3
```

### Disable Completed Task Filtering

Execute all tasks regardless of completion status:

```yaml
task_system:
  skip_completed: false
```

**Note:** This may waste time on already-completed tasks.

## Extending the Task System

### Adding New Task Types

To add support for a new task type:

1. Create a new handler in `src/core/tasks/handlers/`
2. Inherit from `Task` base class
3. Implement the `execute()` method
4. Register the handler in `TaskManager`

Example:

```python
from src.core.tasks.task_base import Task, TaskMetadata
from playwright.async_api import Page

class CustomTask(Task):
    async def execute(self, page: Page) -> bool:
        # Your implementation here
        return True
```

Register in `task_manager.py`:

```python
from src.core.tasks.handlers.custom_task import CustomTask

# In _register_task_types():
self.task_registry['custom'] = CustomTask
```

## Best Practices

1. **Start with default settings**: The default configuration is optimized for reliability
2. **Monitor first runs**: Watch the first few executions to ensure tasks complete correctly
3. **Use appropriate delays**: Longer delays are more human-like but slower
4. **Check logs**: Review logs if tasks fail to understand what went wrong
5. **Keep handlers updated**: Task page structures may change; handlers may need updates

## Limitations

- **Quiz answers**: Currently selects random answers (not intelligent)
- **Complex tasks**: Some advanced task types may not be supported
- **Page structure changes**: Microsoft may change page structures, breaking parsers
- **Manual tasks**: Some tasks require manual intervention (e.g., CAPTCHA)

## Future Enhancements

Planned improvements:
- Intelligent quiz answer selection
- Support for more task types (FindClippy, etc.)
- Better completion detection
- Retry logic for failed tasks
- Task scheduling and prioritization

## Support

For issues or questions:
1. Check the logs in `logs/automator.log`
2. Review the troubleshooting section above
3. Open an issue on GitHub with logs and error messages
