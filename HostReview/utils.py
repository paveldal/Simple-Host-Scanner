import paramiko
from .models import Profile, ScanResult
import re

def detect_os(release_info):
    distributor_match = re.search(r"Distributor ID:\s*(\S+)", release_info)
    return distributor_match.group(1) if distributor_match else None

def detect_os_version(release_info):
    release_match = re.search(r"Release:\s*(\S+)", release_info)
    return release_match.group(1) if release_match else None

def detect_architecture(uname_info):
    return uname_info.split()[11] if len(uname_info.split()) > 11 else 'Unknown'

def collect_services_info(ssh):
    stdin, stdout, stderr = ssh.exec_command('systemctl list-units --type=service --state=running')
    services_output = stdout.read().decode('utf-8')
    return services_output

def collect_information(ssh, command_line):
    stdin, stdout, stderr = ssh.exec_command(command_line)
    return stdout.read().decode('utf-8')

def collect_system_info(profile_id):
    profile = Profile.objects.get(pk=profile_id)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    collected_logs = ""
    collected_os_info = ""
    uname_info = ""

    try:
        ssh.connect(hostname=profile.host, port=profile.port, username=profile.login, password=profile.password)
        scan_result = ScanResult(profile=profile, status='in_progress')
        scan_result.save()
        
        os_command_line = 'lsb_release -a 2>/dev/null | grep -E "Distributor|Release"'
        collected_os_info = collect_information(ssh, os_command_line)
        collected_logs += f"{os_command_line} output:\n{collected_os_info}\n\n"

        arch_command_line = 'uname -m'
        architecture = collect_information(ssh, arch_command_line)
        collected_logs += f"{arch_command_line} output:\n{architecture}\n\n"

        kernel_command_line = 'uname -r'
        kernel = collect_information(ssh, kernel_command_line)
        collected_logs += f"{kernel_command_line} output:\n{kernel}\n\n"

        collected_logs = '\n'.join([line for line in collected_logs.splitlines() if line.strip()])
        
        os_detected = detect_os(collected_os_info)
        os_version = detect_os_version(collected_os_info)
        
        scan_result.log = collected_logs
        scan_result.os = os_detected
        scan_result.os_version = os_version
        scan_result.architecture = architecture
        scan_result.kernel = kernel
        scan_result.status = 'completed'
        scan_result.save()

    except paramiko.AuthenticationException:
        collected_logs += "Ошибка аутентификации при подключении к серверу.\n"
        scan_result.status = 'error'
        scan_result.save()
    except paramiko.SSHException as sshException:
        collected_logs += f"Ошибка SSH: {sshException}\n"
        scan_result.status = 'error'
        scan_result.save()
    except Exception as e:
        collected_logs += f"Произошла непредвиденная ошибка: {e}\n"
        scan_result.status = 'error'
        scan_result.save()
    finally:
        if ssh:
            ssh.close()
