from django.urls import path
from . import views

app_name = "contactsapp"

urlpatterns = [
    path("contacts/", views.my_contacts, name="contact_list"),
    path("contact/add", views.ContactCreateView.as_view(), name="add_contact"),
    path("contact/<int:pk>/update", views.ContactUpdateView.as_view(), name="update_contact"),
    path("contact/<int:contact_id>/", views.contact_details, name="contact_details"),
    path("contact/<int:pk>/delete", views.delete_contact, name="delete_contact"),
    path("groups/", views.my_groups, name="group_list"),
    path("group/add/", views.GroupCreateView.as_view(), name="add_group"),
    path("group/<int:pk>/update", views.GroupUpdateView.as_view(), name="update_group"),
    path("group/<int:pk>/delete", views.delete_group, name="delete_group"),
    path('birthdays/', views.upcoming_birthdays, name='upcoming_birthdays'),
]
