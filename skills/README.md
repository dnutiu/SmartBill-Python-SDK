# Agent Skills for `smartbill-sdk`

These are [pi](https://github.com/earendil-works/pi-coding-agent) skills
(`SKILL.md` files) that teach coding agents how to use this SDK. An agent
imports a skill to get concise, copy-pasteable usage guidance for a given
area of the API.

Install the SDK first (`pip install smartbill-sdk`), then use any skill:

| Skill                  | Covers                                                                 |
|------------------------|------------------------------------------------------------------------|
| `smartbill-invoices`   | Invoices & proformas/estimates: create, storno, cancel, restore, PDF, payment status |
| `smartbill-payments`   | Payments & fiscal receipts (`bon fiscal`): `POST /payment`, payment types, mixed cash/card, fiscal-printer text, delete |
| `smartbill-email`      | Emailing a document (`POST /document/send`): base64 subject/body, invoice/proforma |

## Importing into a pi agent

Copy any of these `SKILL.md` files into your agent's skills directory (or
symlink them), then reference the skill by its `name` in the front matter.
Each skill is self-contained and points back to the relevant source files,
models, and runnable `examples/` scripts in this repo for deeper detail.

## Layout

```
skills/
  smartbill-invoices/SKILL.md
  smartbill-payments/SKILL.md
  smartbill-email/SKILL.md
```

All skills assume the SDK is installed and that you have a SmartBill
`username` (login e-mail) and API `token` (SmartBill Cloud → **Contul Meu →
Integrari → API**).
