#!/usr/bin/env python3
"""
System Health Monitor for Farmer Assistant
Monitors performance, logs usage, and tracks system health
"""

import os
import sys
import json
import time
import psutil
from datetime import datetime, timedelta
import logging


class SystemMonitor:
    """Production system health monitor"""
    
    def __init__(self):
        """Initialize system monitor"""
        self.start_time = datetime.now()
        self.log_file = "farmer_assistant.log"
        self.metrics_file = "system_metrics.json"
        
        # Setup logging
        self.setup_logging()
        
        # System metrics
        self.metrics = {
            "session_start": self.start_time.isoformat(),
            "total_queries": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "average_response_time": 0,
            "component_health": {
                "stt": "unknown",
                "nlp": "unknown", 
                "llm": "unknown",
                "tts": "unknown"
            },
            "system_resources": {
                "cpu_usage": [],
                "memory_usage": [],
                "disk_usage": []
            },
            "error_log": []
        }
        
        self.logger.info("System monitor initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_query(self, query: str, intent: str, confidence: float, response_time: float, success: bool):
        """Log a farmer query"""
        self.metrics["total_queries"] += 1
        
        if success:
            self.metrics["successful_responses"] += 1
        else:
            self.metrics["failed_responses"] += 1
        
        # Update average response time
        total_responses = self.metrics["successful_responses"] + self.metrics["failed_responses"]
        if total_responses > 0:
            current_avg = self.metrics["average_response_time"]
            self.metrics["average_response_time"] = (
                (current_avg * (total_responses - 1) + response_time) / total_responses
            )
        
        # Log details
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:100],  # Truncate for privacy
            "intent": intent,
            "confidence": confidence,
            "response_time": response_time,
            "success": success
        }
        
        self.logger.info(f"Query processed: {intent} ({confidence:.2f}) - {response_time:.2f}s - {'✅' if success else '❌'}")
        
        # Save metrics
        self.save_metrics()
    
    def log_error(self, component: str, error: str):
        """Log system error"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error": str(error)
        }
        
        self.metrics["error_log"].append(error_entry)
        self.metrics["component_health"][component] = "error"
        
        self.logger.error(f"{component} error: {error}")
        self.save_metrics()
    
    def update_component_health(self, component: str, status: str):
        """Update component health status"""
        self.metrics["component_health"][component] = status
        self.logger.info(f"{component} status: {status}")
        self.save_metrics()
    
    def monitor_system_resources(self):
        """Monitor system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics["system_resources"]["cpu_usage"].append({
                "timestamp": datetime.now().isoformat(),
                "value": cpu_percent
            })
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics["system_resources"]["memory_usage"].append({
                "timestamp": datetime.now().isoformat(),
                "value": memory.percent,
                "available_gb": memory.available / (1024**3)
            })
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics["system_resources"]["disk_usage"].append({
                "timestamp": datetime.now().isoformat(),
                "value": (disk.used / disk.total) * 100,
                "free_gb": disk.free / (1024**3)
            })
            
            # Keep only last 100 entries
            for resource in self.metrics["system_resources"]:
                if len(self.metrics["system_resources"][resource]) > 100:
                    self.metrics["system_resources"][resource] = self.metrics["system_resources"][resource][-100:]
            
            self.save_metrics()
            
        except Exception as e:
            self.log_error("system_monitor", f"Resource monitoring failed: {e}")
    
    def get_system_health_report(self):
        """Generate system health report"""
        uptime = datetime.now() - self.start_time
        
        # Calculate success rate
        total_queries = self.metrics["total_queries"]
        success_rate = 0
        if total_queries > 0:
            success_rate = (self.metrics["successful_responses"] / total_queries) * 100
        
        # Get latest resource usage
        latest_cpu = 0
        latest_memory = 0
        latest_disk = 0
        
        if self.metrics["system_resources"]["cpu_usage"]:
            latest_cpu = self.metrics["system_resources"]["cpu_usage"][-1]["value"]
        
        if self.metrics["system_resources"]["memory_usage"]:
            latest_memory = self.metrics["system_resources"]["memory_usage"][-1]["value"]
            
        if self.metrics["system_resources"]["disk_usage"]:
            latest_disk = self.metrics["system_resources"]["disk_usage"][-1]["value"]
        
        # Component health summary
        healthy_components = sum(1 for status in self.metrics["component_health"].values() if status == "healthy")
        total_components = len(self.metrics["component_health"])
        
        report = {
            "system_status": "healthy" if success_rate > 80 and healthy_components >= 3 else "warning",
            "uptime": str(uptime),
            "total_queries": total_queries,
            "success_rate": success_rate,
            "average_response_time": self.metrics["average_response_time"],
            "component_health": self.metrics["component_health"],
            "resource_usage": {
                "cpu_percent": latest_cpu,
                "memory_percent": latest_memory,
                "disk_percent": latest_disk
            },
            "recent_errors": len([e for e in self.metrics["error_log"] 
                                if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=1)])
        }
        
        return report
    
    def display_health_dashboard(self):
        """Display real-time health dashboard"""
        report = self.get_system_health_report()
        
        print("\n🔍 Farmer Assistant - System Health Dashboard")
        print("=" * 60)
        
        # System status
        status_icon = "🟢" if report["system_status"] == "healthy" else "🟡"
        print(f"{status_icon} System Status: {report['system_status'].upper()}")
        print(f"⏱️ Uptime: {report['uptime']}")
        
        # Performance metrics
        print(f"\n📊 Performance Metrics:")
        print(f"  💬 Total Queries: {report['total_queries']}")
        print(f"  ✅ Success Rate: {report['success_rate']:.1f}%")
        print(f"  ⚡ Avg Response Time: {report['average_response_time']:.2f}s")
        
        # Component health
        print(f"\n🔧 Component Health:")
        for component, status in report["component_health"].items():
            icon = "✅" if status == "healthy" else "❌" if status == "error" else "⚪"
            print(f"  {icon} {component.upper()}: {status}")
        
        # Resource usage
        print(f"\n💻 Resource Usage:")
        print(f"  🖥️ CPU: {report['resource_usage']['cpu_percent']:.1f}%")
        print(f"  🧠 Memory: {report['resource_usage']['memory_percent']:.1f}%")
        print(f"  💾 Disk: {report['resource_usage']['disk_percent']:.1f}%")
        
        # Recent errors
        if report["recent_errors"] > 0:
            print(f"\n⚠️ Recent Errors (last hour): {report['recent_errors']}")
        
        print("=" * 60)
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")
    
    def load_metrics(self):
        """Load metrics from file"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    saved_metrics = json.load(f)
                    # Merge with current metrics
                    self.metrics.update(saved_metrics)
                    self.logger.info("Metrics loaded from file")
        except Exception as e:
            self.logger.error(f"Failed to load metrics: {e}")
    
    def cleanup_old_logs(self, days=7):
        """Clean up old log entries"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Clean error log
        self.metrics["error_log"] = [
            error for error in self.metrics["error_log"]
            if datetime.fromisoformat(error["timestamp"]) > cutoff_date
        ]
        
        # Clean resource usage logs
        for resource in self.metrics["system_resources"]:
            self.metrics["system_resources"][resource] = [
                entry for entry in self.metrics["system_resources"][resource]
                if datetime.fromisoformat(entry["timestamp"]) > cutoff_date
            ]
        
        self.save_metrics()
        self.logger.info(f"Cleaned up logs older than {days} days")


# Global monitor instance
monitor = SystemMonitor()


def main():
    """Main monitoring function"""
    print("🔍 System Monitor - Real-time Dashboard")
    
    try:
        monitor.load_metrics()
        
        while True:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Update resource monitoring
            monitor.monitor_system_resources()
            
            # Display dashboard
            monitor.display_health_dashboard()
            
            print("\n💡 Press Ctrl+C to exit monitoring")
            
            # Wait 5 seconds
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")
    except Exception as e:
        print(f"❌ Monitoring error: {e}")


if __name__ == "__main__":
    main()
