import os

def get_environment_str(name) -> str:
    env_str = os.getenv(name)

    if not env_str:
        raise EnvironmentError(f'Environment variable "{name}" not found.')
    
    return env_str


def get_environment_int(name) -> int:
    env_str = os.getenv(name)

    if not env_str:
        raise EnvironmentError(f'Environment variable "{name}" not found.')

    if not env_str.isdigit():
        raise ValueError(f'Environment variable "{name}" must be an integer string.')
    
    return int(env_str)