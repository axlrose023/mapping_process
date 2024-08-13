from django.urls import path, include
from rest_framework.routers import DefaultRouter

from CTR.views import (
    ClientViewSet,
    ClientCompaniesView,
    ProviderListAPIView,
    ProcessFileAPIView,
    UpdateMappingsView,
    SessionCodesView,
    CompanyFileTypes,
    CompanyFileLinks
)

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
    path('companies/', ClientCompaniesView.as_view(), name='all-companies'),
    path('clients/<int:client_id>/companies/', ClientCompaniesView.as_view(), name='client-companies'),
    path('providers/', ProviderListAPIView.as_view(), name='provider-list'),
    path('files/process/', ProcessFileAPIView.as_view(), name='process-files'),
    path('update-mappings/<int:session_id>/', UpdateMappingsView.as_view(), name='update-mappings'),
    path('sessioncodes/<int:session_id>/', SessionCodesView.as_view(), name='sessioncodes'),
    path('company-file-types/', CompanyFileTypes.as_view(), name='company-files'),
    path('company-file-links/', CompanyFileLinks.as_view(), name='company-links'),
]

app_name = 'ctr'
