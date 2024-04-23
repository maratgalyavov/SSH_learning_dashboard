async def submit_job(ssh_client, job_script):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(f'sbatch {job_script}')
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        return output or error or "Задача отправлена на выполнение."
    except Exception as e:
        return f"Ошибка при отправке задачи: {e}"


async def show_queue(ssh_client):
    try:
        stdin, stdout, stderr = ssh_client.exec_command('squeue')
        output = stdout.read().decode('utf-8').strip()
        return output or "Очередь задач пуста."
    except Exception as e:
        return f"Ошибка при просмотре очереди задач: {e}"


async def cancel_job(ssh_client, job_id):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(f'scancel {job_id}')
        output = stdout.read().decode('utf-8').strip()
        return output or "Задача отменена."
    except Exception as e:
        return f"Ошибка при отмене задачи: {e}"
