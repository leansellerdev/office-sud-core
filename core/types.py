from dataclasses import dataclass


@dataclass
class ParticipantType:
    individual = 1
    legal_entity = 2


@dataclass
class ParticipantSide:
    claimant = 1
    debtor = 2
    third_party = 7
    applicant = 4
    representative = 5

    sides = [claimant, debtor, third_party, applicant, representative]


@dataclass
class Status:
    DONE = 1
    CASE_BROKEN = -1
    NOT_DONE = 0


class Dialog:
    text: str
    value: bool
