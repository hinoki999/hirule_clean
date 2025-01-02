import asyncio
from src.agents.coordinator import MasterCoordinator

async def main():
    try:
        coordinator = MasterCoordinator(openai_api_key="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")
        await coordinator.setup()
        print("Setup completed successfully.")
    except Exception as e:
        print(f"Error during setup: {e}")

if __name__ == "__main__":
    asyncio.run(main())


