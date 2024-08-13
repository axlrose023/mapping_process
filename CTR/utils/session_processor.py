import pandas as pd
import requests
from typing import List, Optional, Dict

from django.db import models

from CTR.models import (Session, SessionFileType, SessionMappingMemos, SessionMappingEarnings, SessionMappingDeductions,
                        SessionMappingTaxes, SessionCodesEarnings, SessionCodesMemos, SessionCodesDeductions)
from CTR.utils import SessionManager


class SessionProcessor:
    def process_uploaded_files(self, files, provider: str, session_id: int) -> dict:
        response = self.send_files_to_endpoint(files, provider)
        if response.status_code == 200:
            try:
                json_data = response.json()

                # Extract headers directly from JSON data
                headers = self.extract_headers_from_json(json_data['data'])
                return {"headers": headers, "payroll_data": json_data['data']}
            except ValueError as e:
                raise ValueError(f"Failed to decode JSON response: {e}")
        else:
            print(f"Failed to process files: {response.status_code} {response.text}")
            response.raise_for_status()

    def send_files_to_endpoint(self, files, provider: str) -> requests.Response:
        url = 'http://ctrpowerautomatedev.eastus.azurecontainer.io:5001/extract'
        files_data = [('file', (file.name, file, file.content_type)) for file in files]
        data = {"provider": "Paycom"}
        response = requests.post(url, files=files_data, data=data)
        response.raise_for_status()
        return response

    def extract_headers_from_json(self, json_data: List[dict]) -> List[str]:
        # Extract headers from the first item in the JSON data (assuming all items have the same structure)
        if json_data:
            return list(json_data[0].keys())
        return []

    def _process_header(self, session: Session, header: str) -> Optional[models.Model]:
        if "payments" in header.lower():
            return SessionMappingEarnings(session=session, extracted_header=header, mapped_header="")
        elif "memos" in header.lower():
            return SessionMappingMemos(session=session, extracted_header=header, mapped_header="")
        elif "deductions" in header.lower():
            return SessionMappingDeductions(session=session, extracted_header=header, mapped_header="")
        elif "taxes" in header.lower():
            return SessionMappingTaxes(session=session, extracted_header=header, mapped_header="")
        return None

    def populate_extracted_headers(self, session_id: int, headers: List[str], file_type: str, company) -> None:
        session = SessionManager.get_session(session_id)

        # Ensure SessionFileType exists
        self._ensure_file_type(session, file_type)

        # Get or create mappings for each header
        current_mappings = self._get_or_create_mappings(session, headers, company)

        # Create new mappings or apply found mappings
        new_mappings = self._build_new_mappings(session, current_mappings)

        # Bulk create new mappings
        self._bulk_create_mappings(new_mappings)

    def _ensure_file_type(self, session: Session, file_type: str) -> None:
        """Ensure the SessionFileType exists for the session."""
        SessionFileType.objects.get_or_create(session=session, file_type=file_type)

    def _get_or_create_mappings(self, session: Session, headers: List[str], company) -> Dict[
        str, Optional[models.Model]]:
        """Retrieve or create mappings for headers based on the current session or other sessions."""
        current_mappings = {
            header: self._get_existing_mapping(session, header) for header in headers
        }

        # If no mappings are found, check other sessions of the same client
        if not any(current_mappings.values()):
            other_sessions = Session.objects.filter(company__client=company.client).exclude(id=session.id)
            for other_session in other_sessions:
                for header in headers:
                    if not current_mappings[header]:
                        current_mappings[header] = self._get_existing_mapping(other_session, header)

        return current_mappings

    def _build_new_mappings(self, session: Session, current_mappings: Dict[str, Optional[models.Model]]) -> List[
        models.Model]:
        """Build a list of new mappings based on existing or newly created mappings."""
        new_mappings = []
        for header, mapping in current_mappings.items():
            if mapping:  # If a mapping was found
                new_mappings.append(self._create_mapping_instance(session, header, mapping))
            else:  # If no mapping was found, create a new one
                new_mapping = self._process_header(session, header)
                if new_mapping:
                    new_mappings.append(new_mapping)
        return new_mappings

    def _create_mapping_instance(self, session: Session, header: str, mapping: models.Model) -> models.Model:
        """Create a mapping instance based on the type of mapping found."""
        if isinstance(mapping, SessionMappingEarnings):
            return SessionMappingEarnings(session=session, extracted_header=header, mapped_header=mapping.mapped_header)
        elif isinstance(mapping, SessionMappingMemos):
            return SessionMappingMemos(session=session, extracted_header=header, mapped_header=mapping.mapped_header)
        elif isinstance(mapping, SessionMappingDeductions):
            return SessionMappingDeductions(session=session, extracted_header=header,
                                            mapped_header=mapping.mapped_header)
        elif isinstance(mapping, SessionMappingTaxes):
            return SessionMappingTaxes(session=session, extracted_header=header, mapped_header=mapping.mapped_header)
        return None

    def _bulk_create_mappings(self, new_mappings: List[models.Model]) -> None:
        """Bulk create all new mappings."""
        SessionMappingEarnings.objects.bulk_create([m for m in new_mappings if isinstance(m, SessionMappingEarnings)])
        SessionMappingMemos.objects.bulk_create([m for m in new_mappings if isinstance(m, SessionMappingMemos)])
        SessionMappingDeductions.objects.bulk_create(
            [m for m in new_mappings if isinstance(m, SessionMappingDeductions)])
        SessionMappingTaxes.objects.bulk_create([m for m in new_mappings if isinstance(m, SessionMappingTaxes)])

    def _get_existing_mapping(self, session: Session, header: str) -> Optional[models.Model]:
        """
        Check for an existing mapping for a given header in a specific session.
        Returns the latest match or None if no matches are found.
        """
        mapping = SessionMappingEarnings.objects.filter(session=session, extracted_header=header).order_by(
            '-id').first()
        if mapping:
            return mapping
        mapping = SessionMappingMemos.objects.filter(session=session, extracted_header=header).order_by('-id').first()
        if mapping:
            return mapping
        mapping = SessionMappingDeductions.objects.filter(session=session, extracted_header=header).order_by(
            '-id').first()
        if mapping:
            return mapping
        mapping = SessionMappingTaxes.objects.filter(session=session, extracted_header=header).order_by('-id').first()
        if mapping:
            return mapping
        return None

    def populate_session_codes(self, session_id, mapping_files):
        session = Session.objects.get(id=session_id)

        for file in mapping_files:
            if 'Deductions' in file.name:
                self._create_session_codes(file, session, 'Deduction', SessionCodesDeductions)
            elif 'Memos' in file.name:
                self._create_session_codes(file, session, 'Memo', SessionCodesMemos)
            elif 'Earnings' in file.name:
                self._create_session_codes(file, session, 'Earning', SessionCodesEarnings)

    def _create_session_codes(self, file, session, title, model_class):
        data = self._extract_title_code(file, title=title)
        seen_codes = set()
        for d in data:
            if d["Code"] not in seen_codes:
                model_class.objects.create(
                    session=session,
                    title=d[f"{title} Title"],
                    code=d["Code"]
                )
                seen_codes.add(d["Code"])

    def _extract_title_code(self, file_path, title):
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names

        # Initialize an empty list to store all data
        codes_list = []

        # Loop through each sheet and extract the required columns
        for sheet_name in sheet_names:
            sheet = pd.read_excel(xls, sheet_name=sheet_name)
            # Extract the relevant columns from the sheet
            df = sheet.iloc[2:, [1, 2]].dropna().reset_index(drop=True)
            df.columns = [f"{title} Title", "Code"]
            # Append the data to the list
            codes_list.extend(df.to_dict('records'))

        seen = set()
        distinct_data = []
        for item in codes_list:
            if item["Code"] not in seen:
                distinct_data.append(item)
                seen.add(item["Code"])

        return distinct_data

    def _header_exists(self, session: Session, header: str) -> bool:
        return (SessionMappingEarnings.objects.filter(session=session, extracted_header=header).exists() or
                SessionMappingMemos.objects.filter(session=session, extracted_header=header).exists() or
                SessionMappingDeductions.objects.filter(session=session, extracted_header=header).exists() or
                SessionMappingTaxes.objects.filter(session=session, extracted_header=header).exists())
