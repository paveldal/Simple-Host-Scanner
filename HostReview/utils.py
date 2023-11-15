import paramiko
from .models import Profile, ScanResult

class SystemInfoCollector:
    def __init__(self, profile_id):
        self.profile = Profile.objects.get(pk=profile_id)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect()

    def connect(self):
        try:
            self.ssh.connect(hostname=self.profile.host, port=self.profile.port,
                             username=self.profile.login, password=self.profile.password)
        except paramiko.AuthenticationException:
            raise Exception("Ошибка аутентификации при подключении к серверу.")
        except paramiko.SSHException as e:
            raise Exception(f"Ошибка SSH: {e}")

    def execute_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return f"execute command: {command}\n{stdout.read().decode('utf-8').strip()}"

    def collect_os(self):
        return self.execute_command('lsb_release -a 2>/dev/null | grep -E "Distributor"')

    def collect_os_version(self):
        return self.execute_command('lsb_release -a 2>/dev/null | grep -E "Release"')
    
    def collect_architecture(self):
        return self.execute_command('uname -m')
    
    def collect_kernel(self):
        return self.execute_command('uname -r')

    def collect_processes(self):
        return self.execute_command('ps aux')

    def collect_system_load(self):
        return self.execute_command('uptime')

    def collect_disk_space(self):
        return self.execute_command('df -h')

    def collect_memory_status(self):
        return self.execute_command('free -m')

    def collect_sys_logs(self):
        try:
            log_files_command = "find /var/log -type f -name '*.log'"
            log_files = self.execute_command(log_files_command).splitlines()

            collected_logs = ""

            for log_file in log_files:
                try:
                    log_content = self.execute_command(f'cat {log_file} 2>/dev/null')
                    if log_content:
                        collected_logs += f"\n--- {log_file} ---\n{log_content}\n"
                except Exception as e:
                    collected_logs += f"\n--- Error accessing {log_file}: {e} ---\n"

            return collected_logs if collected_logs else "No logs found or accessible."

        except Exception as e:
            return f"Error collecting log files: {e}"

    def collect_network_info(self):
        return self.execute_command('ss -tulpn')

    def detect_package_manager(self):
        try:
            if self.execute_command('which dpkg'):
                return 'dpkg -l'
            elif self.execute_command('which rpm'):
                return 'rpm -qa'
            elif self.execute_command('which pacman'):
                return 'pacman -Q'
        except Exception:
            return None
        
    def collect_installed_packages(self):
        package_manager_cmd = self.detect_package_manager()
        if package_manager_cmd:
            return self.execute_command(package_manager_cmd)
        else:
            return 'Unknown'
    
    def collect_users_info(self):
        return self.execute_command('cat /etc/passwd')
    
    def collect_groups_info(self):
        return self.execute_command('cat /etc/group')
    
    def collect_sudo_info(self):
        return self.execute_command('sudo -l')

    def collect_firewall_status(self):
        return self.execute_command('iptables -L')

    def close_connection(self):
        if self.ssh:
            self.ssh.close()

    def perform_scan(self):
        scan_result = ScanResult(profile=self.profile, status='in_progress')
        scan_result.save()
        try:
            scan_result.os = self.collect_os()
            scan_result.os_version = self.collect_os_version()
            scan_result.architecture = self.collect_architecture()
            scan_result.kernel = self.collect_kernel()
            scan_result.active_processes = self.collect_processes()
            scan_result.system_load = self.collect_system_load()
            scan_result.disk_space = self.collect_disk_space()
            scan_result.memory_status = self.collect_memory_status()
            scan_result.sys_logs = self.collect_sys_logs()
            scan_result.network_info = self.collect_network_info()
            scan_result.installed_packages = self.collect_installed_packages()
            scan_result.users = self.collect_users_info()
            scan_result.groups = self.collect_groups_info()
            scan_result.sudo_permissions = self.collect_sudo_info()
            scan_result.firewall_status = self.collect_firewall_status()
            scan_result.status = 'completed'
            scan_result.save()

        except Exception as e:
            scan_result.status = 'error'
            scan_result.error_message = str(e)
            scan_result.save()
        finally:
            self.close_connection()
