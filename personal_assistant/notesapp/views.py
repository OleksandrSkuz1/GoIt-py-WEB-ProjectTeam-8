from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Note, Tag
from .forms import NoteForm, TagForm, NoteSearchForm
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .context_processors import get_language
from .translations import translations


@login_required
def note_list(request):
    """
    View function for displaying a list of notes associated with the logged-in user.

    Retrieves notes based on search queries and tag filters, handles pagination.

    Returns:
    HttpResponse: Rendered template with notes, tags, search form, and tag filter.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])
    query = request.GET.get('q')
    tag_query = request.GET.get('tag')
    search_form = NoteSearchForm(request.GET, language=language)

    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')

    notes = Note.objects.filter(user=request.user)  # Ensure we only get notes for the logged-in user
    notes = notes.order_by('created_at')

    selected_tag_name = 'All'

    if query:
        notes = Note.objects.filter(
            Q(user=request.user) &
            (Q(title__icontains=query) | Q(content__icontains=query))
        ).distinct()
    elif tag_query and tag_query != 'All':
        notes = Note.objects.filter(tags__name__icontains=tag_query, user=request.user).distinct()
        selected_tag_name = tag_query

    # Setting up pagination
    paginator = Paginator(notes, 10)
    page_number = request.GET.get('page')
    try:
        notes = paginator.page(page_number)
    except PageNotAnInteger:
        notes = paginator.page(1)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)

    return render(request, 'notesapp/note_list.html', {
        'notes': notes,
        'tags': Tag.objects.filter(user=request.user),
        'search_form': search_form,
        "query": query,
        'selected_tag_name': selected_tag_name,
        'translations': trans
    })


@login_required
def note_details(request, id):
    """
    View function for displaying details of a specific note.

    Retrieves and displays the note based on the provided ID.

    Args:
    id (int): The ID of the note to display
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])
    note = get_object_or_404(Note, pk=id, user=request.user)
    return render(request, 'notesapp/note_details.html', {"note": note, 'translations': trans})


@login_required
def tag_list(request):
    """
    View function for displaying a list of tags associated with the logged-in user.

    Retrieves and displays tags, handles pagination.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: Rendered template with tags and tag form.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])
    tags = Tag.objects.filter(user=request.user)
    tags = tags.order_by('id')

    # Setting up pagination
    paginator = Paginator(tags, 10)
    page_number = request.GET.get('page')
    try:
        tags = paginator.page(page_number)
    except PageNotAnInteger:
        tags = paginator.page(1)
    except EmptyPage:
        tags = paginator.page(paginator.num_pages)

    return render(request, 'notesapp/tag_list.html', {'tags': tags, 'translations': trans, 'tag_form': TagForm(user=request.user, language=language)})


@login_required
def add_note(request):
    """
    View function for adding a new note.

    Handles form submission for creating a new note.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: Redirects to the note list or re-renders the note form on validation failure.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])
    if request.method == "POST":
        form = NoteForm(request.POST, user=request.user, language=language)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            form.save_m2m()

            # Handling tags
            choice_tags = Tag.objects.filter(name__in=request.POST.getlist('tags'), user=request.user)
            for tag in choice_tags.iterator():
                note.tags.add(tag)

            return redirect('notesapp:note_list')
        else:
            tags = Tag.objects.filter(user=request.user).all()
            return render(request, 'notesapp/note_form.html', {"tags": tags, 'form': form, 'translations': trans})

    else:
        form = NoteForm(user=request.user, language=language, initial={'language': language})
        return render(request, 'notesapp/note_form.html', {'form': form, 'translations': trans})


@login_required
def add_tag(request):
    """
    View function for adding a new tag.

    Handles form submission for creating a new tag.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: Redirects to the tag list or re-renders the tag form on validation failure.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])
    if request.method == 'POST':
        form = TagForm(request.POST, user=request.user, language=language)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            return redirect(to='notesapp:tag_list')
        else:
            tags = Tag.objects.filter(user=request.user)
            return render(request, 'notesapp/tag_list.html', {'tags': tags, 'tag_form': form, 'translations': trans})

    return redirect('notesapp:tag_list')


@login_required
def edit_note(request, id):
    """
    View function for editing an existing note.

    Handles form submission for updating a note.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The ID of the note to edit.

    Returns:
    HttpResponse: Redirects to the note list or re-renders the note form on validation failure.
    """
    language = get_language(request)
    trans = translations.get(language, translations['en'])
    note = get_object_or_404(Note, id=id)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note, user=request.user)
        if form.is_valid():
            note = form.save()

            # Handling tags
            selected_tags = request.POST.getlist('tags')
            choice_tags = Tag.objects.filter(
                name__in=selected_tags, user=request.user
            )
            for tag in choice_tags:
                note.tags.add(tag)

            return redirect('notesapp:note_list')
    else:
        form = NoteForm(instance=note, user=request.user)
    return render(request, 'notesapp/note_form.html', {'form': form, 'translations': trans})


@login_required
def delete_note(request, id):
    """
    View function for deleting a note.

    Handles form submission for deleting a note.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The ID of the note to delete.

    Returns:
    HttpResponse: Redirects to the note list.
    """
    note = get_object_or_404(Note, id=id,  user=request.user)
    if request.method == "POST":
        note.delete()
        return redirect('notesapp:note_list')
    return redirect('notesapp:note_list')


@login_required
def delete_tag(request, id):
    """
    View function for deleting a tag.

    Handles form submission for deleting a tag.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The ID of the tag to delete.

    Returns:
    HttpResponse: Redirects to the tag list.
    """
    tag = get_object_or_404(Tag, id=id, user=request.user)
    if request.method == 'POST':
        tag.delete()
        return redirect('notesapp:tag_list')
    return redirect('notesapp:tag_list')
