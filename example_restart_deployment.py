#!/usr/bin/env python3
"""Example script showing how to restart Docker deployment with a different image during SWE-Agent run."""

from pathlib import Path
from sweagent.environment.swe_env import EnvironmentConfig, SWEEnv
from sweagent.agent.problem_statement import EmptyProblemStatement
from swerex.deployment.config import DockerDeploymentConfig


def example_restart_during_run():
    """Example of restarting deployment with different image during agent run."""
    
    # Create initial environment config
    env_config = EnvironmentConfig(
        deployment=DockerDeploymentConfig(
            image="python:3.11",
            python_standalone_dir="/root"
        ),
        repo=None,  # No repo for this example
        post_startup_commands=["echo 'Initial environment setup'"],
        name="main"
    )
    
    # Create environment
    env = SWEEnv.from_config(env_config)
    
    # Start the environment
    env.start()
    
    # Run some commands in the initial environment
    print("Running commands in initial environment...")
    result = env.communicate("python --version")
    print(f"Python version: {result}")
    
    # Now restart with a different image
    print("\nRestarting with different image...")
    env.restart_deployment_with_image("python:3.12", preserve_repo_state=True)
    
    # Run commands in the new environment
    print("Running commands in new environment...")
    result = env.communicate("python --version")
    print(f"Python version: {result}")
    
    # Example with custom deployment config
    print("\nRestarting with custom deployment config...")
    from swerex.deployment.config import DockerDeploymentConfig
    custom_config = DockerDeploymentConfig(
        image="ubuntu:22.04",
        docker_args=["--memory=2g"],
        python_standalone_dir="/root"
    )
    env.restart_deployment_with_config(custom_config, preserve_repo_state=True)
    
    # Run commands in the custom environment
    print("Running commands in custom environment...")
    result = env.communicate("cat /etc/os-release | head -1")
    print(f"OS: {result}")
    
    # Clean up
    env.close()
    print("\nEnvironment closed successfully!")


def example_in_agent_run():
    """Example of how to integrate restart functionality into an agent run."""
    
    # Create a custom agent that can restart deployment
    class RestartCapableAgent:
        def __init__(self, env: SWEEnv):
            self.env = env
            self.step_count = 0
        
        def run(self, problem_statement, env, output_dir):
            """Example agent run with deployment restart capability."""
            
            # Simulate some agent steps
            for step in range(5):
                self.step_count += 1
                print(f"Agent step {self.step_count}")
                
                # Example: restart deployment after step 2
                if self.step_count == 2:
                    print("Restarting deployment with different image...")
                    self.env.restart_deployment_with_image("python:3.12")
                
                # Continue with agent logic
                result = self.env.communicate(f"echo 'Step {self.step_count} completed'")
                print(f"Step result: {result}")
            
            return {"status": "completed", "steps": self.step_count}
    
    # Create environment
    env_config = EnvironmentConfig(
        deployment=DockerDeploymentConfig(
            image="python:3.11",
            python_standalone_dir="/root"
        ),
        repo=None,
        post_startup_commands=["echo 'Agent environment setup'"],
    )
    env = SWEEnv.from_config(env_config)
    
    # Create agent
    agent = RestartCapableAgent(env)
    
    # Run agent
    problem_statement = EmptyProblemStatement()
    result = agent.run(problem_statement, env, Path("output"))
    
    print(f"Agent completed with result: {result}")
    
    # Clean up
    env.close()


if __name__ == "__main__":
    print("=== Example 1: Basic restart functionality ===")
    example_restart_during_run()
    
    print("\n=== Example 2: Restart during agent run ===")
    example_in_agent_run() 