# Docker Deployment Restart Functionality

This document explains how to restart Docker deployments with different images during the middle of a SWE-Agent run.

## Overview

The `SWEEnv` class now includes two new methods that allow you to restart the Docker deployment with a different image while preserving the environment state:

1. `restart_deployment_with_image(new_image: str, preserve_repo_state: bool = False)` - Restart with just a different image
2. `restart_deployment_with_config(new_deployment_config: DockerDeploymentConfig, preserve_repo_state: bool = False)` - Restart with a complete new deployment configuration

## Basic Usage

### Simple Image Change

```python
from sweagent.environment.swe_env import SWEEnv, EnvironmentConfig
from swerex.deployment.config import DockerDeploymentConfig

# Create initial environment
env_config = EnvironmentConfig(
    deployment=DockerDeploymentConfig(
        image="python:3.11",
        python_standalone_dir="/root"
    ),
    repo=None,
    post_startup_commands=["echo 'Initial setup'"]
)

env = SWEEnv.from_config(env_config)
env.start()

# Run some commands
result = env.communicate("python --version")
print(f"Initial Python: {result}")

# Restart with different image (preserving repo state)
env.restart_deployment_with_image("python:3.12", preserve_repo_state=True)

# Continue with new environment
result = env.communicate("python --version")
print(f"New Python: {result}")

env.close()
```

### Custom Deployment Configuration

```python
from swerex.deployment.config import DockerDeploymentConfig

# Create custom deployment config
custom_config = DockerDeploymentConfig(
    image="ubuntu:22.04",
    docker_args=["--memory=2g", "--cpus=2"],
    python_standalone_dir="/root",
    platform="linux/amd64"
)

# Restart with custom config (preserving repo state)
env.restart_deployment_with_config(custom_config, preserve_repo_state=True)
```

## Integration with Agents

### Method 1: Direct Integration

```python
class MyAgent:
    def run(self, problem_statement, env, output_dir):
        # Your agent logic here
        
        # Check if restart is needed
        if self.needs_different_environment():
            env.restart_deployment_with_image("python:3.12", preserve_repo_state=True)
        
        # Continue with agent logic
        # ...
```

### Method 2: Conditional Restart

```python
class AgentWithRestartCapability:
    def __init__(self):
        self.restart_conditions = {
            "needs_python_3_12": "python:3.12",
            "needs_gpu": "nvidia/cuda:11.8-devel-ubuntu22.04",
            "needs_memory": "python:3.11-slim"
        }
    
    def should_restart(self, current_step):
        # Your logic to determine if restart is needed
        if "needs_python_3_12" in current_step:
            return self.restart_conditions["needs_python_3_12"]
        return None
    
    def run(self, problem_statement, env, output_dir):
        for step in self.steps:
            # Check if restart is needed
            new_image = self.should_restart(step)
            if new_image:
                env.restart_deployment_with_image(new_image, preserve_repo_state=True)
            
            # Execute step
            # ...
```

## What Happens During Restart

When you call either restart method, the following sequence occurs:

1. **Store Current State**: The current repository reference is preserved
2. **Close Current Deployment**: The existing Docker container is stopped and removed
3. **Create New Deployment**: A new deployment is created with the specified configuration
4. **Reinitialize**: The new deployment is started and initialized
5. **Repository Handling**: 
   - If `preserve_repo_state=True`: Only copy the repository if it doesn't exist, don't reset it
   - If `preserve_repo_state=False` (default): Copy and reset the repository to clean state
6. **Re-run Post-Startup Commands**: Any post-startup commands are re-executed

### Repository State Preservation

The `preserve_repo_state` parameter controls how the repository is handled during restart:

- **`preserve_repo_state=False`** (default): Behaves like the original `reset()` method - copies the repository and resets it to the base commit, losing any uncommitted changes
- **`preserve_repo_state=True`**: Only copies the repository if it doesn't exist in the new container, preserving any existing repository state and uncommitted changes

## Important Notes

### Repository State
- **With `preserve_repo_state=False`** (default):
  - The repository will be re-copied to the new container
  - The repository will be reset to its base commit state
  - Any uncommitted changes will be lost
- **With `preserve_repo_state=True`**:
  - The repository will only be copied if it doesn't exist in the new container
  - The repository state will be preserved (including uncommitted changes)
  - Any existing repository state in the new container will be maintained

### Environment Variables
- Environment variables set via `set_env_variables()` will need to be re-set after restart
- The basic environment variables (LANG, LC_ALL) are automatically re-set

### Session State
- Any running processes or shell sessions will be terminated
- You'll need to re-establish any long-running processes

### Post-Startup Commands
- All post-startup commands from the original configuration will be re-executed
- This ensures the new environment is properly set up

## Error Handling

The restart methods include error handling and logging:

```python
try:
    env.restart_deployment_with_image("python:3.12")
    print("Restart successful")
except Exception as e:
    print(f"Restart failed: {e}")
    # Handle error appropriately
```

## Examples

See the following example files for complete working examples:

- `example_restart_deployment.py` - Basic restart functionality
- `example_agent_with_restart.py` - Integration with agent workflow

## Running Examples

```bash
# Basic restart example
python example_restart_deployment.py

# Agent with restart capability
python example_agent_with_restart.py
```

## Troubleshooting

### Common Issues

1. **Image not found**: Ensure the new image exists and is accessible
2. **Port conflicts**: The new deployment will use a different port automatically
3. **Repository not found**: Ensure the repository configuration is correct
4. **Timeout issues**: Increase `startup_timeout` in deployment config if needed

### Debugging

Enable debug logging to see detailed restart information:

```python
import logging
logging.getLogger("swea-env").setLevel(logging.DEBUG)
``` 