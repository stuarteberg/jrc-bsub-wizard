import re
from typing import List, Optional, Tuple
from pathlib import Path


class JobValidator:
    """Validation utilities for job configurations"""
    
    # Reserved words that shouldn't be in job names
    RESERVED_WORDS = ['spark', 'janelia', 'master', 'int', 'admin', 'root', 'system']
    
    # Valid characters for job names (alphanumeric, underscore, hyphen)
    JOB_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    # Time format patterns
    TIME_PATTERN_HHMM = re.compile(r'^([0-9]{1,3}):([0-5][0-9])$')
    TIME_PATTERN_MM = re.compile(r'^([0-9]{1,5})$')
    
    @classmethod
    def validate_job_name(cls, job_name: str) -> Tuple[bool, Optional[str]]:
        """Validate job name according to cluster policies"""
        if not job_name:
            return False, "Job name is required"
        
        if not job_name.strip():
            return False, "Job name cannot be empty or whitespace only"
        
        if len(job_name) > 100:
            return False, "Job name must be 100 characters or less"
        
        if ' ' in job_name:
            return False, "Job name cannot contain spaces"
        
        if not cls.JOB_NAME_PATTERN.match(job_name):
            return False, "Job name can only contain letters, numbers, underscores, and hyphens"
        
        # Check for reserved words
        job_name_lower = job_name.lower()
        for word in cls.RESERVED_WORDS:
            if word in job_name_lower:
                return False, f"Job name cannot contain reserved word: {word}"
        
        return True, None
    
    @classmethod
    def validate_time_format(cls, time_str: str) -> Tuple[bool, Optional[str]]:
        """Validate time format (MM or HH:MM)"""
        if not time_str:
            return True, None  # Empty time is valid (no limit)
        
        # Try HH:MM format first
        match = cls.TIME_PATTERN_HHMM.match(time_str)
        if match:
            hours, minutes = int(match.group(1)), int(match.group(2))
            if hours > 999:
                return False, "Hours cannot exceed 999"
            return True, None
        
        # Try MM format
        match = cls.TIME_PATTERN_MM.match(time_str)
        if match:
            minutes = int(match.group(1))
            if minutes > 59999:
                return False, "Minutes cannot exceed 59999"
            return True, None
        
        return False, "Time must be in format MM or HH:MM"
    
    @classmethod
    def validate_slots(cls, slots: int, max_slots: int = 64) -> Tuple[bool, Optional[str]]:
        """Validate number of slots"""
        if slots < 1:
            return False, "Number of slots must be at least 1"
        
        if slots > max_slots:
            return False, f"Number of slots cannot exceed {max_slots}"
        
        return True, None
    
    @classmethod
    def validate_gpu_count(cls, gpu_count: int, max_gpus: int = 8) -> Tuple[bool, Optional[str]]:
        """Validate number of GPUs"""
        if gpu_count < 1:
            return False, "Number of GPUs must be at least 1"
        
        if gpu_count > max_gpus:
            return False, f"Number of GPUs cannot exceed {max_gpus}"
        
        return True, None
    
    @classmethod
    def validate_file_path(cls, file_path: str, must_be_absolute: bool = True) -> Tuple[bool, Optional[str]]:
        """Validate file path"""
        if not file_path:
            return True, None  # Empty path is valid
        
        try:
            path = Path(file_path)
            
            if must_be_absolute and not path.is_absolute():
                return False, "File path should be absolute (start with /)"
            
            # Check for invalid characters (basic check)
            if any(char in file_path for char in ['<', '>', '|', '*', '?']):
                return False, "File path contains invalid characters"
            
            return True, None
        
        except Exception as e:
            return False, f"Invalid file path: {str(e)}"
    
    @classmethod
    def validate_command(cls, command: str) -> Tuple[bool, Optional[str]]:
        """Validate command string"""
        if not command:
            return False, "Command is required"
        
        if not command.strip():
            return False, "Command cannot be empty or whitespace only"
        
        # Basic security check - reject potentially dangerous commands
        dangerous_patterns = [
            r'rm\s+-rf\s+/',  # rm -rf /
            r':\(\)\{.*\|.*&.*\};:',  # fork bomb pattern
            r'>\s*/dev/sd[a-z]',  # writing to disk devices
            r'sudo\s+rm',  # sudo rm commands
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, "Command contains potentially dangerous patterns"
        
        return True, None
    
    @classmethod
    def validate_array_config(cls, start: int, end: int, step: int = 1) -> Tuple[bool, Optional[str]]:
        """Validate array job configuration"""
        if start < 1:
            return False, "Array start index must be at least 1"
        
        if end < start:
            return False, "Array end index must be greater than or equal to start index"
        
        if step < 1:
            return False, "Array step must be at least 1"
        
        # Check for reasonable array size
        total_tasks = (end - start) // step + 1
        if total_tasks > 10000:
            return False, "Array job cannot have more than 10,000 tasks"
        
        return True, None
    
    @classmethod
    def validate_memory_requirement(cls, memory_str: str) -> Tuple[bool, Optional[str]]:
        """Validate memory requirement string (e.g., '16G', '512M')"""
        if not memory_str:
            return True, None
        
        pattern = re.compile(r'^([0-9]+)([GMK]?)$', re.IGNORECASE)
        match = pattern.match(memory_str)
        
        if not match:
            return False, "Memory must be specified as number followed by optional unit (G, M, K)"
        
        amount = int(match.group(1))
        unit = match.group(2).upper() if match.group(2) else 'M'
        
        # Convert to MB for validation
        if unit == 'G':
            memory_mb = amount * 1024
        elif unit == 'K':
            memory_mb = amount / 1024
        else:  # M
            memory_mb = amount
        
        if memory_mb < 1:
            return False, "Memory requirement must be at least 1MB"
        
        if memory_mb > 2048 * 1024:  # 2TB limit
            return False, "Memory requirement cannot exceed 2TB"
        
        return True, None
    
    @classmethod
    def suggest_queue_for_requirements(cls, job_type: str, runtime_hours: float, gpu_needed: bool = False) -> List[str]:
        """Suggest appropriate queues based on job requirements"""
        suggestions = []
        
        if job_type == "interactive":
            suggestions.append("interactive")
        elif gpu_needed:
            if runtime_hours <= 1:
                suggestions.append("gpu_short")
            else:
                suggestions.extend(["gpu_a100", "gpu_l4", "gpu_t4"])
        else:  # CPU job
            if runtime_hours <= 1:
                suggestions.append("short")
            else:
                suggestions.append("local")
        
        return suggestions
    
    @classmethod
    def validate_environment_variable(cls, var_name: str, var_value: str) -> Tuple[bool, Optional[str]]:
        """Validate environment variable name and value"""
        if not var_name:
            return False, "Environment variable name is required"
        
        # Check variable name format
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', var_name):
            return False, "Environment variable name must start with letter or underscore, contain only letters, numbers, and underscores"
        
        # Check for reserved variable names
        reserved_vars = ['PATH', 'HOME', 'USER', 'PWD', 'SHELL', 'LSB_JOBID', 'LSB_JOBINDEX']
        if var_name in reserved_vars:
            return False, f"Cannot override reserved environment variable: {var_name}"
        
        # Basic value validation
        if len(var_value) > 1000:
            return False, "Environment variable value cannot exceed 1000 characters"
        
        return True, None