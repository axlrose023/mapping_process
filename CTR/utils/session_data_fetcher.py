from typing import Dict, List
from CTR.models import (
    SessionMappingEarnings, SessionMappingDeductions, SessionMappingTaxes,
    SessionCodesEarnings, SessionCodesDeductions
)
from .tax_codes import TAX_CODES


class SessionDataFetcher:
    @staticmethod
    def get_mappings(session_id: int) -> Dict[str, List[Dict[str, str]]]:
        data = {
            "earnings_mappings": SessionDataFetcher._get_earnings_mappings(session_id),
            "earnings_available": SessionDataFetcher._get_earnings_available(SessionCodesEarnings, "E", session_id),
            "deductions_mappings": SessionDataFetcher._get_mappings(SessionMappingDeductions, session_id),
            "deductions_available": SessionDataFetcher._get_deductions_available(session_id),
            "taxes_mappings": SessionDataFetcher._get_mappings(SessionMappingTaxes, session_id),
            "taxes_available": SessionDataFetcher._get_static_tax_codes(),
        }
        return data

    @staticmethod
    def _get_earnings_mappings(session_id: int) -> List[Dict[str, str]]:
        earnings_mappings = SessionDataFetcher._get_mappings(SessionMappingEarnings, session_id)
        # Ensure uniqueness by using a dictionary and then converting it back to a list
        unique_mappings = {mapping['extracted']: mapping for mapping in earnings_mappings}
        return list(unique_mappings.values())

    @staticmethod
    def _get_mappings(model, session_id: int) -> List[Dict[str, str]]:
        mappings = model.objects.filter(session_id=session_id)
        unique_mappings = {}
        for mapping in mappings:
            unique_mappings[mapping.extracted_header] = {
                "extracted": mapping.extracted_header,
                "mapped": mapping.mapped_header or "",
                "confidence": "Mapped" if mapping.mapped_header else "unmapped"
            }
        return list(unique_mappings.values())

    @staticmethod
    def _get_earnings_available(model, prefix: str, session_id: int) -> List[str]:
        earnings_codes = set(code.code for code in model.objects.filter(session_id=session_id))
        available = []
        available.append("IGNORE")
        for code in earnings_codes:
            available.append(f"{prefix}_{code}_dollars")
            available.append(f"{prefix}_{code}_hours")
            available.append(f"#{prefix}_{code}_dollars")
            available.append(f"#{prefix}_{code}_hours")
        return available

    @staticmethod
    def _get_deductions_available(session_id: int) -> List[str]:
        deductions_codes = SessionCodesDeductions.objects.filter(session_id=session_id)
        available = []
        available.append("IGNORE")
        for code in deductions_codes:
            available.append(f"D_{code.code}")
            available.append(f"#D_{code.code}")
        return available

    @staticmethod
    def _get_static_tax_codes() -> List[str]:
        tax_codes = TAX_CODES.keys()
        available = []
        available.append("IGNORE")
        for code in tax_codes:
            available.append(f"T_{code}")
            available.append(f"#T_{code}")
        return available
