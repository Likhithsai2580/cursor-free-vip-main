import os
import sys
import configparser
from colorama import Fore, Style
from utils import get_user_documents_path, get_linux_cursor_path, get_default_driver_path, get_default_browser_path
import shutil
import datetime

EMOJI = {
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "SUCCESS": "✅",
    "ADMIN": "🔒",
    "ARROW": "➡️",
    "USER": "👤",
    "KEY": "🔑",
    "SETTINGS": "⚙️"
}

# global config cache
_config_cache = None

def setup_config(translator=None):
    """Setup configuration file and return config object and its path"""
    try:
        # get documents path
        docs_path = get_user_documents_path()
        if not docs_path or not os.path.exists(docs_path):
            # if documents path not found, use current directory
            print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.documents_path_not_found', fallback='Documents path not found, using current directory') if translator else 'Documents path not found, using current directory'}{Style.RESET_ALL}")
            docs_path = os.path.abspath('.')
        
        # normalize path
        config_dir = os.path.normpath(os.path.join(docs_path, ".cursor-free-vip"))
        config_file = os.path.normpath(os.path.join(config_dir, "config.ini"))
        
        # create config directory, only print message when directory not exists
        dir_exists = os.path.exists(config_dir)
        try:
            os.makedirs(config_dir, exist_ok=True)
            if not dir_exists:  # only print message when directory not exists
                print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_dir_created', path=config_dir) if translator else f'Config directory created: {config_dir}'}{Style.RESET_ALL}")
        except Exception as e:
            # if cannot create directory, use temporary directory
            import tempfile
            temp_dir = os.path.normpath(os.path.join(tempfile.gettempdir(), ".cursor-free-vip"))
            temp_exists = os.path.exists(temp_dir)
            config_dir = temp_dir
            config_file = os.path.normpath(os.path.join(config_dir, "config.ini"))
            os.makedirs(config_dir, exist_ok=True)
            if not temp_exists:  # only print message when temporary directory not exists
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.using_temp_dir', path=config_dir, error=str(e)) if translator else f'Using temporary directory due to error: {config_dir} (Error: {str(e)})'}{Style.RESET_ALL}")
        
        # create config object
        config = configparser.ConfigParser()
        
        # Default configuration
        default_config = {
            'Browser': {
                'default_browser': 'chrome',
                'chrome_path': get_default_browser_path('chrome'),
                'chrome_driver_path': get_default_driver_path('chrome'),
                'edge_path': get_default_browser_path('edge'),
                'edge_driver_path': get_default_driver_path('edge'),
                'firefox_path': get_default_browser_path('firefox'),
                'firefox_driver_path': get_default_driver_path('firefox'),
                'brave_path': get_default_browser_path('brave'),
                'brave_driver_path': get_default_driver_path('brave'),
                'opera_path': get_default_browser_path('opera'),
                'opera_driver_path': get_default_driver_path('opera'),
                'operagx_path': get_default_browser_path('operagx'),
                'operagx_driver_path': get_default_driver_path('chrome')  # Opera GX 使用 Chrome 驱动
            },
            'Turnstile': {
                'handle_turnstile_time': '2',
                'handle_turnstile_random_time': '1-3'
            },
            'Timing': {
                'min_random_time': '0.1',
                'max_random_time': '0.8',
                'page_load_wait': '0.1-0.8',
                'input_wait': '0.3-0.8',
                'submit_wait': '0.5-1.5',
                'verification_code_input': '0.1-0.3',
                'verification_success_wait': '2-3',
                'verification_retry_wait': '2-3',
                'email_check_initial_wait': '4-6',
                'email_refresh_wait': '2-4',
                'settings_page_load_wait': '1-2',
                'failed_retry_time': '0.5-1',
                'retry_interval': '8-12',
                'max_timeout': '160'
            },
            'Utils': {
                'enabled_update_check': 'True',
                'enabled_force_update': 'False',
                'enabled_account_info': 'True'
            },
            'OAuth': {
                'show_selection_alert': False,  # 默认不显示选择提示弹窗
                'timeout': 120,
                'max_attempts': 3
            },
            'Token': {
                'refresh_server': 'https://token.cursorpro.com.cn',
                'enable_refresh': True
            },
            'Language': {
                'current_language': '',  # Set by local system detection if empty
                'fallback_language': 'en',
                'auto_update_languages': 'True',
                'language_cache_dir': os.path.join(config_dir, "language_cache")
            }
        }

        # Add system-specific path configuration
        if sys.platform == "win32":
            appdata = os.getenv("APPDATA")
            localappdata = os.getenv("LOCALAPPDATA", "")
            default_config['WindowsPaths'] = {
                'storage_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "storage.json"),
                'sqlite_path': os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb"),
                'machine_id_path': os.path.join(appdata, "Cursor", "machineId"),
                'cursor_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app"),
                'updater_path': os.path.join(localappdata, "cursor-updater"),
                'update_yml_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app-update.yml"),
                'product_json_path': os.path.join(localappdata, "Programs", "Cursor", "resources", "app", "product.json")
            }
            # Create storage directory
            os.makedirs(os.path.dirname(default_config['WindowsPaths']['storage_path']), exist_ok=True)
            
        elif sys.platform == "darwin":
            default_config['MacPaths'] = {
                'storage_path': os.path.abspath(os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/storage.json")),
                'sqlite_path': os.path.abspath(os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")),
                'machine_id_path': os.path.expanduser("~/Library/Application Support/Cursor/machineId"),
                'cursor_path': "/Applications/Cursor.app/Contents/Resources/app",
                'updater_path': os.path.expanduser("~/Library/Application Support/cursor-updater"),
                'update_yml_path': "/Applications/Cursor.app/Contents/Resources/app-update.yml",
                'product_json_path': "/Applications/Cursor.app/Contents/Resources/app/product.json"
            }
            # Create storage directory
            os.makedirs(os.path.dirname(default_config['MacPaths']['storage_path']), exist_ok=True)
            
        elif sys.platform == "linux":
            # Get the actual user's home directory, handling both sudo and normal cases
            sudo_user = os.environ.get('SUDO_USER')
            current_user = sudo_user if sudo_user else (os.getenv('USER') or os.getenv('USERNAME'))
            
            if not current_user:
                current_user = os.path.expanduser('~').split('/')[-1]
            
            # Handle sudo case
            if sudo_user:
                actual_home = f"/home/{sudo_user}"
                root_home = "/root"
            else:
                actual_home = f"/home/{current_user}"
                root_home = None
            
            if not os.path.exists(actual_home):
                actual_home = os.path.expanduser("~")
            
            # Define base config directory
            config_base = os.path.join(actual_home, ".config")
            
            # Try both "Cursor" and "cursor" directory names in both user and root locations
            cursor_dir = None
            possible_paths = [
                os.path.join(config_base, "Cursor"),
                os.path.join(config_base, "cursor"),
                os.path.join(root_home, ".config", "Cursor") if root_home else None,
                os.path.join(root_home, ".config", "cursor") if root_home else None
            ]
            
            for path in possible_paths:
                if path and os.path.exists(path):
                    cursor_dir = path
                    break
            
            if not cursor_dir:
                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.neither_cursor_nor_cursor_directory_found', config_base=config_base) if translator else f'Neither Cursor nor cursor directory found in {config_base}'}{Style.RESET_ALL}")
                if root_home:
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.also_checked', path=f'{root_home}/.config') if translator else f'Also checked {root_home}/.config'}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.please_make_sure_cursor_is_installed_and_has_been_run_at_least_once') if translator else 'Please make sure Cursor is installed and has been run at least once'}{Style.RESET_ALL}")
            
            # Define Linux paths using the found cursor directory
            storage_path = os.path.abspath(os.path.join(cursor_dir, "User/globalStorage/storage.json")) if cursor_dir else ""
            storage_dir = os.path.dirname(storage_path) if storage_path else ""
            
            # Verify paths and permissions
            try:
                # Check storage directory
                if storage_dir and not os.path.exists(storage_dir):
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.storage_directory_not_found', storage_dir=storage_dir) if translator else f'Storage directory not found: {storage_dir}'}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.please_make_sure_cursor_is_installed_and_has_been_run_at_least_once') if translator else 'Please make sure Cursor is installed and has been run at least once'}{Style.RESET_ALL}")
                
                # Check storage.json with more detailed verification
                if storage_path and os.path.exists(storage_path):
                    # Get file stats
                    try:
                        stat = os.stat(storage_path)
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.storage_file_found', storage_path=storage_path) if translator else f'Storage file found: {storage_path}'}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.file_size', size=stat.st_size) if translator else f'File size: {stat.st_size} bytes'}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.file_permissions', permissions=oct(stat.st_mode & 0o777)) if translator else f'File permissions: {oct(stat.st_mode & 0o777)}'}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.file_owner', owner=stat.st_uid) if translator else f'File owner: {stat.st_uid}'}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}{EMOJI['INFO']} {translator.get('config.file_group', group=stat.st_gid) if translator else f'File group: {stat.st_gid}'}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_getting_file_stats', error=str(e)) if translator else f'Error getting file stats: {str(e)}'}{Style.RESET_ALL}")
                    
                    # Check if file is readable and writable
                    if not os.access(storage_path, os.R_OK | os.W_OK):
                        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.permission_denied', storage_path=storage_path) if translator else f'Permission denied: {storage_path}'}{Style.RESET_ALL}")
                        if sudo_user:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.try_running', command=f'chown {sudo_user}:{sudo_user} {storage_path}') if translator else f'Try running: chown {sudo_user}:{sudo_user} {storage_path}'}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.and') if translator else 'And'}: chmod 644 {storage_path}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.try_running', command=f'chown {current_user}:{current_user} {storage_path}') if translator else f'Try running: chown {current_user}:{current_user} {storage_path}'}{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.and') if translator else 'And'}: chmod 644 {storage_path}{Style.RESET_ALL}")
                    
                    # Try to read the file to verify it's not corrupted
                    try:
                        with open(storage_path, 'r') as f:
                            content = f.read()
                            if not content.strip():
                                print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.storage_file_is_empty', storage_path=storage_path) if translator else f'Storage file is empty: {storage_path}'}{Style.RESET_ALL}")
                                print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.the_file_might_be_corrupted_please_reinstall_cursor') if translator else 'The file might be corrupted, please reinstall Cursor'}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.GREEN}{EMOJI['SUCCESS']} {translator.get('config.storage_file_is_valid_and_contains_data') if translator else 'Storage file is valid and contains data'}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_reading_storage_file', error=str(e)) if translator else f'Error reading storage file: {str(e)}'}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.the_file_might_be_corrupted_please_reinstall_cursor') if translator else 'The file might be corrupted. Please reinstall Cursor'}{Style.RESET_ALL}")
                elif storage_path:
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.storage_file_not_found', storage_path=storage_path) if translator else f'Storage file not found: {storage_path}'}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}{EMOJI['INFO']} {translator.get('config.please_make_sure_cursor_is_installed_and_has_been_run_at_least_once') if translator else 'Please make sure Cursor is installed and has been run at least once'}{Style.RESET_ALL}")
                
            except (OSError, IOError) as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_checking_linux_paths', error=str(e)) if translator else f'Error checking Linux paths: {str(e)}'}{Style.RESET_ALL}")
            
            # Define all paths using the found cursor directory
            default_config['LinuxPaths'] = {
                'storage_path': storage_path,
                'sqlite_path': os.path.abspath(os.path.join(cursor_dir, "User/globalStorage/state.vscdb")) if cursor_dir else "",
                'machine_id_path': os.path.join(cursor_dir, "machineid") if cursor_dir else "",
                'cursor_path': get_linux_cursor_path(),
                'updater_path': os.path.join(config_base, "cursor-updater"),
                'update_yml_path': os.path.join(cursor_dir, "resources/app-update.yml") if cursor_dir else "",
                'product_json_path': os.path.join(cursor_dir, "resources/app/product.json") if cursor_dir else ""
            }

        # Add tempmail_plus configuration
        default_config['TempMailPlus'] = {
            'enabled': 'false',
            'email': '',
            'epin': ''
        }

        # Check and create config.ini if it doesn't exist or is empty
        if not os.path.exists(config_file) or os.path.getsize(config_file) == 0:
            try:
                config.read_dict(default_config)  # Load defaults into the config object
                with open(config_file, 'w', encoding='utf-8') as f:
                    config.write(f)
                if not os.path.exists(config_file) or os.path.getsize(config_file) == 0: # check after write
                    print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.created_config_file', path=config_file) if translator else f'Created config file: {config_file}'}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_creating_config_file', path=config_file, error=str(e)) if translator else f'Error creating config file {config_file}: {str(e)}'}{Style.RESET_ALL}")
                # Fallback: return default config object and path even if file creation failed
                config.read_dict(default_config) # ensure config object has defaults
                return config, config_file

        else:
            try:
                config.read(config_file, encoding='utf-8')
                # Merge defaults for any missing sections or keys
                updated = False
                for section, keys in default_config.items():
                    if not config.has_section(section):
                        config.add_section(section)
                        updated = True
                    for key, value in keys.items():
                        if not config.has_option(section, key):
                            config.set(section, key, str(value))
                            updated = True
                if updated:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        config.write(f)
            except Exception as e:
                print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_reading_config_file', path=config_file, error=str(e)) if translator else f'Error reading config file {config_file}: {str(e)}'}{Style.RESET_ALL}")
                # If reading fails, try to create a backup and use defaults
                try:
                    backup_file = f"{config_file}.backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.copy(config_file, backup_file)
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.backup_created', path=backup_file) if translator else f'Created backup of corrupted config: {backup_file}'}{Style.RESET_ALL}")
                except Exception as backup_error:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_creating_backup', error=str(backup_error)) if translator else f'Error creating backup: {str(backup_error)}'}{Style.RESET_ALL}")
                
                # Reset to default config
                config = configparser.ConfigParser() # Create a new config object
                config.read_dict(default_config)
                try:
                    with open(config_file, 'w', encoding='utf-8') as f: # Overwrite with defaults
                        config.write(f)
                    print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.config_reset_to_default', path=config_file) if translator else f'Config file reset to default: {config_file}'}{Style.RESET_ALL}")
                except Exception as write_error:
                    print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.error_writing_default_config', path=config_file, error=str(write_error)) if translator else f'Error writing default config {config_file}: {str(write_error)}'}{Style.RESET_ALL}")
                    # Fallback: return default config object and path even if file write failed
                    return config, config_file
        
        return config, config_file # Return both config object and its path

    except Exception as e:
        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.unexpected_error_setup', error=str(e)) if translator else f'Unexpected error during config setup: {str(e)}'}{Style.RESET_ALL}")
        # Fallback in case of major failure: return a default ConfigParser instance and a None path
        config = configparser.ConfigParser()
        # Populate with minimal defaults if possible, or handle this state upstream
        config.read_dict(default_config_minimal_for_fallback) # Assuming a minimal default
        return config, None

