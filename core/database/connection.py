from supabase import AsyncClient, create_async_client
from supabase.client import AsyncClientOptions

from core.utils.config import settings


class SupabaseConnection:
    def __init__(self, schema: str) -> None:
        self.client: AsyncClient = None
        self.schema: str = schema

    async def connect(self) -> AsyncClient:
        options = AsyncClientOptions(
            postgrest_client_timeout=10,
            storage_client_timeout=10,
            schema=self.schema,
        )

        client = self.client = await create_async_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_key,
            options=options,
        )

        return client
