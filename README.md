# office-sud

Python automation library for filing court claims through Kazakhstan's judicial portal [office.sud.kz](https://office.sud.kz).

Automates the full end-to-end workflow: NCA Layer authentication, case type selection, form filling, payment setup, document upload, and electronic digital signature (EDS).

## Requirements

- Python 3.11+
- Windows OS (required for NCALayer desktop integration and `pywin32`/`pywinauto`)
- [NCALayer](https://pki.gov.kz/ncalayer/) installed (for EDS signing)
- Google Chrome or Chromium browser
- `.p12` digital signature key file
- Supabase project (for case data backend)

## Installation

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### Case Configuration

Each case type is described by a JSON config file in the `configs/` directory. Two case types are supported:

- `"type": "statement"` — civil statement (иск / заявление)
- `"type": "petition"` — petition (ходатайство)

**Example config (`configs/my_org.json`):**

```json
{
  "auth": {
    "creds": { "bin": "123456789012", "password": "secret" },
    "nca": { "nca_path": "nca_key/my_key.p12", "nca_password": "keypass" }
  },
  "select_options_page": {
    "case_type": "CIVIL",
    "instance": "FIRSTINSTANCE",
    "doc_type": "3"
  },
  "fill_info_page": {
    "cat_group": "2",
    "cat": "204",
    "statement_character": "2",
    "district": "14",
    "court": "291",
    "court_name": "Районный суд №2 Ауэзовского района города Алматы",
    "org_bin": "123456789012",
    "org_address": "г. Алматы, ул. Примерная 1",
    "org_requisites": "Расчетный счет KZ... БИК ..."
  },
  "upload_files_page": {
    "base_req": "Требование по договору № {credit_id} ...",
    "additional_req": "При неоднократном оповещении клиента ...",
    "file_list": [
      "Лицензия",
      "Приказ_о_назначении_директора",
      "Договор_о_предоставлении_микрокредита",
      "Исковое_Заявление"
    ]
  },
  "payment_page": { "kbk": "2", "is_online": false },
  "type": "statement",
  "db_scheme": "ccloan",
  "max_cases_per_day": 100,
  "result_dir_path": "Z:/Поданные"
}
```

## Usage

The intended way to use this library is to subclass `OfficeSudProcess` and implement the
abstract steps for your specific case type. Each `process_*` method corresponds to one
stage of the workflow and can be overridden or composed as needed.

### 1. Prepare a config

Load a JSON config file or build `SetupParams` directly:

```python
from office_sud_core import read_config

config = read_config("configs/my_org.json")
```

### 2. Subclass `OfficeSudProcess`

```python
import asyncio
from office_sud_core import OfficeSudProcess, read_config


class MyCaseProcess(OfficeSudProcess):
    """Automation for my organization's microcredit cases."""

    async def run(self, debtor_iin: str, debt_sum: str, state_duty: str) -> None:
        async with self.chrome:
            self.tab = await self.chrome.get_tab()

            await self.process_login()
            await self.process_select_options()
            await self.process_fill_info(debtor_iin=debtor_iin)
            await self.process_set_payment(
                debt_sum=debt_sum,
                state_duty_sum=state_duty,
                is_online=self.params.payment_page_params.is_online,
            )
            await self.process_upload_files(files=self._collect_files(debtor_iin))
            await self.process_signing()

    def _collect_files(self, debtor_iin: str) -> list[str]:
        base = f"cases/{debtor_iin}"
        return [f"{base}/{name}.pdf" for name in self.params.upload_files_page_params.file_list]


if __name__ == "__main__":
    config = read_config("configs/my_org.json")
    process = MyCaseProcess(config, headless_browser=False)
    asyncio.run(process.run("123456789012", debt_sum="50000", state_duty="2500"))
```

### Available methods to override or call

| Method | Stage | Notes |
|--------|-------|-------|
| `process_login(*, with_creds=False)` | 1 — Auth | Pass `with_creds=True` to use BIN + password instead of NCALayer |
| `process_select_options()` | 2 — Case type | Reads from `config.select_options_page_params` |
| `process_fill_info(debtor_iin, debtor_phone_number="")` | 3 — Form | Court, org, and participant details |
| `process_set_payment(debt_sum, state_duty_sum, payment=None, is_online=False)` | 4 — Payment | KBK and duty amount |
| `process_upload_files(files)` | 5 — Documents | List of absolute file paths |
| `process_signing()` | 6 — EDS | Signs and downloads the result |

## Project Structure

```
office_sud_core/
├── browser/
│   ├── office_sud.py        # OfficeSudProcess — main orchestrator
│   ├── pages/
│   │   ├── base.py          # OfficeSudBase — shared browser helpers
│   │   ├── login.py         # LoginPage
│   │   ├── select_options.py# SelectOptionsPage
│   │   ├── fill_info.py     # FillInfoPage
│   │   ├── payment.py       # PaymentPage
│   │   ├── upload_files.py  # UploadFilesPage
│   │   └── signing.py       # SigningPage
│   └── constants/
│       ├── selectors.py     # All CSS/XPath selectors
│       └── scripts.py       # JavaScript snippets
├── desktop/
│   └── nca_layer.py         # NCALayer Windows process manager
├── models/
│   ├── base.py              # Pydantic param models
│   ├── setup.py             # SetupParams (master config)
│   └── statement.py         # StatementFillInfoParams
├── utils/
│   ├── config.py            # read_config() — JSON loader
│   └── utils.py             # File/temp helpers
├── types.py                 # ParticipantType, ParticipantSide, Status
└── exceptions.py            # StatementError
configs/                     # JSON case configurations
nca_key/                     # .p12 digital signature keys (not committed)
```

## Workflow Steps

| Step | Method | Description |
|------|--------|-------------|
| 1 | `process_login()` | Authenticate via NCALayer EDS or credentials |
| 2 | `process_select_options()` | Select case type, instance, and document type |
| 3 | `process_fill_info()` | Fill court, organization, and participant details |
| 4 | `process_set_payment()` | Configure state duty and KBK code |
| 5 | `process_upload_files()` | Upload supporting documents |
| 6 | `process_signing()` | Sign with EDS and submit |

## Key Types

```python
from office_sud_core import ParticipantType, ParticipantSide, Status

ParticipantType.individual    # 1
ParticipantType.legal_entity  # 2

ParticipantSide.claimant      # 1
ParticipantSide.debtor        # 2
ParticipantSide.third_party   # 7
ParticipantSide.representative# 5

Status.DONE        # 1
Status.NOT_DONE    # 0
Status.CASE_BROKEN # -1
```

## Version

```python
import office_sud_core
print(office_sud_core.__version__)  # 1.0.0
```

## License

MIT