def print_config(config, translator=None):
    """Print configuration in a readable format"""
    if not config:
        print(f"{Fore.YELLOW}{EMOJI['WARNING']} {translator.get('config.config_not_available') if translator else 'Configuration not available'}{Style.RESET_ALL}")
        return
        
    print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.configuration') if translator else 'Configuration'}:{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    for section in config.sections():
        print(f"{Fore.GREEN}[{section}]{Style.RESET_ALL}")
        for key, value in config.items(section):
            # 对布尔值进行特殊处理，使其显示为彩色
            if value.lower() in ('true', 'yes', 'on', '1'):
                value_display = f"{Fore.GREEN}{translator.get('config.enabled') if translator else 'Enabled'}{Style.RESET_ALL}"
            elif value.lower() in ('false', 'no', 'off', '0'):
                value_display = f"{Fore.RED}{translator.get('config.disabled') if translator else 'Disabled'}{Style.RESET_ALL}"
            else:
                value_display = value
                
            print(f"  {key} = {value_display}")
    
    print(f"\n{Fore.CYAN}{'─' * 70}{Style.RESET_ALL}")
    config_dir = os.path.join(get_user_documents_path(), ".cursor-free-vip", "config.ini")
    print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_directory') if translator else 'Config Directory'}: {config_dir}{Style.RESET_ALL}")

    print()  

