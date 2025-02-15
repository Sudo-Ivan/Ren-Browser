use log::{debug, info};
use sysinfo::{Pid, System};

#[cfg(feature = "memory-profiling")]
use memory_stats::memory_stats;

pub struct AppMonitor {
    sys: System,
    pid: Pid,
}

impl AppMonitor {
    pub fn new() -> Self {
        let sys = System::new();
        let pid = Pid::from(std::process::id() as usize);
        Self { sys, pid }
    }

    pub fn log_usage(&mut self) {
        self.sys.refresh_all();

        if let Some(process) = self.sys.process(self.pid) {
            let cpu_usage = process.cpu_usage();
            let memory_usage = process.memory() / 1024; // Convert to KB

            #[cfg(feature = "memory-profiling")]
            if let Some(usage) = memory_stats() {
                info!(
                    "Memory Profiling: Physical: {} KB, Virtual: {} KB",
                    usage.physical_mem / 1024,
                    usage.virtual_mem / 1024
                );
            }

            info!(
                "Performance: CPU: {:.1}%, Memory: {} KB",
                cpu_usage, memory_usage
            );

            debug!(
                "Detailed: Virtual Memory: {} KB",
                process.virtual_memory() / 1024
            );
        }
    }
}
