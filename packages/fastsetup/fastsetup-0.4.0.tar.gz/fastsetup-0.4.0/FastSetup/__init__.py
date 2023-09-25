def _check_dependencies():
    _hard_dependencies = ("cx_Oracle", "pandas", "logging", "datetime", "email", "smtplib", "pysftp", "sqlalchemy", "requests")
    _missing_dependencies = []

    for _dependency in _hard_dependencies:
        try:
            __import__(_dependency)
        except ImportError as _e:  
            _missing_dependencies.append(f"{_dependency}: {_e}")

    if _missing_dependencies:  
        raise ImportError("Unable to import required dependencies:\n" + "\n".join(_missing_dependencies))
    
    del _hard_dependencies, _dependency, _missing_dependencies


# Let users know if they're missing any of our hard dependencies
_check_dependencies()
import tools
import orchestrator_api
