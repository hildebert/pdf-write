from collections import OrderedDict
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject, NumberObject


def set_need_appearances_writer(writer):
    try:
        catalog = writer._root_object
        # get the AcroForm tree
        if "/AcroForm" not in catalog:
            writer._root_object.update({
                NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
        return writer

    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))
        return writer


def _getFields(obj, tree=None, retval=None, fileobj=None):
    fieldAttributes = {'/FT': 'Field Type', '/Parent': 'Parent', '/T': 'Field Name', '/TU': 'Alternate Field Name',
                       '/TM': 'Mapping Name', '/Ff': 'Field Flags', '/V': 'Value', '/DV': 'Default Value'}
    if retval is None:
        retval = OrderedDict()
        catalog = obj.trailer["/Root"]
        # get the AcroForm tree
        if "/AcroForm" in catalog:
            tree = catalog["/AcroForm"]
        else:
            return None
    if tree is None:
        return retval

    obj._checkKids(tree, retval, fileobj)
    for attr in fieldAttributes:
        if attr in tree:
            # Tree is a field
            obj._buildField(tree, retval, fileobj, fieldAttributes)
            break

    if "/Fields" in tree:
        fields = tree["/Fields"]
        for f in fields:
            field = f.getObject()
            obj._buildField(field, retval, fileobj, fieldAttributes)

    return retval


def get_form_fields(infile):
    infile = PdfFileReader(open(infile, 'rb'))
    fields = _getFields(infile)
    return OrderedDict((k, v.get('/V', '')) for k, v in fields.items())


def update_form_values(infile, outfile, newvals=None):
    pdf = PdfFileReader(open(infile, 'rb'))
    writer = PdfFileWriter()
    set_need_appearances_writer(writer)

    if "/AcroForm" in writer._root_object:
        writer._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})

    # print(pdf)

    # if '/AcroForm' in pdf._root_object:
    #     pdf._root_object["/AcroForm"].update(
    #         {NameObject("/NeedAppearances"): BooleanObject(True)}
    #     )

    for i in range(pdf.getNumPages()):
        page = pdf.getPage(i)

        if not newvals:
            newvals = {k: f'#{i} {k}={v}' for i, (k, v) in enumerate(get_form_fields(infile).items())}

        try:
            writer.updatePageFormFieldValues(page, newvals)

            for j in range(0, len(page['/Annots'])):
                writer_annot = page['/Annots'][j].getObject()
                for field in newvals:
                    # -----------------------------------------------------BOOYAH!
                    if writer_annot.get('/T') == field:
                        writer_annot.update({
                            NameObject("/Ff"): NumberObject(1)
                        })
                        # -----------------------------------------------------

            writer.addPage(page)
        except Exception as e:
            print(repr(e))
            writer.addPage(page)

    with open(outfile, 'wb') as out:
        writer.write(out)


if __name__ == '__main__':
    from pprint import pprint

    pdf_file_name = 'template.pdf'

    # pprint(get_form_fields(pdf_file_name))

    update_form_values(pdf_file_name, 'out-' + pdf_file_name)  # enumerate & fill the fields with their own names
    update_form_values(pdf_file_name, 'out2-' + pdf_file_name,
                       {u'Текстовое поле 1014': 'My Value',
                        u'Текстовое поле 1015': 'My Another 💎alue'})  # u
