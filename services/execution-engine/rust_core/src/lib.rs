use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;

// শুধুমাত্র যখন 'python-backend' ফিচার অন থাকবে, তখন pyo3 ব্যবহার হবে
#[cfg(feature = "python-backend")]
use pyo3::prelude::*;

#[derive(Serialize, Deserialize, Debug)]
struct Order {
    id: String,
    price: f64,
    amount: f64,
    side: String,
}

// --- Python Section (Backend Only) ---
// এই অংশ শুধু Python এর জন্য কম্পাইল হবে

#[cfg(feature = "python-backend")]
#[pyfunction]
fn is_safe_entry(current_price: f64, spread: f64, volatility: f64, max_spread: f64, max_volatility: f64) -> bool {
    if spread > max_spread {
        return false;
    }
    if volatility > max_volatility {
        return false;
    }
    true
}

#[cfg(feature = "python-backend")]
#[pyfunction]
fn validate_order(price: f64, amount: f64, min_amount: f64, max_amount: f64, balance: f64) -> (bool, String) {
    if amount < min_amount {
        return (false, "Amount below minimum limit".to_string());
    }
    if amount > max_amount {
        return (false, "Amount exceeds maximum limit".to_string());
    }
    if price <= 0.0 {
        return (false, "Price must be positive".to_string());
    }
    if amount * price > balance {
        return (false, "Insufficient balance".to_string());
    }
    (true, "Valid".to_string())
}

#[cfg(feature = "python-backend")]
#[pymodule]
fn rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(is_safe_entry, m)?)?;
    m.add_function(wrap_pyfunction!(validate_order, m)?)?;
    Ok(())
}

// --- WebAssembly (Edge AI) Section (Frontend Only) ---
// এই অংশ শুধু ব্রাউজারের জন্য

#[wasm_bindgen]
pub fn run_heavy_sim(data: &str) -> String {
    // Simulate a heavy Monte Carlo simulation
    let iterations = 1_000_000;
    let mut score = 0.0;
    
    // Simple CPU burn loop to simulate "work"
    for i in 0..iterations {
        score += (i as f64).sqrt().sin();
    }
    
    format!("Simulation Complete. Processed {} iterations. Score: {:.4}. Data received: {}", iterations, score, data)
}
