"""
sandbox_main.py — Entry point for SandboxManus (LM Studio / Daytona)
=====================================================================
Launches the `SandboxManus` agent, which automatically selects the
appropriate execution backend:

  • **LM Studio (local)** — when `[llm] api_type = "lmstudio"` is set in
    config/config.toml and no `[daytona]` API key is present.
    Uses local tools (Python, browser, file editor) with LM Studio as
    the inference backend.

  • **Daytona (cloud)** — when `[daytona] daytona_api_key` is configured.
    Provisions a remote sandbox and uses the full sandbox toolset.

Quick start with LM Studio:
  1. Start LM Studio and load a model.
  2. Enable the local server (default: http://localhost:1234).
  3. Copy config/config.example-lmstudio.toml to config/config.toml.
  4. Run: python sandbox_main.py
"""

import argparse
import asyncio

from app.agent.sandbox_agent import SandboxManus
from app.config import config
from app.logger import logger


async def main():
    parser = argparse.ArgumentParser(
        description="Run SandboxManus agent (LM Studio or Daytona)"
    )
    parser.add_argument(
        "--prompt", type=str, required=False, help="Input prompt for the agent"
    )
    args = parser.parse_args()

    # Inform the user which backend is active
    lmstudio = config.lmstudio
    daytona = config.daytona
    if lmstudio and not (daytona and getattr(daytona, "daytona_api_key", None)):
        logger.info(
            f"[SandboxManus] LM Studio mode — endpoint: {lmstudio.base_url}"
        )
    elif daytona and getattr(daytona, "daytona_api_key", None):
        logger.info("[SandboxManus] Daytona mode — provisioning remote sandbox")
    else:
        logger.info("[SandboxManus] Local mode — using default LLM configuration")

    agent = await SandboxManus.create()
    try:
        prompt = args.prompt if args.prompt else input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")
        await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
