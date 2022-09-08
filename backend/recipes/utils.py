from django.db.models import F, Sum
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from recipes.models import RecipeIngredients


def get_list_ingredients(user):
    ingredients = RecipeIngredients.objects.filter(
        recipe__shopping_recipe__user=user).values(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(amount=Sum('amount')).values_list(
        'ingredient__name', 'amount', 'ingredient__measurement_unit')
    return ingredients


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=shoppinglist'
    pdf_status = pisa.CreatePDF(html, dest=response)

    if pdf_status.err:
        return HttpResponse('Ошибка: <pre>' + html + '</pre>')

    return response