def force_update_config(translator=None):
    """
    Force update configuration file with latest defaults if update check is enabled.
    Args:
        translator: Translator instance
    Returns:
        Tuple (config_object, config_file_path) or (None, None) if failed
    """
    try:
        config_dir = os.path.join(get_user_documents_path(), ".cursor-free-vip")
        config_file = os.path.join(config_dir, "config.ini")
        current_time = datetime.datetime.now()

        # If the config file exists, check if forced update is enabled
        if os.path.exists(config_file):
            # First, read the existing configuration
            existing_config = configparser.ConfigParser()
            existing_config.read(config_file, encoding='utf-8')
            # Check if "enabled_update_check" is True
            update_enabled = True  # Default to True if not set
            if existing_config.has_section('Utils') and existing_config.has_option('Utils', 'enabled_force_update'):
                update_enabled = existing_config.get('Utils', 'enabled_force_update').strip().lower() in ('true', 'yes', '1', 'on')

            if update_enabled:
                try:
                    # Create a backup
                    backup_file = f"{config_file}.bak.{current_time.strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(config_file, backup_file)
                    if translator:
                        print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.backup_created', path=backup_file) if translator else f'Backup created: {backup_file}'}{Style.RESET_ALL}")
                    print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_force_update_enabled') if translator else 'Config file force update enabled'}{Style.RESET_ALL}")
                    # Delete the original config file (forced update)
                    os.remove(config_file)
                    if translator:
                        print(f"{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_removed') if translator else 'Config file removed for forced update'}{Style.RESET_ALL}")
                except Exception as e:
                    if translator:
                        print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.backup_failed', error=str(e)) if translator else f'Failed to backup config: {str(e)}'}{Style.RESET_ALL}")
            else:
                if translator:
                    print(f"\n{Fore.CYAN}{EMOJI['INFO']} {translator.get('config.config_force_update_disabled', fallback='Config file force update disabled by configuration. Keeping existing config file.') if translator else 'Config file force update disabled by configuration. Keeping existing config file.'}{Style.RESET_ALL}")

        # Generate a new (or updated) configuration if needed
        return setup_config(translator)

    except Exception as e:
        if translator:
            print(f"{Fore.RED}{EMOJI['ERROR']} {translator.get('config.force_update_failed', error=str(e)) if translator else f'Force update config failed: {str(e)}'}{Style.RESET_ALL}")
        return None, None

def get_config(translator=None):
    global _config_cache
    if _config_cache is None:
        _config_cache = setup_config(translator)  # setup_config now returns a tuple
    return _config_cache # Returns the tuple (config_object, config_file_path)

# Example of a minimal default config for fallback if everything else fails
default_config_minimal_for_fallback = {
    'Language': {
        'current_language': 'en',
        'fallback_language': 'en',
    }
}