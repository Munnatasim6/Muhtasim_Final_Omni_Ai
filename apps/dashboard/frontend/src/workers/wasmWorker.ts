// Web Worker for running heavy WASM simulations off the main thread.

import init, { run_heavy_sim } from "../../../rust_core/pkg/rust_core";

self.onmessage = async (e: MessageEvent) => {
    const { type, data } = e.data;

    if (type === "RUN_SIMULATION") {
        try {
            // Initialize WASM module
            await init();

            // Run the heavy simulation
            const result = run_heavy_sim(JSON.stringify(data));

            // Send result back to main thread
            self.postMessage({ type: "SIMULATION_COMPLETE", result });
        } catch (error) {
            self.postMessage({ type: "SIMULATION_ERROR", error: String(error) });
        }
    }
};
