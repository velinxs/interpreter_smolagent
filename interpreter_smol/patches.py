"""
Patches for interpreter-smol to fix issues without modifying the smolagents library.
"""

from functools import wraps

def apply_patches():
    """Apply all patches to fix issues without modifying the smolagents library."""
    # Import the necessary modules
    from smolagents.monitoring import Monitor
    from interpreter_smol.gemini_model import GeminiModel
    
    # Fix 1: Patch the Monitor.update_metrics method to handle None values
    original_update_metrics = Monitor.update_metrics
    
    @wraps(original_update_metrics)
    def safe_update_metrics(self, step_log):
        """Patched version of update_metrics that handles None values."""
        step_duration = step_log.duration
        self.step_durations.append(step_duration)
        console_outputs = f"[Step {len(self.step_durations) - 1}: Duration {step_duration:.2f} seconds"

        if hasattr(self, 'total_input_token_count') and hasattr(self.tracked_model, 'last_input_token_count'):
            # Safely handle None values
            input_tokens = self.tracked_model.last_input_token_count or 0
            output_tokens = self.tracked_model.last_output_token_count or 0
            
            self.total_input_token_count += input_tokens
            self.total_output_token_count += output_tokens
            
            console_outputs += (
                f"| Input tokens: {self.total_input_token_count:,} | Output tokens: {self.total_output_token_count:,}"
            )
        console_outputs += "]"
        self.logger.log(console_outputs, level=1)
    
    # Apply the patch
    Monitor.update_metrics = safe_update_metrics
    
    # Fix 2: Patch the GeminiModel._handle_streaming method to initialize token counts
    original_handle_streaming = GeminiModel._handle_streaming
    
    @wraps(original_handle_streaming)
    def safe_handle_streaming(self, *args, **kwargs):
        """Patched version of _handle_streaming that initializes token counts."""
        # Initialize token counts for streaming
        self.last_input_token_count = 0
        self.last_output_token_count = 0
        return original_handle_streaming(self, *args, **kwargs)
    
    # Apply the patch
    GeminiModel._handle_streaming = safe_handle_streaming