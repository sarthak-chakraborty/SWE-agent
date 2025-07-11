#!/usr/bin/env python3
"""Example showing how to integrate deployment restart into an existing SWE-Agent."""

from pathlib import Path
from typing import Any, Dict
from sweagent.environment.swe_env import SWEEnv
from sweagent.agent.agents import AbstractAgent
from sweagent.agent.problem_statement import ProblemStatement


class AgentWithRestartCapability(AbstractAgent):
    """Example agent that can restart deployment with different images during execution."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.restart_conditions = {
            "python_version_needed": "python:3.12",
            "gpu_needed": "nvidia/cuda:11.8-devel-ubuntu22.04",
            "memory_intensive": "python:3.11-slim"
        }
    
    def should_restart_deployment(self, env: SWEEnv, current_step: str) -> str | None:
        """Determine if deployment should be restarted based on current step.
        
        Args:
            env: The current environment
            current_step: Description of current agent step
            
        Returns:
            New image name if restart is needed, None otherwise
        """
        # Example logic for when to restart
        if "needs_python_3_12" in current_step:
            return self.restart_conditions["python_version_needed"]
        elif "needs_gpu" in current_step:
            return self.restart_conditions["gpu_needed"]
        elif "memory_intensive_task" in current_step:
            return self.restart_conditions["memory_intensive"]
        
        return None
    
    def run(self, problem_statement: ProblemStatement, env: SWEEnv, output_dir: Path) -> Dict[str, Any]:
        """Run the agent with deployment restart capability."""
        
        # Example agent workflow
        steps = [
            "initial_setup",
            "needs_python_3_12",  # This will trigger restart
            "continue_after_restart",
            "memory_intensive_task",  # This will trigger another restart
            "final_step"
        ]
        
        results = []
        
        for i, step in enumerate(steps):
            print(f"Executing step {i+1}: {step}")
            
            # Check if we need to restart deployment
            new_image = self.should_restart_deployment(env, step)
            if new_image:
                print(f"Restarting deployment with image: {new_image}")
                env.restart_deployment_with_image(new_image, preserve_repo_state=True)
                print(f"Deployment restarted successfully with {new_image}")
            
            # Execute step logic
            try:
                # Example step execution
                if step == "initial_setup":
                    result = env.communicate("python --version")
                    print(f"Initial Python version: {result}")
                
                elif step == "needs_python_3_12":
                    result = env.communicate("python --version")
                    print(f"Python version after restart: {result}")
                
                elif step == "continue_after_restart":
                    result = env.communicate("echo 'Continuing after restart'")
                    print(f"Step result: {result}")
                
                elif step == "memory_intensive_task":
                    result = env.communicate("free -h")
                    print(f"Memory info: {result}")
                
                elif step == "final_step":
                    result = env.communicate("echo 'Final step completed'")
                    print(f"Final step: {result}")
                
                results.append({"step": step, "status": "success", "result": result})
                
            except Exception as e:
                print(f"Error in step {step}: {e}")
                results.append({"step": step, "status": "error", "error": str(e)})
        
        return {
            "status": "completed",
            "steps": results,
            "total_steps": len(steps)
        }


def example_usage():
    """Example of how to use the agent with restart capability."""
    
    from sweagent.environment.swe_env import EnvironmentConfig
    from sweagent.agent.problem_statement import EmptyProblemStatement
    from swerex.deployment.config import DockerDeploymentConfig
    
    # Create environment config
    env_config = EnvironmentConfig(
        deployment=DockerDeploymentConfig(
            image="python:3.11",
            python_standalone_dir="/root"
        ),
        repo=None,
        post_startup_commands=["echo 'Environment ready'"],
    )
    
    # Create environment
    env = SWEEnv.from_config(env_config)
    
    # Create agent
    agent = AgentWithRestartCapability()
    
    # Run agent
    problem_statement = EmptyProblemStatement()
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    try:
        result = agent.run(problem_statement, env, output_dir)
        print(f"\nAgent completed successfully!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Agent failed: {e}")
    finally:
        env.close()


if __name__ == "__main__":
    example_usage() 