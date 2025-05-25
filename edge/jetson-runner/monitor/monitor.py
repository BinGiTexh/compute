import os
import time
import requests
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/monitor/monitor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("runner-monitor")

DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def send_discord_notification(message):
    """Send a message to Discord webhook"""
    if not DISCORD_WEBHOOK_URL:
        logger.warning("Discord webhook URL not configured")
        return False
        
    try:
        payload = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            logger.info(f"Discord notification sent: {message}")
            return True
        else:
            logger.error(f"Failed to send Discord notification: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error sending Discord notification: {str(e)}")
        return False

def check_runner_container():
    """Check if the GitHub runner container is healthy"""
    try:
        # Use Docker API to check container status
        # For simplicity in this script, we'll use the docker command line
        import subprocess
        
        # Get container status
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}} {{.State.Health.Status}}", "github-runner"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Failed to get container status: {result.stderr}")
            return False
            
        status_parts = result.stdout.strip().split()
        if len(status_parts) < 2:
            logger.error(f"Unexpected container status format: {result.stdout}")
            return False
            
        container_status, health_status = status_parts
        
        if container_status != "running":
            send_discord_notification(f"🚨 GitHub Runner is not running! Status: {container_status}")
            return False
            
        if health_status != "healthy":
            send_discord_notification(f"⚠️ GitHub Runner is unhealthy! Health status: {health_status}")
            return False
            
        # Check GitHub connectivity
        ping_result = subprocess.run(["ping", "-c", "1", "github.com"], capture_output=True)
        if ping_result.returncode != 0:
            send_discord_notification("📡 GitHub Runner container is running but cannot reach GitHub.com")
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error checking runner health: {str(e)}")
        send_discord_notification(f"🔥 Monitor error: {str(e)}")
        return False

def main():
    """Main monitoring loop"""
    last_notification_time = {}
    notification_interval = 3600  # 1 hour in seconds
    
    logger.info("GitHub Runner monitor started")
    send_discord_notification("🟢 GitHub Runner monitoring service started")
    
    while True:
        try:
            current_time = time.time()
            is_healthy = check_runner_container()
            
            # If unhealthy and we haven't sent a notification recently, send one
            if not is_healthy:
                last_sent = last_notification_time.get('unhealthy', 0)
                if current_time - last_sent > notification_interval:
                    last_notification_time['unhealthy'] = current_time
            else:
                # If it was previously unhealthy but now is healthy, send recovery notification
                if 'unhealthy' in last_notification_time:
                    send_discord_notification("✅ GitHub Runner has recovered and is now healthy")
                    last_notification_time.pop('unhealthy', None)
                    
            # Daily status report
            now = datetime.now()
            if now.hour == 9 and now.minute == 0:  # 9 AM status report
                last_sent = last_notification_time.get('daily', 0)
                if current_time - last_sent > 23 * 3600:  # ~23 hours
                    if is_healthy:
                        send_discord_notification("📊 Daily Status: GitHub Runner is healthy and operational")
                    last_notification_time['daily'] = current_time
                
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
            
        # Check every 5 minutes
        time.sleep(300)

if __name__ == "__main__":
    main()
