from datetime import datetime, timezone

from core.database.connection import SupabaseConnection


class DatabaseQueries(SupabaseConnection):
    async def create_record(self, iin: str) -> None:
        await self.client.table("cases").insert({"iin": iin}).execute()

    async def select_record(self) -> dict:
        record = (
            await self.client.table("applications")
            .select("*")
            .eq("status_id", 0)
            .limit(1)
            .execute()
        )

        return record.data[0] if len(record.data) > 0 else {}

    async def update_record(
        self,
        *,
        iin: str,
        status_id: int,
    ) -> None:
        (
            await self.client.table("applications")
            .update(
                {
                    "status_id": status_id,
                    "send_at": str(datetime.now()) if status_id == 1 else None,
                }
            )
            .eq("iin", iin)
            .execute()
        )

    async def update_payment(
        self,
        *,
        iin: str,
        payment_code: str,
    ) -> None:
        (
            await self.client.table("applications")
            .update(
                {
                    "payment_code": payment_code,
                }
            )
            .eq("iin", iin)
            .execute()
        )

    async def update_notification_code(
        self, *, iin: str, notification_code: str
    ) -> None:
        (
            await self.client.table("applications")
            .update(
                {
                    "notification_code": notification_code,
                }
            )
            .eq("iin", iin)
            .execute()
        )

    async def get_total_today_cases(self) -> int:
        today_start = (
            datetime.now(timezone.utc)
            .replace(hour=0, minute=0, second=0, microsecond=0)
            .isoformat()
        )

        total = (
            await self.client.table("applications")
            .select("*")
            .gte("send_at", today_start)
            .execute()
        )
        return len(total.data)
