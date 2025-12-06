use std::thread;
use std::time::Duration;

fn main() {
    println!("Execution Engine (rust_core) Service Started.");
    println!("Running in loop to keep container alive...");
    
    // Infinite loop to keep the service running
    loop {
        thread::sleep(Duration::from_secs(60));
        println!("Heartbeat: Execution Engine is alive.");
    }
}
