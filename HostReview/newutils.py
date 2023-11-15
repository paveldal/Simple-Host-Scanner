import paramiko
from .models import Profile, ScanResult
import re

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
        return stdout.read().decode('utf-8').strip()

    def detect_os_and_version(self):
        os_info = self.execute_command('uname -a')
        os_match = re.search(r"(\S+)\s+(\S+)", os_info)
        os, version = os_match.groups() if os_match else ('Unknown', 'Unknown')
        return os, version

    def collect_processes(self):
        return self.execute_command('ps aux')

    def collect_system_load(self):
        return self.execute_command('uptime')

    def collect_disk_space(self):
        return self.execute_command('df -h')

    def collect_memory_status(self):
        return self.execute_command('free -m')

    def collect_sys_logs(self):
        # Дополнительная логика для выбора журнала в зависимости от ОС
        log_file = "/var/log/syslog"  # Пример, может меняться в зависимости от ОС
        return self.execute_command(f'cat {log_file}')

    def collect_network_info(self):
        return self.execute_command('netstat -tuln')

    def collect_installed_packages(self):
        # Дополнительная логика для определения системы управления пакетами
        return self.execute_command('dpkg -l')  # Или rpm -qa для Red Hat систем

    def collect_user_info(self):
        users = self.execute_command('cat /etc/passwd')
        groups = self.execute_command('cat /etc/group')
        sudo_permissions = self.execute_command('sudo -l')
        return users, groups, sudo_permissions

    def collect_firewall_status(self):
        # Дополнительная логика для определения типа брандмауэра
        return self.execute_command('iptables -L')

    def close_connection(self):
        if self.ssh:
            self.ssh.close()

    def perform_scan(self):
        try:
            scan_result = ScanResult(profile=self.profile, status='in_progress')
            scan_result.save()

            os, version = self.detect_os_and_version()
            scan_result.os = os
            scan_result.os_version = version

            scan_result.architecture = self.execute_command('uname -m')
            scan_result.kernel = self.execute_command('uname -r')
            scan_result.active_processes = self.collect_processes()
            scan_result.system_load = self.collect_system_load()
            scan_result.disk_space = self.collect_disk_space()
            scan_result.memory_status = self.collect_memory_status()
            scan_result.sys_logs = self.collect_sys_logs()
            scan_result.network_info = self.collect_network_info()
            scan_result.installed_packages = self.collect_installed_packages()
            users, groups, sudo_permissions = self.collect_user_info()
            scan_result.users = users
            scan_result.groups = groups
            scan_result.sudo_permissions = sudo_permissions
            scan_result.firewall_status = self.collect_firewall_status()

            scan_result.status = 'completed'
            scan_result.save()

        except Exception as e:
            scan_result.status = 'error'
            scan_result.error_message = str(e)
            scan_result.save()
        finally:
            self.close_connection()