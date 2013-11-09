"""
Exporting views
"""


def as_filetype(data, filetype, *a, **kw):
    handler = {
        "csv": as_csv,
    }[filetype]
    return handler(data, *a, **kw)


def as_csv(data, sheet_name=None, filename="data"):
    """
    Exports the given 'data' as a CSV file.
    Data is a list of rows
    Rows are lists of cells
    Cells are tuples of either value or (value, params)
    Ignores its sheet_name parameter, as CSV doesn't support it.
    Also ignores any styling.
    """
    
    from django.http import HttpResponse
    httpresponse = HttpResponse(mimetype='text/csv')
    httpresponse['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename.encode("ascii", "replace")
    
    rowstrs = []
    # Cycle through the rows
    for row in data:
        rowstr = u""
        # And the cells
        for cell in row:
            if isinstance(cell, (tuple, list)):
                rowstr += unicode(cell[0]) + ","
            else:
                rowstr += unicode(cell) + ","
        rowstrs.append(rowstr[:-1])
    
    httpresponse.write("\n".join(rowstrs))
    
    return httpresponse
