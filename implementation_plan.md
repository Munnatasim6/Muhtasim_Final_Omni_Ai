# Implementation Plan - Singularity Level Upgrade

## Goal Description
Upgrade "OmniTrade AI Core" to "Singularity Level" by integrating Self-Evolving AI, Generative Models, Hardware Acceleration, and Advanced Scrapers. This involves adding 7 new modules and updating the main entry point.

## User Review Required
> [!IMPORTANT]
> This upgrade introduces significant complexity, including dynamic code generation (LLM) and hardware interfacing (FPGA). Ensure the environment is isolated when testing generated strategies.

## Proposed Changes

### Core Intelligence Modules

#### [NEW] [strategy_generator.py](file:///d:/muhtasim_AI_Bot/core/meta_brain/strategy_generator.py)
- **Purpose**: LLM-based strategy generator that reads market conditions and outputs Python code.
- **Key Features**: `generate_strategy()`, `exec_sandbox()`.

#### [NEW] [evolution.py](file:///d:/muhtasim_AI_Bot/core/meta_brain/evolution.py)
- **Purpose**: Genetic Algorithm for hyperparameter tuning of RL agents.
- **Key Features**: `Population`, `crossover()`, `mutate()`, `evolve()`.

#### [NEW] [gan_market.py](file:///d:/muhtasim_AI_Bot/backend/brain/models/gan_market.py)
- **Purpose**: GAN for simulating market scenarios (e.g., crashes).
- **Key Features**: `Generator`, `Discriminator`, `train_gan()`.

### Market Analysis & Execution

#### [NEW] [macro_correlator.py](file:///d:/muhtasim_AI_Bot/core/macro_correlator.py)
- **Purpose**: Global macro-economic correlation engine using `yfinance`.
- **Key Features**: `fetch_macro_data()`, `calculate_correlations()`.

#### [NEW] [sor_router.py](file:///d:/muhtasim_AI_Bot/core/sor_router.py)
- **Purpose**: Smart Order Routing across multiple exchanges.
- **Key Features**: `route_order()`, `get_liquidity_depth()`.

#### [NEW] [whale_graph.py](file:///d:/muhtasim_AI_Bot/web3_modules/whale_graph.py)
- **Purpose**: Neo4j connector for whale wallet analysis.
- **Key Features**: `add_transaction()`, `find_clusters()`.

### Hardware & Data

#### [NEW] [fpga_bridge.py](file:///d:/muhtasim_AI_Bot/hardware/fpga_bridge.py)
- **Purpose**: Interface for FPGA hardware via serial/UDP.
- **Key Features**: `send_order_binary()`, `receive_confirmation()`.

#### [NEW] [twitter_advanced.py](file:///d:/muhtasim_AI_Bot/core/scrapers/twitter_advanced.py)
- **Purpose**: Advanced Twitter scraper using `twikit`.
- **Key Features**: `login()`, `search_latest()`, `rotate_user_agent()`.

### Integration

#### [MODIFY] [main.py](file:///d:/muhtasim_AI_Bot/main.py)
- **Changes**: Initialize `MacroCorrelator` and `EvolutionEngine`.

#### [NEW] [requirements_singularity.txt](file:///d:/muhtasim_AI_Bot/requirements_singularity.txt)
- **Content**: `yfinance`, `neo4j`, `twikit`, `pyserial`, `torch`.

## Verification Plan
### Automated Tests
- Run `python main.py` to verify all modules load without errors.
- Unit tests for each module (mocking external APIs and hardware).

### Manual Verification
- Check logs for successful initialization of new modules.
- Verify `requirements_singularity.txt` installation.
