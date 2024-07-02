from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Contact, Group
from .forms import ContactForm, GroupForm, ContactSearchForm
from .context_processors import get_language
from .localize import text_array


@method_decorator(login_required, name='dispatch')
class ContactCreateView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "contactsapp/contact_form.html"
    success_url = reverse_lazy("contactsapp:contact_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['language'] = get_language(self.request)
        return kwargs

    def form_valid(self, form):
        fields = form.save(commit=False)
        fields.creator = self.request.user  # Set the creator field
        fields.save()
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ContactUpdateView(UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = "contactsapp/contact_form.html"
    success_url = reverse_lazy("contactsapp:contact_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['language'] = get_language(self.request)
        return kwargs

    def get_queryset(self):
        return Contact.objects.filter(creator=self.request.user)


@method_decorator(login_required, name='dispatch')
class GroupCreateView(CreateView):
    model = Group
    form_class = GroupForm
    template_name = "contactsapp/group_form.html"
    success_url = reverse_lazy("contactsapp:group_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['language'] = get_language(self.request)
        return kwargs

    def form_valid(self, form):
        fields = form.save(commit=False)
        fields.creator = self.request.user
        fields.save()
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class GroupUpdateView(UpdateView):
    model = Group
    form_class = GroupForm
    template_name = "contactsapp/group_form.html"
    success_url = reverse_lazy("contactsapp:group_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['language'] = get_language(self.request)
        return kwargs

    def get_queryset(self):
        return Group.objects.filter(creator=self.request.user)


@login_required
def my_contacts(request):
    language = get_language(request)
    localization = text_array[language]
    curr_user = request.user.id

    query = request.GET.get('query', '')
    group_id = request.GET.get('group_id')

    # Create the search form with the current query
    search_form = ContactSearchForm(request.GET, language=language)

    # Filter contacts based on query and group_id
    selected_group_name = ''
    contacts = Contact.objects.filter(creator=curr_user)
    if group_id:
        contacts = contacts.filter(group_id=group_id)
        selected_group = Group.objects.get(id=group_id)
        selected_group_name = selected_group.name
        # Translate the group name
        if selected_group_name == 'Family':
            selected_group_name = localization['family_group']
        elif selected_group_name == 'Friends':
            selected_group_name = localization['friends_group']
        elif selected_group_name == 'Work':
            selected_group_name = localization['work_group']
    if query:
        contacts = contacts.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query)
        )

    contacts = contacts.order_by("-creation_time")
    groups = Group.objects.filter(creator=curr_user)

    # Setting up pagination
    paginator = Paginator(contacts, 10)
    page_number = request.GET.get('page')
    try:
        contacts = paginator.page(page_number)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    template = loader.get_template("contactsapp/contact_list.html")
    context = {
        "translations": localization,
        "contacts": contacts,
        "groups": groups,
        "search_form": search_form,
        "selected_group_name": selected_group_name,
        "query": query,
        "text": {
            'title': localization['addressbook'],
            'list': localization['contact_list'],
            'edit': localization['edit'],
            'delete': localization['delete'],
            'confirm_delete': localization['confirm_delete_contact'],
            'search': localization['search'],
            'reset': localization['reset'],
            'groups': localization['groups'],
        },
    }
    return HttpResponse(template.render(context=context, request=request))


@login_required
def contact_details(request, contact_id):
    localization = text_array[get_language(request)]
    contact = Contact.objects.get(pk=contact_id)
    template = loader.get_template("contactsapp/contact_details.html")
    creator = None
    if contact.creator == request.user:
        creator = True
    else:
        creator = False
    context = {
        "translations": localization,
        "contact": contact,
        "creator": creator,
        "text": {
            'name': localization['name'],
            'phone': localization['phone'],
            'email': localization['email'],
            'address': localization['address'],
            'birthday': localization['birthday'],
            'created_at': localization['created_at'],
            'updated_at': localization['updated_at'],
            'group': localization['group'],
            'edit': localization['edit'],
            'delete': localization['delete'],
            'confirm_delete': localization['confirm_delete_contact'],
            'not_found': localization['contact_not_found']
        },
    }
    return HttpResponse(template.render(context=context, request=request))


@login_required
def my_groups(request):
    language = get_language(request)
    localization = text_array[language]
    user_groups = Group.objects.filter(creator=request.user).order_by("-id")
    for group in user_groups:
        group.display_name = group.name

    template = loader.get_template("contactsapp/group_list.html")
    context = {
        "translations": localization,
        "groups": user_groups,
        "text": {
            'title': localization['my_groups'],
            'list': localization['group_list'],
            'list_empty': localization['group_list_empty'],
            'edit': localization['edit'],
            'delete': localization['delete'],
            'confirm_delete': localization['confirm_delete_group'],
            'add_group': localization['add_group'],
            'back_to_contacts': localization['back_to_contacts']
        },
    }
    return HttpResponse(template.render(context=context, request=request))


@login_required
def delete_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk, creator=request.user)
    if request.method == 'POST':
        contact.delete()
        return redirect('contactsapp:contact_list')
    return redirect('contactsapp:contact_list')


@login_required
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk, creator=request.user)
    if request.method == 'POST':
        group.delete()
        return redirect('contactsapp:group_list')
    return redirect('contactsapp:group_list')
