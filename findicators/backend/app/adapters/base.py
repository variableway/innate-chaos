from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    @abstractmethod
    async def fetch_latest(self) -> list[dict]:
        """Fetch latest data points.

        Returns list of dicts with keys:
            asset, price, source, change_24h (optional), volume_24h (optional)
        """
        pass
