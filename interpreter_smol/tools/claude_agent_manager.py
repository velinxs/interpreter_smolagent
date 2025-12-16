"""
Claude Agent Manager - Deploy and manage Claude Code agents

Enables the smolagents agent to deploy Claude Code agents in headless mode
for complex, autonomous tasks that benefit from Claude Opus's capabilities.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
import queue


@dataclass
class ClaudeAgentTask:
    """Specification for a Claude agent task"""
    task_id: str
    description: str
    project_path: Path
    model: str = "opus"  # opus, sonnet, haiku
    headless: bool = True
    permissions: List[str] = None  # file, bash, web, etc.
    timeout: Optional[int] = None  # seconds
    status: str = "pending"  # pending, running, completed, failed
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = ["file", "bash", "web"]  # Full permissions
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['project_path'] = str(data['project_path'])
        return data


class ClaudeAgentManager:
    """
    Manager for deploying and monitoring Claude Code agents

    Features:
    - Deploy Claude agents in headless mode
    - Grant full permissions for autonomous work
    - Monitor agent progress
    - Manage multiple concurrent agents
    - Retrieve results
    """

    def __init__(
        self,
        workspace_dir: Optional[Path] = None,
        max_concurrent_agents: int = 5,
        verbose: bool = False
    ):
        """
        Initialize ClaudeAgentManager

        Args:
            workspace_dir: Directory for Claude projects
            max_concurrent_agents: Maximum number of concurrent agents
            verbose: Print detailed information
        """
        if workspace_dir is None:
            workspace_dir = Path.home() / ".interpreter_smol" / "claude_projects"

        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        self.max_concurrent_agents = max_concurrent_agents
        self.verbose = verbose

        # Task tracking
        self._tasks: Dict[str, ClaudeAgentTask] = {}
        self._processes: Dict[str, subprocess.Popen] = {}
        self._output_queues: Dict[str, queue.Queue] = {}

        # State file
        self.state_file = self.workspace_dir / "agent_state.json"
        self._load_state()

    def deploy_agent(
        self,
        task_description: str,
        project_name: Optional[str] = None,
        model: str = "opus",
        permissions: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        wait_for_completion: bool = False
    ) -> tuple[str, Optional[str]]:
        """
        Deploy a Claude Code agent for a task

        Args:
            task_description: What the agent should do
            project_name: Optional project name (auto-generated if not provided)
            model: Claude model to use (opus, sonnet, haiku)
            permissions: List of permissions to grant
            timeout: Optional timeout in seconds
            wait_for_completion: If True, wait for agent to complete before returning

        Returns:
            Tuple of (task_id, error_message)
        """
        # Check concurrent limit
        running_count = len([t for t in self._tasks.values() if t.status == "running"])
        if running_count >= self.max_concurrent_agents:
            return None, f"Maximum concurrent agents ({self.max_concurrent_agents}) reached"

        # Generate task ID and project name
        task_id = f"task_{int(time.time())}_{len(self._tasks)}"

        if project_name is None:
            project_name = f"claude_task_{task_id}"

        # Create project directory
        project_path = self.workspace_dir / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        # Set default permissions (full access)
        if permissions is None:
            permissions = ["file", "bash", "web", "edit", "write", "read"]

        # Create task
        task = ClaudeAgentTask(
            task_id=task_id,
            description=task_description,
            project_path=project_path,
            model=model,
            headless=True,
            permissions=permissions,
            timeout=timeout
        )

        self._tasks[task_id] = task

        # Initialize Claude Code project
        init_success, init_error = self._initialize_claude_project(project_path, task_description)
        if not init_success:
            task.status = "failed"
            task.error = init_error
            self._save_state()
            return task_id, init_error

        # Start agent in headless mode
        success, error = self._start_agent(task)
        if not success:
            task.status = "failed"
            task.error = error
            self._save_state()
            return task_id, error

        task.status = "running"
        task.started_at = datetime.now().isoformat()
        self._save_state()

        if self.verbose:
            print(f"[ClaudeAgent] Deployed agent '{task_id}' for task: {task_description[:50]}...")

        # Wait for completion if requested
        if wait_for_completion:
            self.wait_for_agent(task_id, timeout=timeout)

        return task_id, None

    def _initialize_claude_project(
        self,
        project_path: Path,
        task_description: str
    ) -> tuple[bool, Optional[str]]:
        """
        Initialize a Claude Code project directory

        Creates necessary files and configuration for Claude Code
        """
        try:
            # Create .claude directory
            claude_dir = project_path / ".claude"
            claude_dir.mkdir(parents=True, exist_ok=True)

            # Create task file
            task_file = project_path / "TASK.md"
            with open(task_file, 'w') as f:
                f.write(f"# Task\n\n{task_description}\n")

            # Create README
            readme_file = project_path / "README.md"
            with open(readme_file, 'w') as f:
                f.write(f"# Claude Agent Task\n\n{task_description}\n\n")
                f.write("This project is managed by a Claude Code agent running in headless mode.\n")

            # Create workspace directory
            workspace_dir = project_path / "workspace"
            workspace_dir.mkdir(exist_ok=True)

            return True, None

        except Exception as e:
            return False, f"Error initializing project: {e}"

    def _start_agent(self, task: ClaudeAgentTask) -> tuple[bool, Optional[str]]:
        """
        Start a Claude Code agent in headless mode

        This uses the Claude Code CLI with headless mode and full permissions
        """
        try:
            # Construct Claude Code command
            # Note: This assumes claude-code CLI is available
            # In practice, this would use the Claude Agent SDK programmatically

            cmd = [
                "claude",  # Claude Code CLI
                "--headless",  # Headless mode
                "--model", self._get_model_id(task.model),
                "--auto-approve",  # Automatically approve actions (full permissions)
                "--project", str(task.project_path),
                task.description
            ]

            # Add permission flags
            for perm in task.permissions:
                cmd.append(f"--allow-{perm}")

            if self.verbose:
                print(f"[ClaudeAgent] Starting agent with command: {' '.join(cmd)}")

            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=task.project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            self._processes[task.task_id] = process

            # Create output queue and start monitoring thread
            output_queue = queue.Queue()
            self._output_queues[task.task_id] = output_queue

            # Start output monitoring thread
            threading.Thread(
                target=self._monitor_output,
                args=(task.task_id, process, output_queue),
                daemon=True
            ).start()

            return True, None

        except FileNotFoundError:
            return False, "Claude Code CLI not found. Please install Claude Code."
        except Exception as e:
            return False, f"Error starting agent: {e}"

    def _get_model_id(self, model: str) -> str:
        """Map model name to Claude model ID"""
        model_map = {
            "opus": "claude-opus-4-5-20251101",
            "sonnet": "claude-sonnet-4-5-20250929",
            "haiku": "claude-haiku-3-5-20241022"
        }
        return model_map.get(model, model_map["opus"])

    def _monitor_output(self, task_id: str, process: subprocess.Popen, output_queue: queue.Queue):
        """Monitor agent output in a separate thread"""
        try:
            # Read stdout
            for line in process.stdout:
                output_queue.put(("stdout", line.strip()))

            # Read stderr
            for line in process.stderr:
                output_queue.put(("stderr", line.strip()))

            # Wait for process to complete
            return_code = process.wait()

            # Update task status
            if task_id in self._tasks:
                task = self._tasks[task_id]

                if return_code == 0:
                    task.status = "completed"
                    task.result = self._collect_results(task.project_path)
                else:
                    task.status = "failed"
                    task.error = f"Agent exited with code {return_code}"

                task.completed_at = datetime.now().isoformat()
                self._save_state()

        except Exception as e:
            if task_id in self._tasks:
                self._tasks[task_id].status = "failed"
                self._tasks[task_id].error = f"Monitoring error: {e}"
                self._save_state()

    def _collect_results(self, project_path: Path) -> str:
        """Collect results from a completed agent task"""
        results = []

        # Check for result files
        result_file = project_path / "RESULT.md"
        if result_file.exists():
            with open(result_file, 'r') as f:
                results.append(f.read())

        # Check for created files
        workspace_dir = project_path / "workspace"
        if workspace_dir.exists():
            files = list(workspace_dir.rglob("*"))
            if files:
                results.append(f"\nCreated {len(files)} file(s) in workspace")

        return "\n".join(results) if results else "Agent completed (no explicit results)"

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task"""
        task = self._tasks.get(task_id)
        if task is None:
            return None

        status = task.to_dict()

        # Add live output if available
        if task_id in self._output_queues:
            recent_output = []
            q = self._output_queues[task_id]

            # Get up to 20 recent lines
            for _ in range(min(20, q.qsize())):
                try:
                    stream, line = q.get_nowait()
                    recent_output.append(f"[{stream}] {line}")
                except queue.Empty:
                    break

            status['recent_output'] = recent_output

        return status

    def wait_for_agent(self, task_id: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for an agent to complete

        Args:
            task_id: Task ID
            timeout: Optional timeout in seconds

        Returns:
            True if completed successfully, False otherwise
        """
        if task_id not in self._tasks:
            return False

        if task_id not in self._processes:
            return self._tasks[task_id].status == "completed"

        try:
            process = self._processes[task_id]
            process.wait(timeout=timeout)
            return self._tasks[task_id].status == "completed"

        except subprocess.TimeoutExpired:
            # Timeout reached
            self._tasks[task_id].status = "failed"
            self._tasks[task_id].error = "Timeout exceeded"
            self._tasks[task_id].completed_at = datetime.now().isoformat()
            self._save_state()
            return False

    def stop_agent(self, task_id: str) -> bool:
        """Stop a running agent"""
        if task_id not in self._processes:
            return False

        try:
            process = self._processes[task_id]
            process.terminate()

            # Wait a bit for graceful termination
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            self._tasks[task_id].status = "failed"
            self._tasks[task_id].error = "Stopped by user"
            self._tasks[task_id].completed_at = datetime.now().isoformat()
            self._save_state()

            return True

        except Exception as e:
            if self.verbose:
                print(f"[ClaudeAgent] Error stopping agent: {e}")
            return False

    def get_agent_output(self, task_id: str, lines: int = 50) -> List[str]:
        """Get recent output from an agent"""
        if task_id not in self._output_queues:
            return []

        q = self._output_queues[task_id]
        output = []

        for _ in range(min(lines, q.qsize())):
            try:
                stream, line = q.get_nowait()
                output.append(f"[{stream}] {line}")
            except queue.Empty:
                break

        return output

    def list_tasks(
        self,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all tasks

        Args:
            status: Optional filter by status (pending, running, completed, failed)

        Returns:
            List of task summaries
        """
        tasks = []

        for task in self._tasks.values():
            if status is None or task.status == status:
                tasks.append({
                    'task_id': task.task_id,
                    'description': task.description[:100] + "..." if len(task.description) > 100 else task.description,
                    'status': task.status,
                    'model': task.model,
                    'created_at': task.created_at,
                    'started_at': task.started_at,
                    'completed_at': task.completed_at
                })

        return tasks

    def get_task_result(self, task_id: str) -> Optional[str]:
        """Get the result of a completed task"""
        task = self._tasks.get(task_id)
        if task is None:
            return None

        if task.status != "completed":
            return f"Task status: {task.status}"

        return task.result

    def cleanup_task(self, task_id: str, delete_project: bool = False):
        """Clean up a task"""
        if task_id not in self._tasks:
            return

        # Stop if running
        if task_id in self._processes:
            self.stop_agent(task_id)

        # Remove from tracking
        task = self._tasks[task_id]
        del self._tasks[task_id]

        if task_id in self._processes:
            del self._processes[task_id]

        if task_id in self._output_queues:
            del self._output_queues[task_id]

        # Delete project directory if requested
        if delete_project and task.project_path.exists():
            import shutil
            shutil.rmtree(task.project_path)

        self._save_state()

    def _save_state(self):
        """Save task state to disk"""
        state = {
            'tasks': {
                task_id: task.to_dict()
                for task_id, task in self._tasks.items()
            }
        }

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def _load_state(self):
        """Load task state from disk"""
        if not self.state_file.exists():
            return

        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)

            for task_id, task_data in state.get('tasks', {}).items():
                task_data['project_path'] = Path(task_data['project_path'])
                task = ClaudeAgentTask(**task_data)

                # Only load non-running tasks
                if task.status != "running":
                    self._tasks[task_id] = task

        except Exception as e:
            if self.verbose:
                print(f"[ClaudeAgent] Error loading state: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about agent usage"""
        total = len(self._tasks)
        completed = len([t for t in self._tasks.values() if t.status == "completed"])
        running = len([t for t in self._tasks.values() if t.status == "running"])
        failed = len([t for t in self._tasks.values() if t.status == "failed"])

        return {
            'total_tasks': total,
            'completed': completed,
            'running': running,
            'failed': failed,
            'success_rate': (completed / total * 100) if total > 0 else 0
        }


# Convenience function for quick agent deployment
def deploy_claude_agent(
    task: str,
    model: str = "opus",
    wait: bool = False,
    workspace_dir: Optional[Path] = None
) -> tuple[str, Optional[str]]:
    """
    Quick deployment of a Claude agent

    Args:
        task: Task description
        model: Model to use (opus, sonnet, haiku)
        wait: Whether to wait for completion
        workspace_dir: Optional workspace directory

    Returns:
        Tuple of (task_id, error_message)
    """
    manager = ClaudeAgentManager(workspace_dir=workspace_dir, verbose=True)
    return manager.deploy_agent(
        task_description=task,
        model=model,
        wait_for_completion=wait
    )
