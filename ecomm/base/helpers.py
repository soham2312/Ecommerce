from io import BytesIO
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.conf import settings
import uuid

def save_pdf(params:dict):
    template = get_template('pdfs/invoice.html')
    html = template.render(params)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    filename=uuid.uuid4()
    try:
        with open(str(settings.BASE_DIR)+f"/public/static/{filename}.pdf", 'wb') as output:
            pdf=pisa.pisaDocument(BytesIO(html.encode("UTF-8")), output)
    except Exception as e:  
        print(e)

    if pdf.err:
        return '',False
    return filename,True