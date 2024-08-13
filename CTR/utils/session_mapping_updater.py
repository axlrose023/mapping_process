from CTR.models import SessionMappingEarnings, SessionMappingDeductions, SessionMappingTaxes

class SessionMappingUpdater:
    @staticmethod
    def update_mappings(model, mappings, session_id):
        for mapping in mappings:
            extracted = mapping['extracted']
            mapped = mapping['mapped']

            # Get the first existing mapping if there are multiple
            existing_mapping = model.objects.filter(session_id=session_id, extracted_header=extracted).order_by('id').first()

            if existing_mapping:
                # Update the existing mapping
                existing_mapping.mapped_header = mapped
                existing_mapping.save()
            else:
                # Create a new mapping if none exists
                model.objects.create(
                    session_id=session_id, extracted_header=extracted, mapped_header=mapped
                )

    @classmethod
    def update_session_mappings(cls, session_id, earnings_mappings, deductions_mappings, taxes_mappings):
        cls.update_mappings(SessionMappingEarnings, earnings_mappings, session_id)
        cls.update_mappings(SessionMappingDeductions, deductions_mappings, session_id)
        cls.update_mappings(SessionMappingTaxes, taxes_mappings, session_id)
