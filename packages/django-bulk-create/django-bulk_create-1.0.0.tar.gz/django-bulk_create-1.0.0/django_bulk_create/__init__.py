
def bulk_create(obj_list,model2kwargs=None):
    model_list = list(set(map(lambda c:type(c),obj_list)))
    if not obj_list:
        return
    if not model2kwargs:
        model2kwargs = {}
    for model in sorted(model_list,key=lambda m:m._meta.db_table):
        _obj_list = list(filter(lambda c:isinstance(c,model),obj_list))
        db_table = model._meta.db_table.replace('"','')
        print('BULK_CREATE: %s %s' % (db_table,len(_obj_list)))
        # dict syntax: dict(Model={}) and {Model:{}}
        kwargs_list = [model2kwargs.get(k,None) for k in [model,model.__name__]]
        kwargs = next(filter(None,kwargs_list),None) or {}
        model.objects.bulk_create(_obj_list,**kwargs)
