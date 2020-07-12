import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.template import loader
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import ProductDb, UserPersonalDb
from comments.models import CommentsDb
from comments.forms import CommentsForm, DivErrorList


def autocompleteModel(request):
    """ Autocompletion in searchBar """
    if request.is_ajax():
        q = request.GET.get('term', '')
        search_qs = ProductDb.objects.filter(name__istartswith=q).order_by('name')[:20]
        results = []
        for p in search_qs:
            results.append(p.name)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def index(request):
    """ Rendering home page """
    template = loader.get_template('products/index.html')
    return HttpResponse(template.render(request=request))


def results(request):
    """ Rendering the substitutes' search results """
    page_number = 1
    query = ''

    if request.method == 'GET':
        query = request.GET.get('query', '')
        page_number = request.GET.get('page', 1)

    """elif request.method == 'POST':
        query = request.POST.get('query', '')"""

    if query == '':
        messages.error(request, 'Vous n\'avez saisi aucun produit', extra_tags='toaster')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    elif len(query) > 2:
        try:
            product = ProductDb.objects.filter(name__icontains=query).order_by('name').first()
            substitutes_list = ProductDb.objects.filter(category=product.category, nutriscore__lt=product.nutriscore)\
                .order_by('nutriscore').distinct()
            user_substitutes = []
            if request.user.is_authenticated:
                user_substitutes = UserPersonalDb.objects.filter(user=request.user).values_list('replaced_product__id',
                                                                                                flat=True)

            paginator = Paginator(substitutes_list, 6)

            try:
                substitutes = paginator.page(page_number)
            except EmptyPage:
                substitutes = paginator.page(paginator.num_pages)
            context = {
                'product': product,
                'substitutes': substitutes,
                'paginate': True,
                'query': query,
                'user_substitutions': user_substitutes,
                'page_number': page_number,
            }
            return render(request, 'products/results.html', context)
        except AttributeError:
            messages.error(request, 'Produit inconnu, faites une autre recherche', extra_tags='toaster')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, 'Produit inconnu, faites une autre recherche', extra_tags='toaster')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@require_http_methods(['POST'])
def save_in_db(request):
    """ Saving product in user personal db with AJAX """
    if request.is_ajax():
        body = json.loads(request.body)
    else:
        body = request.POST
    """try:
        body = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        body = request.body
        print(body)"""
    product_id = body['product_id']
    substitute_id = body['substitute_id']

    original_product = ProductDb.objects.get(pk=product_id)
    replaced_product = ProductDb.objects.get(pk=substitute_id)

    try:
        UserPersonalDb.objects.get(original_product=original_product, replaced_product=replaced_product,
                                   user=request.user)
        data = {
            'is_in_db': True
        }
    except ObjectDoesNotExist:
        UserPersonalDb.objects.create(original_product=original_product, replaced_product=replaced_product,
                                      user=request.user)
        data = {
            'is_created': True
        }

    return JsonResponse(data)


def my_substitutes(request):
    """ Rendering the user personal db """
    if not request.user.is_authenticated:
        messages.error(request, 'Vous devez vous connecter pour accéder à votre espace', extra_tags='toaster')
        return HttpResponseRedirect(reverse('login'))

    substitutes_list = UserPersonalDb.objects.filter(user=request.user)

    paginator = Paginator(substitutes_list, 6)
    page_number = request.GET.get('page')

    try:
        substitutes = paginator.page(page_number)
    except PageNotAnInteger:
        substitutes = paginator.page(1)
    except EmptyPage:
        substitutes = paginator.page(paginator.num_pages)
    context = {
            'substitutes': substitutes,
            'paginate': True,
    }
    return render(request, 'products/my_substitutes.html', context)


def detail(request, product_id):
    product = get_object_or_404(ProductDb, pk=product_id)
    approved_comments = product.comments.filter(approved_comment=True)

    context = {
        'product_id': product.id,
        'product_title_page': product.name,
        'product_image': product.image,
        'product_nutriscore': product.nutriscore,
        'product_fat': product.fat,
        'product_saturated_fat': product.saturated_fat,
        'product_sugar': product.sugar,
        'product_salt': product.salt,
        'product_url': product.url,
        'approved_comments': approved_comments
    }

    return render(request, 'products/product.html', context)


def add_comment(request, product_id):
    product = get_object_or_404(ProductDb, pk=product_id)
    new_comment = None

    if request.method == 'POST':
        form = CommentsForm(request.POST, error_class=DivErrorList)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.product = product
            new_comment.user = request.user
            new_comment.save()
            return redirect('product', pk=product.pk)
    else:
        form = CommentsForm()

    return render(request, 'products/product.html', {'product': product,
                                                     'new_comment': new_comment,
                                                     'form': form})


"""def detail(request, product_id):
   
    product = ProductDb.objects.get(pk=product_id)
    existing_comments = product.comments.filter(approved_comment=True)

    context = {
        'product_id': product.id,
        'product_title_page': product.name,
        'product_image': product.image,
        'product_nutriscore': product.nutriscore,
        'product_url': product.url,
        'existing_comments': existing_comments,
        #'new_comment': new_comment,
        #'form': form,
    }
    return render(request, 'products/product.html', context)


@login_required
def add_comment(request, comment_id):
    product = ProductDb.objects.get(pk=comment_id)
    #new_comment = None

    if request.method == 'POST':
        form = CommentsForm(request.POST, error_class=DivErrorList)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.product = product
            new_comment.user = request.user
            new_comment.save()
            return redirect('product', pk=product.pk)
    else:
        form = CommentsForm()
    
    return render(request, 'comments/add_comment.html', {'form': form, 'product': product})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(CommentsDb, pk=pk)
    comment.approve()
    return redirect('product', pk=comment.product.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(CommentsDb, pk=pk)
    comment.remove()
    return redirect('product', pk=comment.product.pk)"""


def legal_notice(request):
    """ Rendering the legal notice """
    return render(request, 'products/legal_notice.html')


""" Saving product in db with Django
@login_required
def save_in_db(request, substitute_id, product_id, query, page_number):

    substitute = ProductDb.objects.get(pk=substitute_id)
    product = ProductDb.objects.get(pk=product_id)
    try:
        UserPersonalDb.objects.get(original_product=product, replaced_product=substitute, user=request.user)
        messages.warning(request, 'Ce produit est déjà dans votre espace personnel')
        return HttpResponseRedirect(reverse('results') + '?query=' + query + '&page=' + page_number)
    except ObjectDoesNotExist:
        UserPersonalDb.objects.create(original_product=product, replaced_product=substitute, user=request.user)
        messages.success(request, 'Le produit a été enregistré dans votre espace personnel')
        return HttpResponseRedirect(reverse('results') + '?query=' + query + '&page=' + page_number)"""
