"""
Tool Registry - Central management for dynamic tools

Manages registration, discovery, and lifecycle of dynamically created tools.
Similar to MCP's server registry but for smolagents Python tools.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass, asdict
import importlib.util
import sys
from datetime import datetime

from .dynamic_tool_factory import ToolSpec, ToolFactory


@dataclass
class ToolMetadata:
    """Metadata about a registered tool"""
    name: str
    description: str
    version: str
    author: str
    created_at: str
    last_used: Optional[str] = None
    use_count: int = 0
    source: str = "runtime"  # runtime, file, or package
    file_path: Optional[str] = None
    tags: List[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ToolMetadata":
        if data.get('tags') is None:
            data['tags'] = []
        return cls(**data)


class ToolRegistry:
    """
    Central registry for all tools (built-in and dynamically created)

    Features:
    - Register/unregister tools
    - List and search tools
    - Persist tools to disk
    - Load tools from disk
    - Track tool usage
    """

    def __init__(
        self,
        storage_dir: Optional[Path] = None,
        auto_save: bool = True,
        verbose: bool = False
    ):
        """
        Initialize ToolRegistry

        Args:
            storage_dir: Directory to store tools (default: ~/.interpreter_smol/tools)
            auto_save: Automatically save tools when registered
            verbose: Print detailed information
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".interpreter_smol" / "tools"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.auto_save = auto_save
        self.verbose = verbose

        # Tool storage
        self._tools: Dict[str, Type] = {}  # name -> Tool class
        self._metadata: Dict[str, ToolMetadata] = {}  # name -> metadata
        self._specs: Dict[str, ToolSpec] = {}  # name -> ToolSpec

        # Registry file
        self.registry_file = self.storage_dir / "registry.json"

        # Load existing tools
        self._load_registry()

    def register_tool(
        self,
        tool_class: Type,
        metadata: Optional[ToolMetadata] = None,
        spec: Optional[ToolSpec] = None,
        overwrite: bool = False
    ) -> bool:
        """
        Register a tool in the registry

        Args:
            tool_class: The Tool class to register
            metadata: Optional metadata about the tool
            spec: Optional ToolSpec for persistence
            overwrite: Whether to overwrite existing tool with same name

        Returns:
            True if registered successfully, False otherwise
        """
        tool_name = tool_class.name

        # Check if already exists
        if tool_name in self._tools and not overwrite:
            if self.verbose:
                print(f"[Registry] Tool '{tool_name}' already exists. Use overwrite=True to replace.")
            return False

        # Create metadata if not provided
        if metadata is None:
            metadata = ToolMetadata(
                name=tool_name,
                description=getattr(tool_class, 'description', ''),
                version="1.0.0",
                author="unknown",
                created_at=datetime.now().isoformat(),
                source="runtime"
            )

        # Register
        self._tools[tool_name] = tool_class
        self._metadata[tool_name] = metadata

        if spec:
            self._specs[tool_name] = spec

        if self.verbose:
            print(f"[Registry] Registered tool '{tool_name}'")

        # Auto-save if enabled
        if self.auto_save and spec:
            self._save_tool(tool_name)

        return True

    def unregister_tool(self, tool_name: str, delete_files: bool = False) -> bool:
        """
        Unregister a tool from the registry

        Args:
            tool_name: Name of the tool to unregister
            delete_files: Whether to delete tool files from disk

        Returns:
            True if unregistered successfully
        """
        if tool_name not in self._tools:
            return False

        # Remove from memory
        del self._tools[tool_name]
        del self._metadata[tool_name]

        if tool_name in self._specs:
            del self._specs[tool_name]

        # Delete files if requested
        if delete_files:
            tool_file = self.storage_dir / f"{tool_name}.py"
            spec_file = self.storage_dir / f"{tool_name}.json"

            if tool_file.exists():
                tool_file.unlink()
            if spec_file.exists():
                spec_file.unlink()

        if self.verbose:
            print(f"[Registry] Unregistered tool '{tool_name}'")

        # Save registry
        self._save_registry()

        return True

    def get_tool(self, tool_name: str) -> Optional[Type]:
        """Get a tool class by name"""
        return self._tools.get(tool_name)

    def get_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a tool"""
        return self._metadata.get(tool_name)

    def get_spec(self, tool_name: str) -> Optional[ToolSpec]:
        """Get ToolSpec for a tool"""
        return self._specs.get(tool_name)

    def list_tools(
        self,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[str]:
        """
        List all registered tools

        Args:
            source: Filter by source (runtime, file, package)
            tags: Filter by tags

        Returns:
            List of tool names
        """
        tools = list(self._tools.keys())

        # Filter by source
        if source:
            tools = [
                name for name in tools
                if self._metadata[name].source == source
            ]

        # Filter by tags
        if tags:
            tools = [
                name for name in tools
                if any(tag in self._metadata[name].tags for tag in tags)
            ]

        return sorted(tools)

    def search_tools(self, query: str) -> List[str]:
        """
        Search tools by name or description

        Args:
            query: Search query

        Returns:
            List of matching tool names
        """
        query_lower = query.lower()
        matches = []

        for name, metadata in self._metadata.items():
            if (query_lower in name.lower() or
                query_lower in metadata.description.lower()):
                matches.append(name)

        return sorted(matches)

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a tool"""
        if tool_name not in self._tools:
            return None

        tool_class = self._tools[tool_name]
        metadata = self._metadata[tool_name]

        info = {
            "name": tool_name,
            "description": tool_class.description,
            "inputs": getattr(tool_class, 'inputs', {}),
            "output_type": getattr(tool_class, 'output_type', 'string'),
            "metadata": metadata.to_dict()
        }

        if tool_name in self._specs:
            info["spec"] = self._specs[tool_name].to_dict()

        return info

    def record_usage(self, tool_name: str):
        """Record that a tool was used"""
        if tool_name in self._metadata:
            metadata = self._metadata[tool_name]
            metadata.use_count += 1
            metadata.last_used = datetime.now().isoformat()

            if self.auto_save:
                self._save_registry()

    def get_all_tools(self) -> Dict[str, Type]:
        """Get all registered tools"""
        return self._tools.copy()

    def export_tool(self, tool_name: str, export_path: Path) -> bool:
        """Export a tool to a file"""
        if tool_name not in self._specs:
            if self.verbose:
                print(f"[Registry] Cannot export '{tool_name}': no spec available")
            return False

        spec = self._specs[tool_name]
        export_path = Path(export_path)

        try:
            # Save spec as JSON
            spec_file = export_path / f"{tool_name}.json"
            with open(spec_file, 'w') as f:
                json.dump(spec.to_dict(), f, indent=2)

            # Save code as Python file
            code_file = export_path / f"{tool_name}.py"
            with open(code_file, 'w') as f:
                f.write(spec.code)

            if self.verbose:
                print(f"[Registry] Exported tool '{tool_name}' to {export_path}")

            return True

        except Exception as e:
            if self.verbose:
                print(f"[Registry] Error exporting tool: {e}")
            return False

    def import_tool(self, tool_path: Path, factory: Optional[ToolFactory] = None) -> Optional[str]:
        """
        Import a tool from a file

        Args:
            tool_path: Path to tool JSON spec file
            factory: ToolFactory instance for creating the tool

        Returns:
            Tool name if successful, None otherwise
        """
        if factory is None:
            factory = ToolFactory(strict_mode=False, verbose=self.verbose)

        try:
            # Load spec
            with open(tool_path, 'r') as f:
                spec_data = json.load(f)

            spec = ToolSpec.from_dict(spec_data)

            # Create tool
            tool_class, error = factory.create_tool_from_spec(spec)
            if error:
                if self.verbose:
                    print(f"[Registry] Error creating tool from spec: {error}")
                return None

            # Register
            metadata = ToolMetadata(
                name=spec.name,
                description=spec.description,
                version=spec.version,
                author=spec.author,
                created_at=datetime.now().isoformat(),
                source="file",
                file_path=str(tool_path)
            )

            self.register_tool(tool_class, metadata, spec)

            if self.verbose:
                print(f"[Registry] Imported tool '{spec.name}'")

            return spec.name

        except Exception as e:
            if self.verbose:
                print(f"[Registry] Error importing tool: {e}")
            return None

    def _save_tool(self, tool_name: str):
        """Save a single tool to disk"""
        if tool_name not in self._specs:
            return

        spec = self._specs[tool_name]

        # Save spec
        spec_file = self.storage_dir / f"{tool_name}.json"
        with open(spec_file, 'w') as f:
            json.dump(spec.to_dict(), f, indent=2)

        # Save code
        code_file = self.storage_dir / f"{tool_name}.py"
        with open(code_file, 'w') as f:
            f.write(spec.code)

    def _save_registry(self):
        """Save registry metadata to disk"""
        registry_data = {
            "tools": {
                name: metadata.to_dict()
                for name, metadata in self._metadata.items()
            }
        }

        with open(self.registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)

    def _load_registry(self):
        """Load registry metadata from disk"""
        if not self.registry_file.exists():
            return

        try:
            with open(self.registry_file, 'r') as f:
                registry_data = json.load(f)

            # Load metadata
            for name, metadata_dict in registry_data.get("tools", {}).items():
                self._metadata[name] = ToolMetadata.from_dict(metadata_dict)

            # Load tool specs and create tools
            factory = ToolFactory(strict_mode=False, verbose=False)

            for name in self._metadata.keys():
                spec_file = self.storage_dir / f"{name}.json"
                if spec_file.exists():
                    try:
                        with open(spec_file, 'r') as f:
                            spec_data = json.load(f)

                        spec = ToolSpec.from_dict(spec_data)
                        self._specs[name] = spec

                        # Create tool class
                        tool_class, error = factory.create_tool_from_spec(spec)
                        if tool_class:
                            self._tools[name] = tool_class

                    except Exception as e:
                        if self.verbose:
                            print(f"[Registry] Error loading tool '{name}': {e}")

            if self.verbose and self._tools:
                print(f"[Registry] Loaded {len(self._tools)} tools from disk")

        except Exception as e:
            if self.verbose:
                print(f"[Registry] Error loading registry: {e}")

    def clear_all(self, delete_files: bool = False):
        """Clear all tools from registry"""
        if delete_files:
            for tool_name in list(self._tools.keys()):
                self.unregister_tool(tool_name, delete_files=True)
        else:
            self._tools.clear()
            self._metadata.clear()
            self._specs.clear()

        self._save_registry()

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the registry"""
        return {
            "total_tools": len(self._tools),
            "runtime_tools": len([m for m in self._metadata.values() if m.source == "runtime"]),
            "file_tools": len([m for m in self._metadata.values() if m.source == "file"]),
            "package_tools": len([m for m in self._metadata.values() if m.source == "package"]),
            "total_uses": sum(m.use_count for m in self._metadata.values()),
            "most_used": max(
                [(m.name, m.use_count) for m in self._metadata.values()],
                key=lambda x: x[1],
                default=("none", 0)
            )
        }


# Global registry instance (singleton pattern)
_global_registry: Optional[ToolRegistry] = None


def get_global_registry() -> ToolRegistry:
    """Get or create the global tool registry"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry(verbose=False)
    return _global_registry


def reset_global_registry():
    """Reset the global registry (useful for testing)"""
    global _global_registry
    _global_registry = None
