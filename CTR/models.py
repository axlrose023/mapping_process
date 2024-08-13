from django.db import models


class Provider(models.Model):
    provider_name = models.CharField(max_length=255)

    def __str__(self):
        return self.provider_name


class Session(models.Model):
    is_closed = models.BooleanField(default=False)


class SessionFileType(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    file_type = models.CharField(max_length=200)

    def __str__(self):
        return self.file_type


class Client(models.Model):
    client_name = models.CharField(max_length=50)

    def __str__(self):
        return self.client_name


class Company(models.Model):
    company_name = models.CharField(max_length=50)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.CASCADE, related_name='companies')

    def __str__(self):
        return self.company_name


class SessionMappingEarnings(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    extracted_header = models.CharField(max_length=300)
    mapped_header = models.CharField(max_length=300)


class SessionMappingMemos(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    extracted_header = models.CharField(max_length=300)
    mapped_header = models.CharField(max_length=300)


class SessionMappingDeductions(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    extracted_header = models.CharField(max_length=300)
    mapped_header = models.CharField(max_length=300)


class SessionMappingTaxes(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    extracted_header = models.CharField(max_length=300)
    mapped_header = models.CharField(max_length=300)


class SessionCodesEarnings(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)


class SessionCodesMemos(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)


class SessionCodesDeductions(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255)


class SessionFileLink(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    file_type = models.CharField(max_length=255)
    file_link = models.URLField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File link for session {self.session.id} ({self.file_type})"
